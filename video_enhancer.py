# -*- coding: utf-8 -*-
"""
تحسين الفيديو محلياً - Local Video Enhancement Module
"""

import os
import logging
import numpy as np
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# محاولة استيراد OpenCV
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("opencv غير متوفر - تحسين الفيديو معطل")

# محاولة استيراد MoviePy
try:
    from moviepy.editor import VideoFileClip, CompositeVideoClip
    from moviepy.video.fx import colorx, lum_contrast
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    logger.warning("moviepy غير متوفر")


class VideoEnhancer:
    """
    فئة لتحسين جودة الفيديو محلياً
    Class for local video quality enhancement
    """
    
    def __init__(self, settings: dict = None):
        """
        تهيئة محسن الفيديو
        Initialize video enhancer
        
        Args:
            settings: إعدادات التحسين من config.py
        """
        self.settings = settings or {}
        self.enabled = self.settings.get('enabled', True)
    
    def enhance(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        تحسين ملف فيديو
        Enhance a video file
        
        Args:
            input_path: مسار الفيديو الأصلي
            output_path: مسار الفيديو المحسن (اختياري)
            
        Returns:
            مسار الفيديو المحسن
        """
        if not self.enabled:
            logger.info("تحسين الفيديو معطل")
            return input_path
        
        if not CV2_AVAILABLE:
            logger.warning("OpenCV غير متوفر - استخدام moviepy فقط")
            return self._enhance_with_moviepy(input_path, output_path)
        
        if not os.path.exists(input_path):
            logger.error(f"الفيديو غير موجود: {input_path}")
            return input_path
        
        try:
            logger.info(f"بدء تحسين الفيديو: {input_path}")
            
            # فتح الفيديو
            cap = cv2.VideoCapture(input_path)
            
            if not cap.isOpened():
                logger.error("فشل في فتح الفيديو")
                return input_path
            
            # الحصول على خصائص الفيديو
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # تحديد مسار الإخراج
            if not output_path:
                base, ext = os.path.splitext(input_path)
                output_path = f"{base}_enhanced{ext}"
            
            # إنشاء كائن الكتابة
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # تحسين الإطار
                enhanced_frame = self._enhance_frame(frame)
                
                out.write(enhanced_frame)
                frame_count += 1
                
                if frame_count % 100 == 0:
                    progress = (frame_count / total_frames) * 100
                    logger.info(f"تقدم تحسين الفيديو: {progress:.1f}%")
            
            # إغلاق الملفات
            cap.release()
            out.release()
            
            # دمج الصوت مع الفيديو المحسن
            output_path = self._merge_audio(input_path, output_path)
            
            logger.info(f"تم حفظ الفيديو المحسن: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"خطأ في تحسين الفيديو: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return input_path
    
    def _enhance_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        تحسين إطار واحد من الفيديو
        Enhance a single video frame
        """
        try:
            # تصحيح الألوان
            if self.settings.get('color_correction', True):
                frame = self._color_correction(frame)
            
            # تعديل السطوع والتباين
            brightness = self.settings.get('brightness', 1.05)
            contrast = self.settings.get('contrast', 1.1)
            
            if brightness != 1.0 or contrast != 1.0:
                frame = cv2.convertScaleAbs(frame, alpha=contrast, beta=(brightness - 1) * 50)
            
            # تعديل التشبع
            saturation = self.settings.get('saturation', 1.15)
            if saturation != 1.0:
                frame = self._adjust_saturation(frame, saturation)
            
            # زيادة الحدة
            if self.settings.get('sharpening', True):
                strength = self.settings.get('sharpening_strength', 1.3)
                frame = self._sharpen(frame, strength)
            
            # إزالة التشويش
            if self.settings.get('denoise', True):
                strength = self.settings.get('denoise_strength', 3)
                frame = self._denoise(frame, strength)
            
            # تأثير التظليل الدائري (Vignette)
            if self.settings.get('vignette', True):
                strength = self.settings.get('vignette_strength', 0.3)
                frame = self._add_vignette(frame, strength)
            
            # تأثير حبيبات الفيلم
            if self.settings.get('film_grain', False):
                strength = self.settings.get('film_grain_strength', 0.1)
                frame = self._add_film_grain(frame, strength)
            
            return frame
            
        except Exception as e:
            logger.error(f"خطأ في تحسين الإطار: {str(e)}")
            return frame
    
    def _color_correction(self, frame: np.ndarray) -> np.ndarray:
        """
        تصحيح الألوان تلقائياً
        Auto color correction
        """
        try:
            # تحويل إلى LAB
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # تطبيق CLAHE على قناة الإضاءة
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # دمج القنوات
            lab = cv2.merge([l, a, b])
            return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            
        except Exception as e:
            logger.error(f"خطأ في تصحيح الألوان: {str(e)}")
            return frame
    
    def _adjust_saturation(self, frame: np.ndarray, factor: float) -> np.ndarray:
        """
        تعديل تشبع الألوان
        Adjust color saturation
        """
        try:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * factor, 0, 255)
            return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        except Exception as e:
            logger.error(f"خطأ في تعديل التشبع: {str(e)}")
            return frame
    
    def _sharpen(self, frame: np.ndarray, strength: float) -> np.ndarray:
        """
        زيادة حدة الصورة
        Sharpen image
        """
        try:
            # مرشح unsharp mask
            gaussian = cv2.GaussianBlur(frame, (0, 0), 3)
            sharpened = cv2.addWeighted(frame, 1 + strength, gaussian, -strength, 0)
            return sharpened
        except Exception as e:
            logger.error(f"خطأ في زيادة الحدة: {str(e)}")
            return frame
    
    def _denoise(self, frame: np.ndarray, strength: int) -> np.ndarray:
        """
        إزالة التشويش
        Remove noise
        """
        try:
            return cv2.fastNlMeansDenoisingColored(frame, None, strength, strength, 7, 21)
        except Exception as e:
            logger.error(f"خطأ في إزالة التشويش: {str(e)}")
            return frame
    
    def _add_vignette(self, frame: np.ndarray, strength: float) -> np.ndarray:
        """
        إضافة تأثير التظليل الدائري
        Add vignette effect
        """
        try:
            rows, cols = frame.shape[:2]
            
            # إنشاء قناع دائري
            X = cv2.getGaussianKernel(cols, cols * 0.75)
            Y = cv2.getGaussianKernel(rows, rows * 0.75)
            
            mask = Y * X.T
            mask = mask / mask.max()
            mask = 1 - (1 - mask) * strength
            
            # تطبيق القناع
            result = frame.copy().astype(np.float32)
            for i in range(3):
                result[:, :, i] = result[:, :, i] * mask
            
            return np.clip(result, 0, 255).astype(np.uint8)
            
        except Exception as e:
            logger.error(f"خطأ في إضافة التظليل: {str(e)}")
            return frame
    
    def _add_film_grain(self, frame: np.ndarray, strength: float) -> np.ndarray:
        """
        إضافة تأثير حبيبات الفيلم
        Add film grain effect
        """
        try:
            noise = np.random.normal(0, strength * 255, frame.shape).astype(np.int16)
            result = frame.astype(np.int16) + noise
            return np.clip(result, 0, 255).astype(np.uint8)
        except Exception as e:
            logger.error(f"خطأ في إضافة حبيبات الفيلم: {str(e)}")
            return frame
    
    def _merge_audio(self, original_path: str, enhanced_path: str) -> str:
        """
        دمج الصوت من الفيديو الأصلي مع الفيديو المحسن
        Merge audio from original video with enhanced video
        """
        if not MOVIEPY_AVAILABLE:
            return enhanced_path
        
        try:
            logger.info("دمج الصوت مع الفيديو المحسن...")
            
            original = VideoFileClip(original_path)
            enhanced = VideoFileClip(enhanced_path)
            
            if original.audio:
                enhanced = enhanced.set_audio(original.audio)
                
                base, ext = os.path.splitext(enhanced_path)
                final_path = f"{base}_with_audio{ext}"
                
                enhanced.write_videofile(final_path, codec='libx264', audio_codec='aac')
                
                original.close()
                enhanced.close()
                
                # حذف الملف بدون صوت
                try:
                    os.remove(enhanced_path)
                except:
                    pass
                
                return final_path
            else:
                original.close()
                enhanced.close()
                return enhanced_path
                
        except Exception as e:
            logger.error(f"خطأ في دمج الصوت: {str(e)}")
            return enhanced_path
    
    def _enhance_with_moviepy(self, input_path: str, output_path: str = None) -> str:
        """
        تحسين الفيديو باستخدام MoviePy فقط
        Enhance video using MoviePy only
        """
        if not MOVIEPY_AVAILABLE:
            return input_path
        
        try:
            clip = VideoFileClip(input_path)
            
            # تعديل السطوع
            brightness = self.settings.get('brightness', 1.05)
            if brightness != 1.0:
                clip = clip.fx(colorx, brightness)
            
            # تعديل التباين
            contrast = self.settings.get('contrast', 1.1)
            if contrast != 1.0:
                clip = clip.fx(lum_contrast, contrast=50 * (contrast - 1))
            
            if not output_path:
                base, ext = os.path.splitext(input_path)
                output_path = f"{base}_enhanced{ext}"
            
            clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
            clip.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"خطأ في تحسين الفيديو (MoviePy): {str(e)}")
            return input_path
    
    def apply_ken_burns(self, clip, zoom: float = 1.1) -> 'VideoFileClip':
        """
        تطبيق تأثير Ken Burns (تكبير وتحريك)
        Apply Ken Burns effect (zoom and pan)
        """
        if not MOVIEPY_AVAILABLE:
            return clip
        
        try:
            duration = clip.duration
            
            def zoom_effect(get_frame, t):
                frame = get_frame(t)
                zoom_factor = 1 + (zoom - 1) * (t / duration)
                
                h, w = frame.shape[:2]
                new_h, new_w = int(h / zoom_factor), int(w / zoom_factor)
                
                y1 = (h - new_h) // 2
                x1 = (w - new_w) // 2
                
                cropped = frame[y1:y1+new_h, x1:x1+new_w]
                
                if CV2_AVAILABLE:
                    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)
                else:
                    from PIL import Image
                    img = Image.fromarray(cropped)
                    img = img.resize((w, h), Image.Resampling.LANCZOS)
                    return np.array(img)
            
            return clip.fl(zoom_effect)
            
        except Exception as e:
            logger.error(f"خطأ في تطبيق Ken Burns: {str(e)}")
            return clip


def enhance_video(input_path: str, settings: dict = None) -> str:
    """
    وظيفة مساعدة لتحسين الفيديو
    Helper function to enhance video
    
    Args:
        input_path: مسار الفيديو
        settings: إعدادات التحسين
        
    Returns:
        مسار الفيديو المحسن
    """
    enhancer = VideoEnhancer(settings)
    return enhancer.enhance(input_path)
