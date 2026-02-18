# -*- coding: utf-8 -*-
"""
ملف الإعدادات للتطبيق
Configuration file for the application
"""

# مفاتيح API - API Keys
# احصل على مفتاح Pexels من: https://www.pexels.com/api/
PEXELS_API_KEY = "fnJ1eGXKTKTHr7yb7lLZC7J8SUR70d5Y8R7gOHWI9DsLQ3YDM0BvQVgG"
DORAR_API_URL = "https://dorar.net/dorar_api.json"

# ===========================
# ElevenLabs API - توليد الصوت بالذكاء الاصطناعي
# ===========================
# احصل على مفتاح ElevenLabs من: https://elevenlabs.io/
ELEVENLABS_API_KEY = "sk_1e6c3bb3952547d4ed41e2ff170e27cc6beba89188055d8b"  # أضف مفتاحك هنا
ELEVENLABS_VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # Adam - صوت عربي واضح
ELEVENLABS_MODEL_ID = "eleven_multilingual_v2"  # أفضل نموذج للغة العربية
ELEVENLABS_SETTINGS = {
    'stability': 0.5,           # استقرار الصوت (0.0-1.0)
    'similarity_boost': 0.75,   # وضوح الصوت (0.0-1.0)
    'style': 0.5,               # أسلوب التعبير (0.0-1.0)
    'use_speaker_boost': True   # تحسين جودة الصوت
}

# ===========================
# Image Generation API - توليد الصور بالذكاء الاصطناعي
# ===========================
# OpenAI DALL-E: https://platform.openai.com/
OPENAI_API_KEY = ""  # مفتاح OpenAI لتوليد الصور
IMAGE_GEN_PROVIDER = "openai"  # openai, stability, replicate, gemini, openrouter
IMAGE_GEN_MODEL = "dall-e-3"  # نموذج توليد الصور
IMAGE_GEN_SIZE = "1792x1024"  # حجم الصورة (1024x1024, 1792x1024, 1024x1792)
IMAGE_GEN_QUALITY = "hd"  # standard أو hd
IMAGE_GEN_STYLE = "natural"  # natural أو vivid

# Stability AI: https://platform.stability.ai/
STABILITY_API_KEY = "sk_1e6c3bb3952547d4ed41e2ff170e27cc6beba89188055d8b"  # مفتاح Stability AI
STABILITY_MODEL = "stable-diffusion-xl-1024-v1-0"

# Google Gemini: https://ai.google.dev/
GEMINI_API_KEY = ""  # مفتاح Google Gemini
GEMINI_IMAGE_MODEL = "gemini-2.0-flash-exp"  # نموذج توليد الصور من Gemini

# OpenRouter: https://openrouter.ai/
OPENROUTER_API_KEY = ""  # مفتاح OpenRouter
OPENROUTER_IMAGE_MODEL = "nvidia/nemotron-nano-12b-v2-vl:free"  # نموذج الصور عبر OpenRouter

# Ollama (Local): https://ollama.ai/
OLLAMA_HOST = "http://localhost:11434"  # عنوان Ollama المحلي
OLLAMA_MODEL = "llava"  # نموذج Ollama للصور

# ===========================
# Video Generation API - توليد الفيديو بالذكاء الاصطناعي
# ===========================
# Runway ML: https://runwayml.com/
RUNWAY_API_KEY = "sk_1e6c3bb3952547d4ed41e2ff170e27cc6beba89188055d8b"  # مفتاح Runway ML لتوليد الفيديو
VIDEO_GEN_PROVIDER = "kling"  # local, runway, pika, kling, veo, replicate

# Pika Labs: https://pika.art/
PIKA_API_KEY = "sk_1e6c3bb3952547d4ed41e2ff170e27cc6beba89188055d8b"  # مفتاح Pika Labs

# Replicate: https://replicate.com/
REPLICATE_API_KEY = "r8_QYHL1JnX8Q7N2ykfmZrLyePjKqFh3KW4Sh"  # مفتاح Replicate

# Kling AI: https://klingai.com/ (Enhanced KIE API)
KLING_API_KEY = "sk_kie_1e6c3bb3952547d4ed41e2ff170e27cc6beba89188055d8b"  # مفتاح Kling AI
KLING_ACCESS_KEY = "ARG44Fa9rkhJ3fD99LyEJ3TbkJ3b8dPy"  # مفتاح الوصول لـ Kling
KLING_SECRET_KEY = "LQHefdhnh3CTRRkyMyHDFy3Q4PmPBA9b"  # المفتاح السري لـ Kling

