# -*- coding: utf-8 -*-
"""
نظام إدارة الأداء والتخزين المؤقت
Performance Management and Caching System
"""

import os
import json
import time
import hashlib
import asyncio
import threading
import logging
from typing import Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import config

logger = logging.getLogger(__name__)

class CacheManager:
    """
    مدير التخزين المؤقت لتحسين الأداء
    Cache Manager for Performance Optimization
    """
    
    def __init__(self, cache_dir: str = None):
        self.cache_dir = cache_dir or os.path.join(config.TEMP_FOLDER, 'cache')
        self.memory_cache = {}
        self.cache_index = {}
        self.max_size = 100  # Maximum number of items in memory cache
        
        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load cache index
        self.load_cache_index()
    
    def _generate_key(self, data: Any) -> str:
        """Generate cache key from data"""
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        return hashlib.md5(str(data).encode()).hexdigest()
    
    def load_cache_index(self):
        """Load cache index from file"""
        try:
            index_path = os.path.join(self.cache_dir, 'index.json')
            if os.path.exists(index_path):
                with open(index_path, 'r', encoding='utf-8') as f:
                    self.cache_index = json.load(f)
        except Exception as e:
            logger.error(f"Error loading cache index: {e}")
            self.cache_index = {}
    
    def save_cache_index(self):
        """Save cache index to file"""
        try:
            index_path = os.path.join(self.cache_dir, 'index.json')
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache_index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache index: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        try:
            # Check memory cache first
            if key in self.memory_cache:
                return self.memory_cache[key]
            
            # Check file cache
            if key in self.cache_index:
                cache_info = self.cache_index[key]
                
                # Check if cache is expired
                if self._is_expired(cache_info):
                    self.delete(key)
                    return None
                
                file_path = cache_info['file_path']
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        data = f.read()
                    
                    # Add to memory cache
                    if len(self.memory_cache) < self.max_size:
                        self.memory_cache[key] = data
                    
                    return data
            
            return None
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None
    
    def set(self, key: str, data: Any, ttl_seconds: int = None) -> bool:
        """Set item in cache"""
        try:
            ttl_seconds = ttl_seconds or config.AI_VIDEO_SETTINGS.get('cache_duration', 3600)
            
            # Add to memory cache
            if len(self.memory_cache) < self.max_size:
                self.memory_cache[key] = data
            
            # Save to file cache
            file_path = os.path.join(self.cache_dir, f"{key}.cache")
            
            if isinstance(data, str):
                data = data.encode('utf-8')
            elif not isinstance(data, bytes):
                data = str(data).encode('utf-8')
            
            with open(file_path, 'wb') as f:
                f.write(data)
            
            # Update cache index
            self.cache_index[key] = {
                'file_path': file_path,
                'created_at': time.time(),
                'expires_at': time.time() + ttl_seconds,
                'size': len(data)
            }
            
            self.save_cache_index()
            return True
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    def _is_expired(self, cache_info: Dict) -> bool:
        """Check if cache item is expired"""
        return time.time() > cache_info.get('expires_at', 0)
    
    def delete(self, key: str) -> bool:
        """Delete item from cache"""
        try:
            # Remove from memory
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            # Remove from file cache
            if key in self.cache_index:
                cache_info = self.cache_index[key]
                file_path = cache_info['file_path']
                if os.path.exists(file_path):
                    os.remove(file_path)
                del self.cache_index[key]
                self.save_cache_index()
            
            return True
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    def clear(self):
        """Clear all cache"""
        try:
            self.memory_cache.clear()
            for cache_info in self.cache_index.values():
                file_path = cache_info['file_path']
                if os.path.exists(file_path):
                    os.remove(file_path)
            self.cache_index.clear()
            self.save_cache_index()
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    def cleanup_expired(self):
        """Clean up expired cache items"""
        try:
            expired_keys = []
            for key, cache_info in self.cache_index.items():
                if self._is_expired(cache_info):
                    expired_keys.append(key)
            
            for key in expired_keys:
                self.delete(key)
            
            logger.info(f"Cleaned up {len(expired_keys)} expired cache items")
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")


