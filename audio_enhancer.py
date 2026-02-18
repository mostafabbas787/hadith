# -*- coding: utf-8 -*-
"""
تحسين الصوت محلياً - Local Audio Enhancement Module
"""

import os
import logging
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)

# محاولة استيراد المكتبات المطلوبة
try:
    from pydub import AudioSegment
    from pydub.effects import normalize, compress_dynamic_range
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logger.warning("pydub غير متوفر - التحسين المحلي للصوت معطل")

try:
    import noisereduce as nr
    NOISEREDUCE_AVAILABLE = True
except ImportError:
    NOISEREDUCE_AVAILABLE = False
    logger.warning("noisereduce غير متوفر - إزالة الضوضاء معطلة")

try:
    from scipy.io import wavfile
    from scipy import signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("scipy غير متوفر - بعض التحسينات معطلة")


class AudioEnhancer:
    """
    فئة لتحسين جودة الصوت محلياً
    Class for local audio quality enhancement
    """
    
    def __init__(self, settings: dict = None):
        """
        تهيئة محسن الصوت
        Initialize audio enhancer
        
        Args:
            settings: إعدادات التحسين من config.py
        """
        self.settings = settings or {}
        self.enabled = self.settings.get('enabled', True)
    
    def enhance(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        تحسين ملف صوتي
        Enhance an audio file
        
        Args:
            input_path: مسار الملف الأصلي
            output_path: مسار الملف المحسن (اختياري)
            
        Returns:
            مسار الملف المحسن
        """
        if not self.enabled:
            logger.info("تحسين الصوت معطل")
            return input_path
        
        if not PYDUB_AVAILABLE:
            logger.warning("مكتبة pydub غير متوفرة")
            return input_path
        
        if not os.path.exists(input_path):
            logger.error(f"الملف غير موجود: {input_path}")
            return input_path
        
        try:
            logger.info(f"بدء تحسين الصوت: {input_path}")
            
            # تحميل الملف الصوتي
            audio = AudioSegment.from_file(input_path)
            
            # تحويل إلى numpy array للمعالجة المتقدمة
            samples = np.array(audio.get_array_of_samples())
            sample_rate = audio.frame_rate
            
            # إزالة الضوضاء
            if self.settings.get('noise_reduction', True) and NOISEREDUCE_AVAILABLE:
                logger.info("إزالة الضوضاء...")
                strength = self.settings.get('noise_reduction_strength', 0.7)
                samples = self._reduce_noise(samples, sample_rate, strength)
            
            # إعادة إنشاء AudioSegment من المصفوفة المعالجة
            audio = AudioSegment(
                samples.tobytes(),
                frame_rate=sample_rate,
                sample_width=audio.sample_width,
                channels=audio.channels
            )
            
            # تطبيع مستوى الصوت
            if self.settings.get('normalize', True):
                logger.info("تطبيع مستوى الصوت...")
                audio = normalize(audio)
            
            # ضغط النطاق الديناميكي
            if self.settings.get('compressor', True):
                logger.info("تطبيق ضغط الصوت...")
                threshold = self.settings.get('compressor_threshold', -20)
                ratio = self.settings.get('compressor_ratio', 4)
                audio = compress_dynamic_range(audio, threshold=threshold, ratio=ratio)
            
            # معادل الصوت (EQ)
            if self.settings.get('equalizer', True) and SCIPY_AVAILABLE:
                logger.info("تطبيق معادل الصوت...")
                audio = self._apply_equalizer(audio)
            
            # تأثيرات التلاشي
            fade_in = self.settings.get('fade_in', 0.5)
            fade_out = self.settings.get('fade_out', 0.5)
            
            if fade_in > 0:
                audio = audio.fade_in(int(fade_in * 1000))
            
            if fade_out > 0:
                audio = audio.fade_out(int(fade_out * 1000))
            
            # تحديد مسار الإخراج
            if not output_path:
                base, ext = os.path.splitext(input_path)
                output_path = f"{base}_enhanced{ext}"
            
            # حفظ الملف المحسن
            audio.export(output_path, format=output_path.split('.')[-1])
            
            logger.info(f"تم حفظ الصوت المحسن: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"خطأ في تحسين الصوت: {str(e)}")
            return input_path
    
    def _reduce_noise(self, samples: np.ndarray, sample_rate: int, strength: float) -> np.ndarray:
        """
        إزالة الضوضاء من الصوت
        Remove noise from audio
        """
        try:
            # تحويل إلى float32
            samples_float = samples.astype(np.float32)
            
            # تطبيق إزالة الضوضاء
            reduced = nr.reduce_noise(
                y=samples_float,
                sr=sample_rate,
                prop_decrease=strength,
                stationary=True
            )
            
            return reduced.astype(samples.dtype)
        except Exception as e:
            logger.error(f"خطأ في إزالة الضوضاء: {str(e)}")
            return samples
    
    def _apply_equalizer(self, audio: 'AudioSegment') -> 'AudioSegment':
        """
        تطبيق معادل الصوت
        Apply audio equalizer
        """
        try:
            eq_settings = self.settings.get('eq_settings', {})
            
            # تعزيز الترددات المنخفضة (bass)
            low_shelf = eq_settings.get('low_shelf', {})
            if low_shelf:
                audio = audio.low_pass_filter(low_shelf.get('freq', 100))
            
            # تعزيز الترددات العالية (treble)
            high_shelf = eq_settings.get('high_shelf', {})
            if high_shelf:
                audio = audio.high_pass_filter(high_shelf.get('freq', 8000))
            
            return audio
        except Exception as e:
            logger.error(f"خطأ في تطبيق المعادل: {str(e)}")
            return audio
    
    def add_reverb(self, audio_path: str, room_size: float = 0.3) -> str:
        """
        إضافة صدى خفيف للصوت
        Add light reverb to audio
        """
        if not SCIPY_AVAILABLE:
            return audio_path
        
        try:
            logger.info("إضافة صدى خفيف...")
            
            audio = AudioSegment.from_file(audio_path)
            samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
            
            # إنشاء مرشح صدى بسيط
            delay_samples = int(audio.frame_rate * 0.05)  # تأخير 50 مللي ثانية
            decay = room_size
            
            reverb_samples = np.zeros(len(samples) + delay_samples)
            reverb_samples[:len(samples)] = samples
            reverb_samples[delay_samples:] += samples * decay
            
            # قص إلى الطول الأصلي
            reverb_samples = reverb_samples[:len(samples)]
            
            # إعادة التطبيع
            reverb_samples = reverb_samples / np.max(np.abs(reverb_samples))
            reverb_samples = (reverb_samples * 32767).astype(np.int16)
            
            result = AudioSegment(
                reverb_samples.tobytes(),
                frame_rate=audio.frame_rate,
                sample_width=2,
                channels=audio.channels
            )
            
            base, ext = os.path.splitext(audio_path)
            output_path = f"{base}_reverb{ext}"
            result.export(output_path, format=ext[1:])
            
            return output_path
            
        except Exception as e:
            logger.error(f"خطأ في إضافة الصدى: {str(e)}")
            return audio_path


def enhance_audio(input_path: str, settings: dict = None) -> str:
    """
    وظيفة مساعدة لتحسين الصوت
    Helper function to enhance audio
    
    Args:
        input_path: مسار الملف الصوتي
        settings: إعدادات التحسين
        
    Returns:
        مسار الملف المحسن
    """
    enhancer = AudioEnhancer(settings)
    return enhancer.enhance(input_path)