# Google Veo (Gemini Video): https://deepmind.google/technologies/veo/
VEO_API_KEY = "AIzaSyDxk3n_2U_85y1TnTdHfcAwKySFMI2r40E"  # يستخدم نفس مفتاح Gemini
VEO_MODEL = "veo-001"  # نموذج Veo لتوليد الفيديو

# إعدادات توليد الفيديو بالذكاء الاصطناعي
AI_VIDEO_SETTINGS = {
    'duration': 4,              # مدة الفيديو بالثواني
    'fps': 24,                  # عدد الإطارات في الثانية
    'motion_strength': 0.7,     # قوة الحركة (0.0-1.0)
    'guidance_scale': 7.5,      # مقياس التوجيه
    'max_parallel_jobs': 3,     # عدد المهام المتوازية
    'use_gpu_acceleration': True, # استخدام تسريع GPU
    'cache_enabled': True,      # تفعيل التخزين المؤقت
    'cache_duration': 3600,     # مدة التخزين المؤقت (ثانية)
    'async_processing': True,   # المعالجة غير المتزامنة
    'quality_preset': 'balanced', # balanced, fast, high_quality
}

# Performance Optimization
PERFORMANCE_SETTINGS = {
    'max_concurrent_requests': 5,
    'request_timeout': 120,
    'retry_attempts': 3,
    'retry_delay': 2,
    'enable_compression': True,
    'memory_limit_mb': 2048,
}

# ===========================
# AI Prompt Generation - توليد الأوامر بالذكاء الاصطناعي
# ===========================
# استخدام AI لتوليد أوامر نصية احترافية للصور والفيديو
PROMPT_GEN_PROVIDER = "gemini"  # gemini, openai, openrouter, ollama
PROMPT_GEN_SETTINGS = {
    'language': 'en',           # لغة الأوامر المولدة (en أفضل للصور)
    'detail_level': 'high',     # مستوى التفاصيل (low, medium, high)
    'include_style': True,      # إضافة وصف الأسلوب
    'include_lighting': True,   # إضافة وصف الإضاءة
    'include_camera': True,     # إضافة وصف زاوية الكاميرا
}

# ===========================
# Local Video Generation - توليد الفيديو محلياً من الصور
# ===========================
LOCAL_VIDEO_FROM_IMAGES = {
    'enabled': True,                    # تفعيل التوليد المحلي
    'transition_duration': 1.5,         # مدة الانتقال بين الصور (ثواني)
    'image_duration': 4.0,              # مدة عرض كل صورة (ثواني)
    'transition_type': 'crossfade',     # نوع الانتقال (crossfade, fade, slide, zoom)
    'ken_burns_enabled': True,          # تأثير Ken Burns
    'ken_burns_zoom': 1.15,             # نسبة التكبير
    'pan_direction': 'random',          # اتجاه التحريك (left, right, up, down, random)
    'add_motion_blur': False,           # إضافة ضبابية الحركة
    'fps': 30,                          # عدد الإطارات في الثانية
    'resolution': '1080p',              # الدقة (720p, 1080p, 4k)
}

# ===========================
# Prompt Generation - توليد الأوامر النصية للفيديو
# ===========================
PROMPT_TEMPLATES = {
    'islamic': "خلفية إسلامية هادئة مع زخارف عربية، مسجد في الخلفية، ألوان دافئة، أجواء روحانية، 4K جودة عالية",
    'nature': "طبيعة خلابة هادئة، سماء صافية، أشجار خضراء، انعكاس على الماء، إضاءة ذهبية، فيديو سينمائي",
    'desert': "صحراء ذهبية عند الغروب، كثبان رملية ناعمة، سماء برتقالية، أجواء هادئة، جودة 4K",
    'sky': "سماء ليلية مليئة بالنجوم، مجرة درب التبانة، أضواء شمالية، مشهد ساحر، فيديو 4K",
    'ocean': "محيط هادئ عند الفجر، أمواج لطيفة، انعكاس السماء على الماء، ألوان باستيل، سينمائي",
    'mountains': "جبال شاهقة مغطاة بالثلوج، ضباب خفيف، إضاءة ذهبية، طبيعة خلابة، 4K"
}

# إعدادات توليد الأوامر التلقائية
AUTO_PROMPT_SETTINGS = {
    'include_quality': True,        # إضافة وصف الجودة
    'include_style': True,          # إضافة وصف الأسلوب
    'include_mood': True,           # إضافة وصف المزاج
    'default_quality': '4K, جودة عالية, سينمائي',
    'default_style': 'احترافي, إضاءة طبيعية',
    'default_mood': 'هادئ, روحاني, ملهم'
}