class AsyncVideoGenerator:
    """
    مولد الفيديو غير المتزامن لتحسين الأداء
    Async Video Generator for Performance Optimization
    """
    
    def __init__(self):
        self.cache = CacheManager()
        self.active_jobs = {}
        self.job_progress = {}
        self.executor = ThreadPoolExecutor(
            max_workers=config.AI_VIDEO_SETTINGS.get('max_parallel_jobs', 3)
        )
    
    async def generate_video_async(self, hadith_data: Dict, options: Dict = None) -> Dict:
        """
        Generate video asynchronously with progress tracking
        """
        job_id = self._generate_job_id()
        self.job_progress[job_id] = {
            'status': 'initializing',
            'progress': 0,
            'message': 'بدء توليد الفيديو...',
            'start_time': time.time()
        }
        
        try:
            # Check cache first
            cache_key = self.cache._generate_key(hadith_data)
            cached_result = self.cache.get(cache_key)
            
            if cached_result and config.AI_VIDEO_SETTINGS.get('cache_enabled', True):
                logger.info("استخدام فيديو محفوظ مؤقتاً")
                return {
                    'success': True,
                    'job_id': job_id,
                    'video_path': cached_result.decode('utf-8') if isinstance(cached_result, bytes) else cached_result,
                    'cached': True
                }
            
            # Start async generation
            future = self.executor.submit(self._generate_video_sync, hadith_data, job_id, options)
            self.active_jobs[job_id] = future
            
            return {
                'success': True,
                'job_id': job_id,
                'status': 'processing',
                'message': 'تم بدء توليد الفيديو بنجاح'
            }
        
        except Exception as e:
            logger.error(f"Error starting async video generation: {e}")
            self.job_progress[job_id] = {
                'status': 'failed',
                'progress': 0,
                'message': f'فشل في بدء توليد الفيديو: {str(e)}',
                'error': str(e)
            }
            return {'success': False, 'error': str(e)}
    
    def _generate_job_id(self) -> str:
        """Generate unique job ID"""
        return f"job_{int(time.time())}_{os.getpid()}"
    
    def _update_progress(self, job_id: str, progress: int, message: str = None, status: str = None):
        """Update job progress"""
        if job_id in self.job_progress:
            self.job_progress[job_id].update({
                'progress': progress,
                'message': message or self.job_progress[job_id].get('message', ''),
                'status': status or self.job_progress[job_id].get('status', 'processing'),
                'updated_at': time.time()
            })
    
    def _generate_video_sync(self, hadith_data: Dict, job_id: str, options: Dict = None) -> str:
        """
        Synchronous video generation with progress updates
        """
        try:
            from main import generate_audio, download_background_video, create_hadith_video
            
            # Step 1: Generate audio (30%)
            self._update_progress(job_id, 10, "توليد الملف الصوتي...")
            audio_path = os.path.join(config.TEMP_FOLDER, f'audio_{job_id}.mp3')
            audio_result = generate_audio(None, audio_path, hadith_data=hadith_data)
            
            if not audio_result:
                raise Exception("فشل في توليد الصوت")
            
            self._update_progress(job_id, 30, "تم توليد الملف الصوتي بنجاح")
            
            # Step 2: Get background video (60%)
            self._update_progress(job_id, 40, "تحميل فيديو الخلفية...")
            video_type = options.get('video_type') if options else None
            background_video = download_background_video(video_type)
            
            if not background_video:
                raise Exception("فشل في تحميل فيديو الخلفية")
            
            self._update_progress(job_id, 60, "تم تحميل فيديو الخلفية بنجاح")
            
            # Step 3: Create final video (90%)
            self._update_progress(job_id, 70, "إنشاء الفيديو النهائي...")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"hadith_video_{timestamp}_{job_id[-8:]}.mp4"
            output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)
            
            video_result = create_hadith_video(hadith_data, background_video, audio_path, output_path)
            
            if not video_result:
                raise Exception("فشل في إنشاء الفيديو النهائي")
            
            # Cache the result
            cache_key = self.cache._generate_key(hadith_data)
            self.cache.set(cache_key, output_filename)
            
            self._update_progress(job_id, 100, "تم إنشاء الفيديو بنجاح", "completed")
            
            # Cleanup
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            return output_filename
            
        except Exception as e:
            logger.error(f"Error in sync video generation: {e}")
            self._update_progress(job_id, 0, f"فشل: {str(e)}", "failed")
            raise e
    
    def get_job_status(self, job_id: str) -> Dict:
        """Get job status and progress"""
        if job_id not in self.job_progress:
            return {'error': 'Job not found'}
        
        progress_info = self.job_progress[job_id].copy()
        
        # Check if job is completed
        if job_id in self.active_jobs:
            future = self.active_jobs[job_id]
            if future.done():
                try:
                    result = future.result()
                    progress_info.update({
                        'status': 'completed',
                        'progress': 100,
                        'result': result,
                        'message': 'تم إنشاء الفيديو بنجاح'
                    })
                except Exception as e:
                    progress_info.update({
                        'status': 'failed',
                        'progress': 0,
                        'error': str(e),
                        'message': f'فشل: {str(e)}'
                    })
                
                # Cleanup completed job
                del self.active_jobs[job_id]
        
        return progress_info
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""
        try:
            if job_id in self.active_jobs:
                future = self.active_jobs[job_id]
                cancelled = future.cancel()
                if cancelled:
                    del self.active_jobs[job_id]
                    self.job_progress[job_id].update({
                        'status': 'cancelled',
                        'message': 'تم إلغاء المهمة'
                    })
                return cancelled
            return False
        except Exception as e:
            logger.error(f"Error cancelling job: {e}")
            return False
    
    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Clean up old job records"""
        try:
            cutoff_time = time.time() - (max_age_hours * 3600)
            old_jobs = []
            
            for job_id, progress in self.job_progress.items():
                start_time = progress.get('start_time', 0)
                if start_time < cutoff_time:
                    old_jobs.append(job_id)
            
            for job_id in old_jobs:
                if job_id in self.active_jobs:
                    self.cancel_job(job_id)
                if job_id in self.job_progress:
                    del self.job_progress[job_id]
            
            logger.info(f"Cleaned up {len(old_jobs)} old jobs")
        except Exception as e:
            logger.error(f"Error cleaning up jobs: {e}")


class BackgroundVideoCache:
    """
    تخزين مؤقت لفيديوهات الخلفية لتحسين الأداء
    Background Video Cache for Performance
    """
    
    def __init__(self):
        self.cache_dir = os.path.join(config.TEMP_FOLDER, 'bg_videos')
        os.makedirs(self.cache_dir, exist_ok=True)
        self.cache_info = {}
        self.max_cache_size = 10  # Maximum number of cached videos
    
    def get_cached_video(self, query: str) -> Optional[str]:
        """Get cached background video"""
        try:
            cache_key = hashlib.md5(str(query).encode()).hexdigest()
            cache_path = os.path.join(self.cache_dir, f"{cache_key}.mp4")
            
            if os.path.exists(cache_path):
                # Check if cache is still valid (24 hours)
                cache_age = time.time() - os.path.getmtime(cache_path)
                if cache_age < 86400:  # 24 hours
                    logger.info(f"استخدام فيديو خلفية محفوظ مؤقتاً: {query}")
                    return cache_path
                else:
                    # Remove expired cache
                    os.remove(cache_path)
            
            return None
        except Exception as e:
            logger.error(f"Error getting cached video: {e}")
            return None
    
    def cache_video(self, query: str, video_path: str) -> bool:
        """Cache background video"""
        try:
            cache_key = hashlib.md5(str(query).encode()).hexdigest()
            cache_path = os.path.join(self.cache_dir, f"{cache_key}.mp4")
            
            # Copy video to cache
            import shutil
            shutil.copy2(video_path, cache_path)
            
            # Update cache info
            self.cache_info[cache_key] = {
                'query': query,
                'path': cache_path,
                'created_at': time.time(),
                'size': os.path.getsize(cache_path)
            }
            
            # Cleanup old cache if needed
            self._cleanup_old_cache()
            
            logger.info(f"تم حفظ فيديو الخلفية مؤقتاً: {query}")
            return True
        except Exception as e:
            logger.error(f"Error caching video: {e}")
            return False
    
    def _cleanup_old_cache(self):
        """Clean up old cache files"""
        try:
            # Get all cache files with their modification times
            cache_files = []
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.mp4'):
                    filepath = os.path.join(self.cache_dir, filename)
                    mtime = os.path.getmtime(filepath)
                    cache_files.append((filepath, mtime))
            
            # Sort by modification time (oldest first)
            cache_files.sort(key=lambda x: x[1])
            
            # Remove oldest files if we exceed max cache size
            while len(cache_files) > self.max_cache_size:
                old_file, _ = cache_files.pop(0)
                os.remove(old_file)
                logger.info(f"تم حذف فيديو خلفية قديم: {os.path.basename(old_file)}")
        
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")


# Singletons
cache_manager = CacheManager()
async_video_generator = AsyncVideoGenerator()
bg_video_cache = BackgroundVideoCache()