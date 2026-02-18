# -*- coding: utf-8 -*-
"""
توليد الصور والفيديو والصوت بالذكاء الاصطناعي
AI Generation Module - Image, Video, and Voice
"""

import os
import logging
import requests
import json
from typing import Optional, Dict, Any
import config

logger = logging.getLogger(__name__)


# ===========================
# ElevenLabs Voice Generation
# ===========================

class ElevenLabsGenerator:
    """
    توليد الصوت باستخدام ElevenLabs API
    Voice generation using ElevenLabs API
    """
    
    BASE_URL = "https://api.elevenlabs.io/v1"
    
    def __init__(self, api_key: str = None):
        """تهيئة مولد ElevenLabs"""
        self.api_key = api_key or getattr(config, 'ELEVENLABS_API_KEY', '')
        self.voice_id = getattr(config, 'ELEVENLABS_VOICE_ID', 'pNInz6obpgDQGcFmaJgB')
        self.model_id = getattr(config, 'ELEVENLABS_MODEL_ID', 'eleven_multilingual_v2')
        self.settings = getattr(config, 'ELEVENLABS_SETTINGS', {})
    
    def is_available(self) -> bool:
        """التحقق من توفر API"""
        return bool(self.api_key)
    
    def generate_speech(self, text: str, output_path: str) -> Optional[str]:
        """
        توليد ملف صوتي من النص
        Generate audio file from text
        
        Args:
            text: النص المراد تحويله
            output_path: مسار حفظ الملف
            
        Returns:
            مسار الملف أو None
        """
        if not self.is_available():
            logger.warning("ElevenLabs API غير متوفر")
            return None
        
        try:
            logger.info("توليد الصوت باستخدام ElevenLabs...")
            
            url = f"{self.BASE_URL}/text-to-speech/{self.voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": self.model_id,
                "voice_settings": {
                    "stability": self.settings.get('stability', 0.5),
                    "similarity_boost": self.settings.get('similarity_boost', 0.75),
                    "style": self.settings.get('style', 0.5),
                    "use_speaker_boost": self.settings.get('use_speaker_boost', True)
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=60)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"تم حفظ الصوت: {output_path}")
            return output_path
            
        except requests.exceptions.RequestException as e:
            logger.error(f"خطأ في ElevenLabs API: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"خطأ في توليد الصوت: {str(e)}")
            return None
    
    def get_voices(self) -> list:
        """الحصول على قائمة الأصوات المتاحة"""
        if not self.is_available():
            return []
        
        try:
            url = f"{self.BASE_URL}/voices"
            headers = {"xi-api-key": self.api_key}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('voices', [])
            
        except Exception as e:
            logger.error(f"خطأ في جلب الأصوات: {str(e)}")
            return []


# ===========================
# OpenAI Image Generation
# ===========================

class OpenAIImageGenerator:
    """
    توليد الصور باستخدام OpenAI DALL-E
    Image generation using OpenAI DALL-E
    """
    
    BASE_URL = "https://api.openai.com/v1"
    
    def __init__(self, api_key: str = None):
        """تهيئة مولد OpenAI"""
        self.api_key = api_key or getattr(config, 'OPENAI_API_KEY', '')
        self.model = getattr(config, 'IMAGE_GEN_MODEL', 'dall-e-3')
        self.size = getattr(config, 'IMAGE_GEN_SIZE', '1792x1024')
        self.quality = getattr(config, 'IMAGE_GEN_QUALITY', 'hd')
        self.style = getattr(config, 'IMAGE_GEN_STYLE', 'natural')
    
    def is_available(self) -> bool:
        """التحقق من توفر API"""
        return bool(self.api_key)
    
    def generate_image(self, prompt: str, output_path: str) -> Optional[str]:
        """
        توليد صورة من الوصف
        Generate image from prompt
        
        Args:
            prompt: وصف الصورة
            output_path: مسار حفظ الصورة
            
        Returns:
            مسار الصورة أو None
        """
        if not self.is_available():
            logger.warning("OpenAI API غير متوفر")
            return None
        
        try:
            logger.info(f"توليد صورة: {prompt[:50]}...")
            
            url = f"{self.BASE_URL}/images/generations"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "prompt": prompt,
                "n": 1,
                "size": self.size,
                "quality": self.quality,
                "style": self.style
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            image_url = result['data'][0]['url']
            
            # تحميل الصورة
            image_response = requests.get(image_url, timeout=60)
            image_response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(image_response.content)
            
            logger.info(f"تم حفظ الصورة: {output_path}")
            return output_path
            
        except requests.exceptions.RequestException as e:
            logger.error(f"خطأ في OpenAI API: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"خطأ في توليد الصورة: {str(e)}")
            return None


# ===========================
# Kling AI Video Generation (KIE API)
# ===========================

class KlingVideoGenerator:
    """
    توليد الفيديو باستخدام Kling AI API (KIE)
    Video generation using Kling AI API (KIE)
    """
    
    BASE_URL = "https://api.klingai.com/v1"
    
    def __init__(self, api_key: str = None):
        """تهيئة مولد Kling AI"""
        self.api_key = api_key or getattr(config, 'KLING_API_KEY', '')
        self.access_key = getattr(config, 'KLING_ACCESS_KEY', '')
        self.secret_key = getattr(config, 'KLING_SECRET_KEY', '')
    
    def is_available(self) -> bool:
        """التحقق من توفر API"""
        return bool(self.api_key and self.access_key)
    
    def generate_video(self, prompt: str, image_path: str = None, duration: int = 4) -> Optional[str]:
        """
        توليد فيديو من نص ووصف
        Generate video from text and description
        
        Args:
            prompt: وصف الفيديو المطلوب
            image_path: مسار صورة البداية (اختياري)
            duration: مدة الفيديو بالثواني
            
        Returns:
            رابط الفيديو أو None
        """
        try:
            if not self.is_available():
                logger.error("Kling API غير متوفر")
                return None
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'X-Access-Key': self.access_key
            }
            
            payload = {
                'prompt': prompt,
                'duration': duration,
                'aspect_ratio': '16:9',
                'fps': 24,
                'quality': 'high',
                'motion_strength': 0.7
            }
            
            if image_path and os.path.exists(image_path):
                # Upload image first
                image_url = self._upload_image(image_path)
                if image_url:
                    payload['image_url'] = image_url
            
            logger.info(f"إرسال طلب توليد فيديو إلى Kling AI: {prompt[:50]}...")
            
            # Start video generation
            response = requests.post(
                f"{self.BASE_URL}/videos/generations",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            task_id = result.get('task_id')
            
            if not task_id:
                logger.error("لم يتم الحصول على معرف المهمة")
                return None
            
            # Poll for completion
            video_url = self._poll_for_completion(task_id)
            return video_url
        
        except requests.exceptions.RequestException as e:
            logger.error(f"خطأ في طلب Kling API: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"خطأ في توليد الفيديو بـ Kling: {str(e)}")
            return None
    
    def _upload_image(self, image_path: str) -> Optional[str]:
        """رفع الصورة إلى Kling"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'X-Access-Key': self.access_key
            }
            
            with open(image_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f"{self.BASE_URL}/images/upload",
                    headers=headers,
                    files=files,
                    timeout=30
                )
                response.raise_for_status()
                
                result = response.json()
                return result.get('url')
        
        except Exception as e:
            logger.error(f"خطأ في رفع الصورة: {e}")
            return None
    
    def _poll_for_completion(self, task_id: str, max_wait: int = 300) -> Optional[str]:
        """انتظار اكتمال توليد الفيديو"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'X-Access-Key': self.access_key
            }
            
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                response = requests.get(
                    f"{self.BASE_URL}/videos/generations/{task_id}",
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                
                result = response.json()
                status = result.get('status')
                
                if status == 'completed':
                    video_url = result.get('video_url')
                    logger.info(f"تم توليد الفيديو بنجاح: {video_url}")
                    return video_url
                elif status == 'failed':
                    error_msg = result.get('error', 'Unknown error')
                    logger.error(f"فشل في توليد الفيديو: {error_msg}")
                    return None
                elif status in ['pending', 'processing']:
                    logger.info(f"توليد الفيديو قيد المعالجة... ({status})")
                    time.sleep(10)
                else:
                    logger.warning(f"حالة غير معروفة: {status}")
                    time.sleep(5)
            
            logger.error("انتهت مهلة انتظار توليد الفيديو")
            return None
        
        except Exception as e:
            logger.error(f"خطأ في انتظار اكتمال الفيديو: {e}")
            return None
    """
    توليد الصور باستخدام Stability AI
    Image generation using Stability AI
    """
    
    BASE_URL = "https://api.stability.ai/v1"
    
    def __init__(self, api_key: str = None):
        """تهيئة مولد Stability"""
        self.api_key = api_key or getattr(config, 'STABILITY_API_KEY', '')
        self.model = getattr(config, 'STABILITY_MODEL', 'stable-diffusion-xl-1024-v1-0')
    
    def is_available(self) -> bool:
        """التحقق من توفر API"""
        return bool(self.api_key)
    
    def generate_image(self, prompt: str, output_path: str, 
                       width: int = 1024, height: int = 576) -> Optional[str]:
        """
        توليد صورة من الوصف
        Generate image from prompt
        """
        if not self.is_available():
            logger.warning("Stability API غير متوفر")
            return None
        
        try:
            logger.info(f"توليد صورة (Stability): {prompt[:50]}...")
            
            url = f"{self.BASE_URL}/generation/{self.model}/text-to-image"
            
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "text_prompts": [{"text": prompt, "weight": 1}],
                "cfg_scale": 7,
                "height": height,
                "width": width,
                "samples": 1,
                "steps": 30
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            
            if 'artifacts' in result and len(result['artifacts']) > 0:
                import base64
                image_data = base64.b64decode(result['artifacts'][0]['base64'])
                
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                
                logger.info(f"تم حفظ الصورة: {output_path}")
                return output_path
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في توليد الصورة (Stability): {str(e)}")
            return None


# ===========================
# Google Gemini Image Generation
# ===========================

class GeminiImageGenerator:
    """
    توليد الصور باستخدام Google Gemini
    Image generation using Google Gemini
    """
    
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    
    def __init__(self, api_key: str = None):
        """تهيئة مولد Gemini"""
        self.api_key = api_key or getattr(config, 'GEMINI_API_KEY', '')
        self.model = getattr(config, 'GEMINI_IMAGE_MODEL', 'gemini-2.0-flash-exp')
    
    def is_available(self) -> bool:
        """التحقق من توفر API"""
        return bool(self.api_key)
    
    def generate_image(self, prompt: str, output_path: str) -> Optional[str]:
        """
        توليد صورة من الوصف باستخدام Gemini
        Generate image from prompt using Gemini
        """
        if not self.is_available():
            logger.warning("Gemini API غير متوفر")
            return None
        
        try:
            logger.info(f"توليد صورة (Gemini): {prompt[:50]}...")
            
            url = f"{self.BASE_URL}/models/{self.model}:generateContent?key={self.api_key}"
            
            headers = {"Content-Type": "application/json"}
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": f"Generate an image: {prompt}"
                    }]
                }],
                "generationConfig": {
                    "responseModalities": ["image", "text"],
                    "responseMimeType": "image/png"
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            
            # استخراج الصورة من الاستجابة
            if 'candidates' in result:
                for candidate in result['candidates']:
                    for part in candidate.get('content', {}).get('parts', []):
                        if 'inlineData' in part:
                            import base64
                            image_data = base64.b64decode(part['inlineData']['data'])
                            
                            with open(output_path, 'wb') as f:
                                f.write(image_data)
                            
                            logger.info(f"تم حفظ الصورة: {output_path}")
                            return output_path
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في توليد الصورة (Gemini): {str(e)}")
            return None
    
    def generate_prompt(self, description: str, style: str = 'cinematic') -> str:
        """
        توليد أمر نصي احترافي للصور باستخدام Gemini
        Generate professional image prompt using Gemini
        """
        if not self.is_available():
            return description
        
        try:
            url = f"{self.BASE_URL}/models/gemini-pro:generateContent?key={self.api_key}"
            
            system_prompt = """You are an expert prompt engineer for AI image generation.
            Create a detailed, professional prompt in English for generating a beautiful background image.
            Include: lighting, camera angle, mood, style, colors, and quality descriptors.
            Keep it under 200 words. Output only the prompt, nothing else."""
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": f"{system_prompt}\n\nCreate a prompt for: {description}\nStyle: {style}"
                    }]
                }]
            }
            
            response = requests.post(url, json=data, headers={"Content-Type": "application/json"}, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if 'candidates' in result:
                return result['candidates'][0]['content']['parts'][0]['text'].strip()
            
            return description
            
        except Exception as e:
            logger.error(f"خطأ في توليد الأمر (Gemini): {str(e)}")
            return description


# ===========================
# OpenRouter Image Generation
# ===========================

class OpenRouterImageGenerator:
    """
    توليد الصور عبر OpenRouter
    Image generation via OpenRouter
    """
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self, api_key: str = None):
        """تهيئة مولد OpenRouter"""
        self.api_key = api_key or getattr(config, 'OPENROUTER_API_KEY', '')
        self.model = getattr(config, 'OPENROUTER_IMAGE_MODEL', 'openai/dall-e-3')
    
    def is_available(self) -> bool:
        """التحقق من توفر API"""
        return bool(self.api_key)
    
    def generate_image(self, prompt: str, output_path: str) -> Optional[str]:
        """
        توليد صورة عبر OpenRouter
        Generate image via OpenRouter
        """
        if not self.is_available():
            logger.warning("OpenRouter API غير متوفر")
            return None
        
        try:
            logger.info(f"توليد صورة (OpenRouter): {prompt[:50]}...")
            
            url = f"{self.BASE_URL}/images/generations"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://hadith-video-generator.local",
                "X-Title": "Hadith Video Generator"
            }
            
            data = {
                "model": self.model,
                "prompt": prompt,
                "n": 1,
                "size": "1792x1024"
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            
            if 'data' in result and len(result['data']) > 0:
                image_url = result['data'][0].get('url') or result['data'][0].get('b64_json')
                
                if image_url and image_url.startswith('http'):
                    image_response = requests.get(image_url, timeout=60)
                    image_response.raise_for_status()
                    
                    with open(output_path, 'wb') as f:
                        f.write(image_response.content)
                elif image_url:  # base64
                    import base64
                    image_data = base64.b64decode(image_url)
                    with open(output_path, 'wb') as f:
                        f.write(image_data)
                
                logger.info(f"تم حفظ الصورة: {output_path}")
                return output_path
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في توليد الصورة (OpenRouter): {str(e)}")
            return None
    
    def generate_prompt(self, description: str, style: str = 'cinematic') -> str:
        """
        توليد أمر نصي باستخدام نموذج لغوي عبر OpenRouter
        Generate prompt using LLM via OpenRouter
        """
        if not self.is_available():
            return description
        
        try:
            url = f"{self.BASE_URL}/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "google/gemini-pro",
                "messages": [{
                    "role": "user",
                    "content": f"""Create a detailed image generation prompt in English for: {description}
                    Style: {style}
                    Include: lighting, camera angle, mood, colors, quality (4K, cinematic).
                    Output only the prompt."""
                }]
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            logger.error(f"خطأ في توليد الأمر (OpenRouter): {str(e)}")
            return description


# ===========================
# Ollama Local Image/Prompt Generation
# ===========================

class OllamaGenerator:
    """
    توليد الأوامر النصية محلياً باستخدام Ollama
    Local prompt generation using Ollama
    """
    
    def __init__(self):
        """تهيئة Ollama"""
        self.host = getattr(config, 'OLLAMA_HOST', 'http://localhost:11434')
        self.model = getattr(config, 'OLLAMA_MODEL', 'llava')
    
    def is_available(self) -> bool:
        """التحقق من توفر Ollama"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_prompt(self, description: str, style: str = 'cinematic') -> str:
        """
        توليد أمر نصي محلياً باستخدام Ollama
        Generate prompt locally using Ollama
        """
        if not self.is_available():
            logger.warning("Ollama غير متوفر")
            return description
        
        try:
            url = f"{self.host}/api/generate"
            
            data = {
                "model": self.model,
                "prompt": f"""Create a detailed image generation prompt in English for: {description}
                Style: {style}
                Include: lighting, camera angle, mood, colors, quality descriptors.
                Output only the prompt, nothing else.""",
                "stream": False
            }
            
            response = requests.post(url, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', description).strip()
            
        except Exception as e:
            logger.error(f"خطأ في Ollama: {str(e)}")
            return description


# ===========================
# Video Generation (Runway, Pika, Kling, Veo)
# ===========================

# ===========================
# Kling AI Video Generation (KIE API)
# ===========================

class KlingVideoGenerator:
    """
    توليد الفيديو باستخدام Kling AI API (KIE)
    Video generation using Kling AI API (KIE)
    """
    
    BASE_URL = "https://api.klingai.com/v1"
    
    def __init__(self, api_key: str = None):
        """تهيئة مولد Kling AI"""
        self.api_key = api_key or getattr(config, 'KLING_API_KEY', '')
        self.access_key = getattr(config, 'KLING_ACCESS_KEY', '')
        self.secret_key = getattr(config, 'KLING_SECRET_KEY', '')
    
    def is_available(self) -> bool:
        """التحقق من توفر API"""
        return bool(self.api_key and self.access_key)
    
    def generate_video(self, prompt: str, image_path: str = None, duration: int = 4) -> Optional[str]:
        """
        توليد فيديو من نص ووصف
        Generate video from text and description
        
        Args:
            prompt: وصف الفيديو المطلوب
            image_path: مسار صورة البداية (اختياري)
            duration: مدة الفيديو بالثواني
            
        Returns:
            رابط الفيديو أو None
        """
        try:
            if not self.is_available():
                logger.error("Kling API غير متوفر")
                return None
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'X-Access-Key': self.access_key
            }
            
            payload = {
                'prompt': prompt,
                'duration': duration,
                'aspect_ratio': '16:9',
                'fps': 24,
                'quality': 'high',
                'motion_strength': 0.7
            }
            
            if image_path and os.path.exists(image_path):
                # Upload image first
                image_url = self._upload_image(image_path)
                if image_url:
                    payload['image_url'] = image_url
            
            logger.info(f"إرسال طلب توليد فيديو إلى Kling AI: {prompt[:50]}...")
            
            # Start video generation
            response = requests.post(
                f"{self.BASE_URL}/videos/generations",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            task_id = result.get('task_id')
            
            if not task_id:
                logger.error("لم يتم الحصول على معرف المهمة")
                return None
            
            # Poll for completion
            video_url = self._poll_for_completion(task_id)
            return video_url
        
        except requests.exceptions.RequestException as e:
            logger.error(f"خطأ في طلب Kling API: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"خطأ في توليد الفيديو بـ Kling: {str(e)}")
            return None
    
    def _upload_image(self, image_path: str) -> Optional[str]:
        """رفع الصورة إلى Kling"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'X-Access-Key': self.access_key
            }
            
            with open(image_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f"{self.BASE_URL}/images/upload",
                    headers=headers,
                    files=files,
                    timeout=30
                )
                response.raise_for_status()
                
                result = response.json()
                return result.get('url')
        
        except Exception as e:
            logger.error(f"خطأ في رفع الصورة: {e}")
            return None
    
    def _poll_for_completion(self, task_id: str, max_wait: int = 300) -> Optional[str]:
        """انتظار اكتمال توليد الفيديو"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'X-Access-Key': self.access_key
            }
            
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                response = requests.get(
                    f"{self.BASE_URL}/videos/generations/{task_id}",
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                
                result = response.json()
                status = result.get('status')
                
                if status == 'completed':
                    video_url = result.get('video_url')
                    logger.info(f"تم توليد الفيديو بنجاح: {video_url}")
                    return video_url
                elif status == 'failed':
                    error_msg = result.get('error', 'Unknown error')
                    logger.error(f"فشل في توليد الفيديو: {error_msg}")
                    return None
                elif status in ['pending', 'processing']:
                    logger.info(f"توليد الفيديو قيد المعالجة... ({status})")
                    time.sleep(10)
                else:
                    logger.warning(f"حالة غير معروفة: {status}")
                    time.sleep(5)
            
            logger.error("انتهت مهلة انتظار توليد الفيديو")
            return None
        
        except Exception as e:
            logger.error(f"خطأ في انتظار اكتمال الفيديو: {e}")
            return None


class VideoGenerator:
    """
    توليد الفيديو بالذكاء الاصطناعي
    AI Video Generation
    """
    
    def __init__(self):
        """تهيئة مولد الفيديو"""
        self.runway_api_key = getattr(config, 'RUNWAY_API_KEY', '')
        self.pika_api_key = getattr(config, 'PIKA_API_KEY', '')
        self.replicate_api_key = getattr(config, 'REPLICATE_API_KEY', '')
        self.kling_api_key = getattr(config, 'KLING_API_KEY', '')
        self.kling_access_key = getattr(config, 'KLING_ACCESS_KEY', '')
        self.kling_secret_key = getattr(config, 'KLING_SECRET_KEY', '')
        self.veo_api_key = getattr(config, 'VEO_API_KEY', '') or getattr(config, 'GEMINI_API_KEY', '')
        self.settings = getattr(config, 'AI_VIDEO_SETTINGS', {})
        self.provider = getattr(config, 'VIDEO_GEN_PROVIDER', 'local')
    
    def is_available(self) -> bool:
        """التحقق من توفر API"""
        return bool(
            self.runway_api_key or 
            self.pika_api_key or 
            self.replicate_api_key or
            self.kling_api_key or
            self.veo_api_key or
            self.provider == 'local'
        )
    
    def generate_video_from_image(self, image_path: str, output_path: str, 
                                   prompt: str = "") -> Optional[str]:
        """
        توليد فيديو من صورة
        Generate video from image
        """
        provider = self.provider
        
        if provider == 'local':
            return self._generate_local(image_path, output_path, prompt)
        elif provider == 'kling' and self.kling_api_key:
            return self._generate_with_kling(image_path, output_path, prompt)
        elif provider == 'veo' and self.veo_api_key:
            return self._generate_with_veo(image_path, output_path, prompt)
        elif provider == 'replicate' and self.replicate_api_key:
            return self._generate_with_replicate(image_path, output_path, prompt)
        elif provider == 'runway' and self.runway_api_key:
            return self._generate_with_runway(image_path, output_path, prompt)
        elif provider == 'pika' and self.pika_api_key:
            return self._generate_with_pika(image_path, output_path, prompt)
        else:
            logger.warning("لا يوجد مزود فيديو متاح، استخدام التوليد المحلي")
            return self._generate_local(image_path, output_path, prompt)
    
    def _generate_local(self, image_path: str, output_path: str, prompt: str) -> Optional[str]:
        """توليد فيديو محلياً من صورة مع تأثيرات"""
        try:
            logger.info("توليد فيديو محلياً من الصورة...")
            
            from moviepy.editor import ImageClip
            import numpy as np
            
            settings = getattr(config, 'LOCAL_VIDEO_FROM_IMAGES', {})
            duration = settings.get('image_duration', 4.0)
            fps = settings.get('fps', 30)
            
            # إنشاء مقطع من الصورة
            clip = ImageClip(image_path, duration=duration)
            
            # تغيير الحجم
            video_width = getattr(config, 'VIDEO_WIDTH', 1920)
            video_height = getattr(config, 'VIDEO_HEIGHT', 1080)
            clip = clip.resize((video_width, video_height))
            
            # تطبيق تأثير Ken Burns إذا مفعل
            if settings.get('ken_burns_enabled', True):
                zoom = settings.get('ken_burns_zoom', 1.15)
                clip = self._apply_ken_burns_effect(clip, zoom, duration)
            
            # حفظ الفيديو
            clip.write_videofile(
                output_path,
                fps=fps,
                codec='libx264',
                audio=False,
                logger=None
            )
            
            clip.close()
            logger.info(f"تم حفظ الفيديو المحلي: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"خطأ في التوليد المحلي: {str(e)}")
            return None
    
    def _apply_ken_burns_effect(self, clip, zoom: float, duration: float):
        """تطبيق تأثير Ken Burns"""
        try:
            def zoom_effect(get_frame, t):
                frame = get_frame(t)
                progress = t / duration
                current_zoom = 1 + (zoom - 1) * progress
                
                h, w = frame.shape[:2]
                new_h, new_w = int(h / current_zoom), int(w / current_zoom)
                
                y1 = (h - new_h) // 2
                x1 = (w - new_w) // 2
                
                cropped = frame[y1:y1+new_h, x1:x1+new_w]
                
                try:
                    import cv2
                    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)
                except:
                    from PIL import Image
                    import numpy as np
                    img = Image.fromarray(cropped)
                    img = img.resize((w, h), Image.Resampling.LANCZOS)
                    return np.array(img)
            
            return clip.fl(zoom_effect)
        except Exception as e:
            logger.error(f"خطأ في تأثير Ken Burns: {str(e)}")
            return clip
    
    def _generate_with_kling(self, image_path: str, output_path: str, prompt: str) -> Optional[str]:
        """توليد فيديو باستخدام Kling AI"""
        try:
            logger.info("توليد فيديو باستخدام Kling AI...")
            
            import base64
            import time
            import hashlib
            import hmac
            
            # قراءة الصورة
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Kling API endpoint
            url = "https://api.klingai.com/v1/videos/image2video"
            
            timestamp = str(int(time.time()))
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.kling_api_key}",
                "X-Access-Key": self.kling_access_key,
                "X-Timestamp": timestamp
            }
            
            data = {
                "image": f"data:image/png;base64,{image_data}",
                "prompt": prompt or "gentle camera movement, cinematic, smooth motion",
                "duration": self.settings.get('duration', 4),
                "mode": "standard"
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=300)
            response.raise_for_status()
            
            result = response.json()
            
            # انتظار اكتمال التوليد وتحميل الفيديو
            if 'task_id' in result:
                video_url = self._poll_kling_task(result['task_id'])
                if video_url:
                    video_response = requests.get(video_url, timeout=120)
                    video_response.raise_for_status()
                    
                    with open(output_path, 'wb') as f:
                        f.write(video_response.content)
                    
                    return output_path
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في Kling: {str(e)}")
            return None
    
    def _poll_kling_task(self, task_id: str, max_attempts: int = 60) -> Optional[str]:
        """الانتظار حتى اكتمال مهمة Kling"""
        import time
        
        url = f"https://api.klingai.com/v1/videos/task/{task_id}"
        headers = {"Authorization": f"Bearer {self.kling_api_key}"}
        
        for _ in range(max_attempts):
            try:
                response = requests.get(url, headers=headers, timeout=30)
                result = response.json()
                
                if result.get('status') == 'completed':
                    return result.get('video_url')
                elif result.get('status') == 'failed':
                    logger.error("فشلت مهمة Kling")
                    return None
                
                time.sleep(5)
            except Exception as e:
                logger.error(f"خطأ في فحص مهمة Kling: {str(e)}")
        
        return None
    
    def _generate_with_veo(self, image_path: str, output_path: str, prompt: str) -> Optional[str]:
        """توليد فيديو باستخدام Google Veo (Gemini Video)"""
        try:
            logger.info("توليد فيديو باستخدام Google Veo...")
            
            import base64
            
            # قراءة الصورة
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/veo-001:generateVideo?key={self.veo_api_key}"
            
            headers = {"Content-Type": "application/json"}
            
            data = {
                "contents": [{
                    "parts": [
                        {"text": prompt or "smooth cinematic camera movement"},
                        {"inline_data": {"mime_type": "image/png", "data": image_data}}
                    ]
                }],
                "generationConfig": {
                    "videoLength": self.settings.get('duration', 4),
                    "aspectRatio": "16:9"
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=300)
            response.raise_for_status()
            
            result = response.json()
            
            # استخراج الفيديو من الاستجابة
            if 'candidates' in result:
                for candidate in result['candidates']:
                    for part in candidate.get('content', {}).get('parts', []):
                        if 'inlineData' in part and 'video' in part['inlineData'].get('mimeType', ''):
                            video_data = base64.b64decode(part['inlineData']['data'])
                            
                            with open(output_path, 'wb') as f:
                                f.write(video_data)
                            
                            return output_path
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في Veo: {str(e)}")
            return None
    
    def _generate_with_pika(self, image_path: str, output_path: str, prompt: str) -> Optional[str]:
        """توليد فيديو باستخدام Pika Labs"""
        try:
            logger.info("توليد فيديو باستخدام Pika Labs...")
            
            import base64
            
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            url = "https://api.pika.art/v1/generate"
            
            headers = {
                "Authorization": f"Bearer {self.pika_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "image": f"data:image/png;base64,{image_data}",
                "prompt": prompt or "smooth camera movement, cinematic",
                "options": {
                    "duration": self.settings.get('duration', 4),
                    "fps": self.settings.get('fps', 24)
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=300)
            response.raise_for_status()
            
            result = response.json()
            
            if 'video_url' in result:
                video_response = requests.get(result['video_url'], timeout=120)
                video_response.raise_for_status()
                
                with open(output_path, 'wb') as f:
                    f.write(video_response.content)
                
                return output_path
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في Pika: {str(e)}")
            return None


# ===========================
# Prompt Generator
# ===========================

class PromptGenerator:
    """
    توليد الأوامر النصية (Prompts) للصور والفيديو
    Generate prompts for images and videos
    """
    
    def __init__(self):
        """تهيئة مولد الأوامر"""
        self.templates = getattr(config, 'PROMPT_TEMPLATES', {})
        self.settings = getattr(config, 'AUTO_PROMPT_SETTINGS', {})
        self.prompt_provider = getattr(config, 'PROMPT_GEN_PROVIDER', 'local')
        self.prompt_settings = getattr(config, 'PROMPT_GEN_SETTINGS', {})
    
    def generate_video_prompt(self, hadith_text: str, style: str = 'islamic') -> str:
        """
        توليد أمر نصي لفيديو خلفية بناءً على نص الحديث
        Generate video background prompt based on hadith text
        
        Args:
            hadith_text: نص الحديث
            style: نمط الخلفية (islamic, nature, desert, sky, ocean, mountains)
            
        Returns:
            الأمر النصي المولد
        """
        # الحصول على القالب الأساسي
        base_prompt = self.templates.get(style, self.templates.get('islamic', ''))
        
        # تحليل نص الحديث لتخصيص الأمر
        keywords = self._analyze_hadith(hadith_text)
        
        # بناء الأمر النهائي
        prompt_parts = [base_prompt]
        
        if keywords:
            prompt_parts.append(f"مستوحى من: {', '.join(keywords)}")
        
        if self.settings.get('include_quality', True):
            prompt_parts.append(self.settings.get('default_quality', '4K, جودة عالية'))
        
        if self.settings.get('include_style', True):
            prompt_parts.append(self.settings.get('default_style', 'احترافي'))
        
        if self.settings.get('include_mood', True):
            prompt_parts.append(self.settings.get('default_mood', 'هادئ, روحاني'))
        
        return ', '.join(prompt_parts)
    
    def generate_image_prompt(self, hadith_text: str, style: str = 'islamic') -> str:
        """
        توليد أمر نصي لصورة خلفية
        Generate image background prompt
        """
        base = self.generate_video_prompt(hadith_text, style)
        return f"صورة ثابتة, {base}"
    
    def generate_ai_prompt(self, description: str, style: str = 'cinematic') -> str:
        """
        توليد أمر نصي احترافي باستخدام AI
        Generate professional prompt using AI
        
        Args:
            description: وصف مختصر بالعربية
            style: نمط الصورة/الفيديو
            
        Returns:
            أمر نصي احترافي بالإنجليزية
        """
        provider = self.prompt_provider
        
        if provider == 'gemini':
            generator = GeminiImageGenerator()
            if generator.is_available():
                return generator.generate_prompt(description, style)
        
        elif provider == 'openrouter':
            generator = OpenRouterImageGenerator()
            if generator.is_available():
                return generator.generate_prompt(description, style)
        
        elif provider == 'ollama':
            generator = OllamaGenerator()
            if generator.is_available():
                return generator.generate_prompt(description, style)
        
        elif provider == 'openai':
            # استخدام OpenAI لتوليد الأمر
            return self._generate_with_openai(description, style)
        
        # الرجوع للقالب المحلي
        return self.generate_video_prompt(description, style)
    
    def _generate_with_openai(self, description: str, style: str) -> str:
        """توليد أمر باستخدام OpenAI"""
        api_key = getattr(config, 'OPENAI_API_KEY', '')
        if not api_key:
            return description
        
        try:
            url = "https://api.openai.com/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-4",
                "messages": [{
                    "role": "user",
                    "content": f"""Create a detailed image generation prompt in English for: {description}
                    Style: {style}
                    Include: lighting, camera angle, mood, colors, quality (4K, cinematic).
                    Output only the prompt, nothing else."""
                }],
                "max_tokens": 300
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            logger.error(f"خطأ في OpenAI: {str(e)}")
            return description
    
    def _analyze_hadith(self, text: str) -> list:
        """
        تحليل نص الحديث لاستخراج المفاهيم
        Analyze hadith text to extract concepts
        """
        keywords = []
        
        # الكلمات المفتاحية وما يقابلها من مفاهيم بصرية
        concept_map = {
            'جنة': ['حدائق خضراء', 'أنهار جارية'],
            'نور': ['ضوء ساطع', 'إشراق'],
            'رحمة': ['سماء صافية', 'طبيعة هادئة'],
            'صلاة': ['مسجد', 'روحانية'],
            'صدق': ['سماء صافية', 'نقاء'],
            'صبر': ['جبال شامخة', 'قوة'],
            'ليل': ['نجوم', 'قمر', 'سماء ليلية'],
            'فجر': ['شروق', 'ضوء ذهبي'],
            'ماء': ['نهر', 'بحر', 'شلال'],
            'شجر': ['غابة', 'أشجار خضراء']
        }
        
        for keyword, concepts in concept_map.items():
            if keyword in text:
                keywords.extend(concepts[:1])  # إضافة مفهوم واحد فقط
        
        return keywords[:3]  # أقصى 3 مفاهيم
    
    def get_template(self, style: str) -> str:
        """الحصول على قالب بنمط معين"""
        return self.templates.get(style, '')
    
    def list_styles(self) -> list:
        """قائمة الأنماط المتاحة"""
        return list(self.templates.keys())


# ===========================
# Local Video from Images Generator
# ===========================

class LocalVideoGenerator:
    """
    توليد فيديو محلياً من مجموعة صور
    Generate video locally from multiple images
    """
    
    def __init__(self):
        """تهيئة المولد المحلي"""
        self.settings = getattr(config, 'LOCAL_VIDEO_FROM_IMAGES', {})
    
    def generate_video_from_images(self, image_paths: list, output_path: str, 
                                    audio_path: str = None) -> Optional[str]:
        """
        توليد فيديو من مجموعة صور مع تأثيرات انتقالية
        Generate video from multiple images with transitions
        
        Args:
            image_paths: قائمة مسارات الصور
            output_path: مسار حفظ الفيديو
            audio_path: مسار الصوت (اختياري)
            
        Returns:
            مسار الفيديو أو None
        """
        try:
            from moviepy.editor import (
                ImageClip, concatenate_videoclips, CompositeVideoClip,
                AudioFileClip, ColorClip
            )
            import numpy as np
            
            if not image_paths:
                logger.error("لا توجد صور للتحويل")
                return None
            
            logger.info(f"توليد فيديو من {len(image_paths)} صورة...")
            
            # إعدادات
            image_duration = self.settings.get('image_duration', 4.0)
            transition_duration = self.settings.get('transition_duration', 1.5)
            fps = self.settings.get('fps', 30)
            ken_burns = self.settings.get('ken_burns_enabled', True)
            zoom = self.settings.get('ken_burns_zoom', 1.15)
            
            video_width = getattr(config, 'VIDEO_WIDTH', 1920)
            video_height = getattr(config, 'VIDEO_HEIGHT', 1080)
            
            clips = []
            
            for i, img_path in enumerate(image_paths):
                # إنشاء مقطع من الصورة
                clip = ImageClip(img_path, duration=image_duration)
                clip = clip.resize((video_width, video_height))
                
                # تطبيق Ken Burns
                if ken_burns:
                    clip = self._apply_ken_burns(clip, zoom, image_duration, i)
                
                clips.append(clip)
            
            # تطبيق الانتقالات
            transition_type = self.settings.get('transition_type', 'crossfade')
            final_clips = self._apply_transitions(clips, transition_duration, transition_type)
            
            # دمج المقاطع
            final_video = concatenate_videoclips(final_clips, method="compose")
            
            # إضافة الصوت إذا وجد
            if audio_path and os.path.exists(audio_path):
                audio = AudioFileClip(audio_path)
                # ضبط مدة الفيديو حسب الصوت
                if audio.duration > final_video.duration:
                    # تكرار الفيديو
                    final_video = final_video.loop(duration=audio.duration)
                final_video = final_video.set_audio(audio)
            
            # حفظ الفيديو
            final_video.write_videofile(
                output_path,
                fps=fps,
                codec='libx264',
                audio_codec='aac',
                logger=None
            )
            
            # تنظيف
            final_video.close()
            for clip in clips:
                clip.close()
            
            logger.info(f"تم حفظ الفيديو: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"خطأ في توليد الفيديو المحلي: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _apply_ken_burns(self, clip, zoom: float, duration: float, index: int):
        """تطبيق تأثير Ken Burns مع اتجاهات مختلفة"""
        try:
            # تنويع الاتجاه بناءً على الفهرس
            directions = ['zoom_in', 'zoom_out', 'pan_left', 'pan_right']
            direction = directions[index % len(directions)]
            
            def effect(get_frame, t):
                frame = get_frame(t)
                progress = t / duration
                
                h, w = frame.shape[:2]
                
                if direction == 'zoom_in':
                    current_zoom = 1 + (zoom - 1) * progress
                elif direction == 'zoom_out':
                    current_zoom = zoom - (zoom - 1) * progress
                else:
                    current_zoom = 1.1  # تكبير ثابت للتحريك
                
                new_h, new_w = int(h / current_zoom), int(w / current_zoom)
                
                # حساب الموقع
                if direction == 'pan_left':
                    x1 = int((w - new_w) * progress)
                elif direction == 'pan_right':
                    x1 = int((w - new_w) * (1 - progress))
                else:
                    x1 = (w - new_w) // 2
                
                y1 = (h - new_h) // 2
                
                cropped = frame[y1:y1+new_h, x1:x1+new_w]
                
                try:
                    import cv2
                    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)
                except:
                    from PIL import Image
                    import numpy as np
                    img = Image.fromarray(cropped)
                    img = img.resize((w, h), Image.Resampling.LANCZOS)
                    return np.array(img)
            
            return clip.fl(effect)
            
        except Exception as e:
            logger.error(f"خطأ في Ken Burns: {str(e)}")
            return clip
    
    def _apply_transitions(self, clips: list, duration: float, transition_type: str) -> list:
        """تطبيق الانتقالات بين المقاطع"""
        if len(clips) <= 1:
            return clips
        
        result = []
        
        for i, clip in enumerate(clips):
            if i == 0:
                # المقطع الأول: fade in فقط
                clip = clip.fx(fadein, duration)
            elif i == len(clips) - 1:
                # المقطع الأخير: fade out فقط
                clip = clip.fx(fadeout, duration)
            else:
                # المقاطع الوسطى: fade in و fade out
                clip = clip.fx(fadein, duration).fx(fadeout, duration)
            
            result.append(clip)
        
        return result


# ===========================
# Helper Functions
# ===========================

def generate_voice(text: str, output_path: str, use_elevenlabs: bool = True) -> Optional[str]:
    """
    توليد صوت من النص (مع اختيار المزود)
    Generate voice from text
    """
    if use_elevenlabs:
        generator = ElevenLabsGenerator()
        if generator.is_available():
            result = generator.generate_speech(text, output_path)
            if result:
                return result
    
    # الرجوع إلى Edge TTS
    return None


def generate_background_image(prompt: str, output_path: str, 
                               provider: str = None) -> Optional[str]:
    """
    توليد صورة خلفية
    Generate background image
    """
    provider = provider or getattr(config, 'IMAGE_GEN_PROVIDER', 'openai')
    
    if provider == 'openai':
        generator = OpenAIImageGenerator()
    elif provider == 'stability':
        generator = StabilityImageGenerator()
    elif provider == 'gemini':
        generator = GeminiImageGenerator()
    elif provider == 'openrouter':
        generator = OpenRouterImageGenerator()
    else:
        logger.error(f"مزود غير معروف: {provider}")
        return None
    
    if generator.is_available():
        return generator.generate_image(prompt, output_path)
    
    return None


def generate_background_video(image_path: str, output_path: str, 
                               prompt: str = "") -> Optional[str]:
    """
    توليد فيديو خلفية من صورة
    Generate background video from image
    """
    generator = VideoGenerator()
    return generator.generate_video_from_image(image_path, output_path, prompt)


def generate_video_from_images(image_paths: list, output_path: str,
                                audio_path: str = None) -> Optional[str]:
    """
    توليد فيديو محلياً من مجموعة صور
    Generate video locally from images
    """
    generator = LocalVideoGenerator()
    return generator.generate_video_from_images(image_paths, output_path, audio_path)


def create_video_prompt(hadith_text: str, style: str = 'islamic') -> str:
    """
    إنشاء أمر نصي للفيديو
    Create video prompt
    """
    generator = PromptGenerator()
    return generator.generate_video_prompt(hadith_text, style)


def create_ai_prompt(description: str, style: str = 'cinematic') -> str:
    """
    إنشاء أمر نصي احترافي باستخدام AI
    Create professional prompt using AI
    """
    generator = PromptGenerator()
    return generator.generate_ai_prompt(description, style)


def get_available_providers() -> Dict[str, bool]:
    """
    الحصول على قائمة المزودين المتاحين
    Get list of available providers
    """
    return {
        'elevenlabs': ElevenLabsGenerator().is_available(),
        'openai_image': OpenAIImageGenerator().is_available(),
        'stability': StabilityImageGenerator().is_available(),
        'gemini': GeminiImageGenerator().is_available(),
        'openrouter': OpenRouterImageGenerator().is_available(),
        'ollama': OllamaGenerator().is_available(),
        'video_gen': VideoGenerator().is_available(),
        'local_video': True  # دائماً متاح
    }


# تصدير إضافي للموديولات الجديدة
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