# ===========================
# Local Audio Enhancement - تحسين الصوت محلياً
# ===========================
LOCAL_AUDIO_ENHANCEMENT = {
    'enabled': True,                    # تفعيل التحسين المحلي
    'noise_reduction': True,            # إزالة الضوضاء
    'noise_reduction_strength': 0.7,    # قوة إزالة الضوضاء (0.0-1.0)
    'normalize': True,                  # تطبيع مستوى الصوت
    'target_loudness': -16.0,           # مستوى الصوت المستهدف (LUFS)
    'compressor': True,                 # ضغط النطاق الديناميكي
    'compressor_threshold': -20,        # عتبة الضغط (dB)
    'compressor_ratio': 4,              # نسبة الضغط
    'equalizer': True,                  # معادل الصوت
    'eq_settings': {
        'low_shelf': {'freq': 100, 'gain': 2},      # تعزيز الترددات المنخفضة
        'mid': {'freq': 1000, 'gain': 1},           # تعزيز الترددات المتوسطة
        'high_shelf': {'freq': 8000, 'gain': 1.5}   # تعزيز الترددات العالية
    },
    'reverb': False,                    # إضافة صدى خفيف
    'reverb_room_size': 0.3,           # حجم الغرفة للصدى
    'fade_in': 0.5,                     # تلاشي الدخول (ثواني)
    'fade_out': 0.5                     # تلاشي الخروج (ثواني)
}

# ===========================
# Local Video Enhancement - تحسين الفيديو محلياً
# ===========================
LOCAL_VIDEO_ENHANCEMENT = {
    'enabled': True,                    # تفعيل التحسين المحلي
    'stabilization': True,              # تثبيت الفيديو
    'color_correction': True,           # تصحيح الألوان
    'brightness': 1.05,                 # سطوع (1.0 = طبيعي)
    'contrast': 1.1,                    # تباين (1.0 = طبيعي)
    'saturation': 1.15,                 # تشبع الألوان (1.0 = طبيعي)
    'sharpening': True,                 # زيادة الحدة
    'sharpening_strength': 1.3,         # قوة الحدة
    'denoise': True,                    # إزالة التشويش
    'denoise_strength': 3,              # قوة إزالة التشويش
    'vignette': True,                   # تأثير التظليل الدائري
    'vignette_strength': 0.3,           # قوة التظليل
    'film_grain': False,                # تأثير حبيبات الفيلم
    'film_grain_strength': 0.1,         # قوة حبيبات الفيلم
    'letterbox': False,                 # إضافة شريط سينمائي
    'letterbox_ratio': 2.35             # نسبة العرض السينمائية
}

# ===========================
# Visual Effects - تأثيرات بصرية متقدمة
# ===========================
ADVANCED_VISUAL_EFFECTS = {
    'ken_burns': True,                  # تأثير Ken Burns (تكبير وتحريك)
    'ken_burns_zoom': 1.1,              # نسبة التكبير
    'parallax': False,                  # تأثير العمق
    'light_leaks': False,               # تسرب الضوء
    'bokeh': False,                     # تأثير البوكيه
    'glow': True,                       # توهج خفيف
    'glow_strength': 0.2,               # قوة التوهج
    'color_grading': True,              # تدريج الألوان السينمائي
    'lut_file': '',                     # ملف LUT للألوان (اختياري)
    'cinematic_bars': False,            # أشرطة سينمائية
    'motion_blur': False,               # ضبابية الحركة
    'slow_motion': False,               # حركة بطيئة
    'slow_motion_factor': 0.5           # معامل البطء
}

# إعدادات الفيديو - Video Settings
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 24  # أقل لسرعة أفضل
VIDEO_BITRATE = '8000k'  # جودة عالية
VIDEO_PRESET = 'medium'  # جودة أفضل

# إعدادات النصوص - Text Settings
# خط Noto Sans Arabic Bold - يدعم جميع الحروف العربية والرموز
FONT_PATH = "static/fonts/NotoSansArabic-Bold.ttf"
FONT_PATH_BACKUP = "static/fonts/NotoNaskhArabic-Bold.ttf"  # خط احتياطي
FONT_PATH_FALLBACK = "C:/Windows/Fonts/arial.ttf"  # خط أخير
HADITH_FONT_SIZE = 52  # حجم أكبر للقراءة الواضحة
TITLE_FONT_SIZE = 38  # حجم العناوين (الراوي، المحدث)
RAWI_FONT_SIZE = 34   # حجم معلومات الراوي
GRADE_FONT_SIZE = 36  # حجم درجة الصحة

