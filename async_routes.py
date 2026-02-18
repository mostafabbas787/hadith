# -*- coding: utf-8 -*-
"""
Enhanced API routes for async video generation and performance improvements
"""

import asyncio
import threading
from functools import wraps
from flask import Flask, request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

def add_async_routes(app):
    """Add async video generation routes to Flask app"""
    
    @app.route('/api/generate_async', methods=['POST'])
    def api_generate_async():
        """
        API لتوليد الفيديو غير المتزامن مع تتبع التقدم
        API endpoint for async video generation with progress tracking
        """
        try:
            from performance_manager import async_video_generator
            
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'لم يتم استلام بيانات صالحة'
                }), 400
            
            hadith_data = data.get('hadith', {})
            options = {
                'video_type': data.get('video_type'),
                'use_ai_voice': data.get('use_ai_voice', True),
                'use_ai_background': data.get('use_ai_background', False),
                'enhance_locally': data.get('enhance_locally', True),
                'custom_prompt': data.get('custom_prompt', '')
            }
            
            if not hadith_data or not hadith_data.get('text'):
                return jsonify({
                    'success': False,
                    'error': 'بيانات الحديث غير صحيحة أو فارغة'
                }), 400
            
            # Start async generation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    async_video_generator.generate_video_async(hadith_data, options)
                )
                return jsonify(result)
            finally:
                loop.close()
            
        except Exception as e:
            logger.error(f"Error in async video generation: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'حدث خطأ: {str(e)}'
            }), 500
    
    @app.route('/api/job_status/<job_id>', methods=['GET'])
    def api_job_status(job_id):
        """
        API للحصول على حالة مهمة التوليد
        API endpoint to get generation job status
        """
        try:
            from performance_manager import async_video_generator
            
            status = async_video_generator.get_job_status(job_id)
            
            if 'error' in status:
                return jsonify({
                    'success': False,
                    'error': status['error']
                }), 404
            
            return jsonify({
                'success': True,
                'status': status
            })
            
        except Exception as e:
            logger.error(f"Error getting job status: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'حدث خطأ: {str(e)}'
            }), 500
    
    @app.route('/api/cancel_job/<job_id>', methods=['POST'])
    def api_cancel_job(job_id):
        """
        API لإلغاء مهمة التوليد
        API endpoint to cancel generation job
        """
        try:
            from performance_manager import async_video_generator
            
            success = async_video_generator.cancel_job(job_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'تم إلغاء المهمة بنجاح'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'لم يتم العثور على المهمة أو لا يمكن إلغاؤها'
                })
            
        except Exception as e:
            logger.error(f"Error cancelling job: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'حدث خطأ: {str(e)}'
            }), 500
    
    @app.route('/api/generate_kie_video', methods=['POST'])
    def api_generate_kie_video():
        """
        API لتوليد الفيديو باستخدام Kling AI (KIE API)
        API endpoint for generating video using Kling AI (KIE API)
        """
        try:
            from ai_generator import KlingVideoGenerator
            
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'لم يتم استلام بيانات صالحة'
                }), 400
            
            prompt = data.get('prompt', '')
            image_path = data.get('image_path')
            duration = data.get('duration', 4)
            
            if not prompt:
                return jsonify({
                    'success': False,
                    'error': 'الرجاء إدخال وصف للفيديو'
                }), 400
            
            # Initialize Kling generator
            kling_gen = KlingVideoGenerator()
            
            if not kling_gen.is_available():
                return jsonify({
                    'success': False,
                    'error': 'خدمة Kling AI غير متوفرة. تحقق من مفاتيح API.'
                }), 500
            
            # Generate video
            logger.info(f"توليد فيديو بـ Kling AI: {prompt[:50]}...")
            video_url = kling_gen.generate_video(prompt, image_path, duration)
            
            if video_url:
                return jsonify({
                    'success': True,
                    'video_url': video_url,
                    'message': 'تم توليد الفيديو بنجاح باستخدام Kling AI'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'فشل في توليد الفيديو. حاول مرة أخرى لاحقاً.'
                }), 500
            
        except Exception as e:
            logger.error(f"Error in KIE video generation: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'حدث خطأ: {str(e)}'
            }), 500
    
    @app.route('/api/cache_status', methods=['GET'])
    def api_cache_status():
        """
        API للحصول على حالة التخزين المؤقت
        API endpoint to get cache status
        """
        try:
            from performance_manager import cache_manager, bg_video_cache
            
            status = {
                'cache_enabled': True,
                'memory_cache_items': len(cache_manager.memory_cache),
                'memory_cache_max': cache_manager.max_size,
                'bg_video_cache_items': len(bg_video_cache.cache_info),
                'bg_video_cache_max': bg_video_cache.max_cache_size
            }
            
            return jsonify({
                'success': True,
                'status': status
            })
            
        except Exception as e:
            logger.error(f"Error getting cache status: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'حدث خطأ: {str(e)}'
            }), 500
    
    @app.route('/api/clear_cache', methods=['POST'])
    def api_clear_cache():
        """
        API لمسح التخزين المؤقت
        API endpoint to clear cache
        """
        try:
            from performance_manager import cache_manager, bg_video_cache
            
            cache_type = request.json.get('cache_type', 'all') if request.json else 'all'
            
            if cache_type == 'all':
                cache_manager.clear()
                bg_video_cache._cleanup_old_cache()
                message = 'تم مسح جميع البيانات المخزنة مؤقتاً'
            elif cache_type == 'memory':
                cache_manager.memory_cache.clear()
                message = 'تم مسح ذاكرة التخزين المؤقت'
            elif cache_type == 'video':
                bg_video_cache._cleanup_old_cache()
                message = 'تم مسح تخزين الفيديوهات المؤقت'
            else:
                return jsonify({
                    'success': False,
                    'error': 'نوع التخزين المؤقت غير مدعوم'
                }), 400
            
            return jsonify({
                'success': True,
                'message': message
            })
            
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'حدث خطأ: {str(e)}'
            }), 500
    
    @app.route('/api/health_check', methods=['GET'])
    def api_health_check():
        """
        API للتحقق من صحة الخدمة
        API endpoint for service health check
        """
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'services': {
                    'audio_enhancer': AUDIO_ENHANCER_AVAILABLE,
                    'video_enhancer': VIDEO_ENHANCER_AVAILABLE,
                    'ai_generator': AI_GENERATOR_AVAILABLE,
                    'performance_manager': PERFORMANCE_MANAGER_AVAILABLE
                }
            }
            
            # Check AI services availability
            if AI_GENERATOR_AVAILABLE:
                try:
                    from ai_generator import ElevenLabsGenerator, KlingVideoGenerator
                    
                    elevenlabs = ElevenLabsGenerator()
                    health_status['services']['elevenlabs'] = elevenlabs.is_available()
                    
                    kling = KlingVideoGenerator()
                    health_status['services']['kling_ai'] = kling.is_available()
                    
                except Exception as e:
                    logger.warning(f"Error checking AI services: {e}")
            
            return jsonify({
                'success': True,
                'health': health_status
            })
            
        except Exception as e:
            logger.error(f"Error in health check: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'حدث خطأ: {str(e)}'
            }), 500

# Global imports for routes
try:
    from performance_manager import async_video_generator, cache_manager, bg_video_cache
    from datetime import datetime
    PERFORMANCE_MANAGER_AVAILABLE = True
except ImportError:
    PERFORMANCE_MANAGER_AVAILABLE = False

# Import availability checks
try:
    from audio_enhancer import AudioEnhancer, enhance_audio
    AUDIO_ENHANCER_AVAILABLE = True
except ImportError:
    AUDIO_ENHANCER_AVAILABLE = False

try:
    from video_enhancer import VideoEnhancer, enhance_video
    VIDEO_ENHANCER_AVAILABLE = True
except ImportError:
    VIDEO_ENHANCER_AVAILABLE = False

try:
    from ai_generator import (
        ElevenLabsGenerator, 
        KlingVideoGenerator
    )
    AI_GENERATOR_AVAILABLE = True
except ImportError:
    AI_GENERATOR_AVAILABLE = False