# ألوان درجات الصحة - Authenticity Grade Colors
GRADE_COLORS = {
    'صحيح': '#4CAF50',      # أخضر زاهي - Bright Green
    'حسن': '#FFC107',        # ذهبي - Gold
    'ضعيف': '#FF5722',       # برتقالي أحمر - Orange Red
    'موضوع': '#9E9E9E',      # رمادي - Gray
    'default': '#2196F3'     # أزرق افتراضي - Default Blue
}

# ألوان العناوين والمعلومات - Title and Info Colors
INFO_COLORS = {
    'title': '#FFD700',       # ذهبي للعناوين
    'narrator': '#87CEEB',    # أزرق سماوي للراوي
    'source': '#98FB98',      # أخضر فاتح للمصدر
    'grade_label': '#FFFFFF'  # أبيض لعنوان الدرجة
}

# إعدادات الصوت المحسنة - Enhanced Audio Settings
TTS_LANG = 'ar'
TTS_SLOW = False
# صوت رجولي عربي من Edge TTS - إعدادات محسنة
# الأصوات المتاحة: 
# ar-SA-HamedNeural (سعودي رجولي - واضح جداً)
# ar-EG-ShakirNeural (مصري رجولي - طبيعي)
# ar-AE-HamdanNeural (إماراتي رجولي)
EDGE_TTS_VOICE = 'ar-SA-HamedNeural'  # صوت سعودي واضح جداً
EDGE_TTS_RATE = '-15%'  # أبطأ للوضوح والفهم
EDGE_TTS_PITCH = '-2Hz'  # طبقة طبيعية

# إعدادات البحث في Pexels - Pexels Search Settings
PEXELS_SEARCH_QUERIES = [
    'nature calm',
    'mountains peaceful',
    'ocean sunset',
    'forest trees',
    'clouds sky',
    'desert landscape',
    'mosque islamic',
    'stars night sky',
    'water reflection'
]

# إعدادات الموسيقى الخلفية - Background Music Settings
PEXELS_MUSIC_QUERIES = [
    'peaceful ambient',
    'meditation calm',
    'nature sounds',
    'relaxing piano'
]

# إعدادات تأثيرات الفيديو - Video Effects Settings
VIDEO_EFFECTS = {
    'fade_duration': 2.0,        # مدة تأثير الظهور/الاختفاء أطول
    'text_shadow': True,          # إضافة ظل للنص
    'text_outline': True,         # إضافة حدود للنص
    'darken_background': 0.55,    # تعتيم الخلفية
    'blur_background': False,     # تأثير ضبابي للخلفية
}

# إعدادات النص المحسنة - Enhanced Text Settings
TEXT_SETTINGS = {
    'shadow_color': (0, 0, 0, 230),      # لون الظل أغمق
    'shadow_offset': (5, 5),              # إزاحة الظل
    'outline_color': (0, 0, 0, 255),     # لون الحدود
    'outline_width': 4,                   # عرض الحدود أكبر
    'line_spacing': 1.9,                  # تباعد أكبر بين الأسطر
    'max_chars_per_line': 30,             # أحرف مناسبة للقراءة
    'background_padding': 50,             # حشو الخلفية
    'background_opacity': 210,            # شفافية الخلفية أغمق
    'background_radius': 25,              # زوايا الخلفية
}

# إعدادات عرض معلومات الحديث - Hadith Info Display Settings
HADITH_DISPLAY = {
    'show_narrator': True,        # عرض الراوي
    'show_source': True,          # عرض المحدث/المصدر
    'show_grade': True,           # عرض درجة الصحة
    'narrator_prefix': 'الراوي',   # نص قبل اسم الراوي
    'source_prefix': 'المحدث',     # نص قبل اسم المحدث
    'grade_prefix': 'الحكم',       # نص قبل درجة الصحة
    'info_separator': ' - ',       # فاصل بين المعلومات
}

# إعدادات قراءة الصوت - Audio Reading Settings
AUDIO_READING = {
    'include_narrator': True,     # قراءة اسم الراوي
    'include_source': True,       # قراءة المحدث
    'include_grade': True,        # قراءة درجة الصحة
    'intro_text': 'قال رسول الله صلى الله عليه وسلم',  # مقدمة الحديث
    'narrator_intro': 'رواه',      # مقدمة الراوي
    'grade_intro': 'والحديث',      # مقدمة الحكم
    'pause_duration': 0.8,        # مدة الوقفة بين الأجزاء (ثانية)
}

# إعدادات المجلدات - Folder Settings
TEMP_FOLDER = 'temp'
OUTPUT_FOLDER = 'outputs'

# إعدادات السجل - Logging Settings
LOG_FILE = 'hadith_video_generator.log'
LOG_LEVEL = 'INFO'
