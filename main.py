# -*- coding: utf-8 -*-
"""
تطبيق ويب لتوليد فيديوهات الأحاديث النبوية
Hadith Video Generator Web Application
"""

import os
import sys
import logging
import requests
import shutil
import random
import re
import json
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ImageClip
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import numpy as np
import config

# إعداد نظام السجلات - Setup logging system
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('hadith_video_generator.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Import async routes
try:
    from async_routes import add_async_routes
    ASYNC_ROUTES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Async routes not available: {e}")
    ASYNC_ROUTES_AVAILABLE = False

# استيراد الوحدات الجديدة
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
        OpenAIImageGenerator, 
        StabilityImageGenerator,
        GeminiImageGenerator,
        OpenRouterImageGenerator,
        OllamaGenerator,
        VideoGenerator,
        PromptGenerator,
        LocalVideoGenerator,
        KlingVideoGenerator
    )
    AI_GENERATOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"مولدات AI غير متوفرة: {e}")
    AI_GENERATOR_AVAILABLE = False

# استيراد نظام إدارة الأداء
try:
    from performance_manager import (
        cache_manager,
        async_video_generator,
        bg_video_cache,
        AsyncVideoGenerator,
        BackgroundVideoCache
    )
    PERFORMANCE_MANAGER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"مدير الأداء غير متوفر: {e}")
    PERFORMANCE_MANAGER_AVAILABLE = False

# Fix for PIL.Image.ANTIALIAS deprecation in Pillow 10+
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

# إعداد التطبيق - Flask Application Setup
app = Flask(__name__)

# Add async routes if available
if ASYNC_ROUTES_AVAILABLE:
    add_async_routes(app)
    logger.info("تم تحميل المسارات غير المتزامنة بنجاح")
else:
    logger.warning("المسارات غير المتزامنة غير متوفرة")
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB max

# إعداد السجل - Logging Setup
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# إنشاء المجلدات المطلوبة - Create required folders
os.makedirs(config.TEMP_FOLDER, exist_ok=True)
os.makedirs(config.OUTPUT_FOLDER, exist_ok=True)


# ===========================
# وظائف مساعدة - Helper Functions
# ===========================

def clean_temp_folder():
    """تنظيف المجلد المؤقت - Clean temporary folder"""
    try:
        if os.path.exists(config.TEMP_FOLDER):
            for file in os.listdir(config.TEMP_FOLDER):
                file_path = os.path.join(config.TEMP_FOLDER, file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            logger.info("تم تنظيف المجلد المؤقت")
    except Exception as e:
        logger.error(f"خطأ في تنظيف المجلد المؤقت: {str(e)}")


def format_arabic_text(text):
    """تنسيق النص العربي للعرض الصحيح - Format Arabic text for proper display"""
    try:
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception as e:
        logger.error(f"خطأ في تنسيق النص العربي: {str(e)}")
        return text


# ===========================
# API Functions - وظائف التواصل مع APIs
# ===========================

def search_hadith(keyword):
    """
    البحث عن الأحاديث من موقع dorar.net
    Search for hadiths from dorar.net
    
    Args:
        keyword (str): الكلمة المفتاحية للبحث
        
    Returns:
        list: قائمة بالأحاديث المطابقة
    """
    try:
        logger.info(f"البحث عن الحديث: {keyword}")
        
        # استخدام JSONP callback كما في التوثيق
        # Using JSONP callback as per documentation
        url = f"{config.DORAR_API_URL}?skey={keyword}&callback=processDorar"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # معالجة JSONP response - استخراج JSON من callback
        # Process JSONP response - extract JSON from callback
        response_text = response.text
        
        # إزالة wrapper الخاص بـ JSONP للحصول على JSON النقي
        # Remove JSONP wrapper to get pure JSON
        # حسب الاختبار: API يرجع HTML داخل JSON
        # According to test: API returns HTML inside JSON
        
        # محاولة استخراج JSON من JSONP
        # Try to extract JSON from JSONP
        json_match = re.search(r'processDorar\((.*)\);?\s*$', response_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
            data = json.loads(json_str)
        else:
            # محاولة قراءته كـ JSON عادي في حال لم يكن JSONP
            try:
                data = response.json()
            except:
                logger.error(f"فشل في تحليل الاستجابة")
                return []
        
        # حسب الاختبار: data.ahadith.result يحتوي على HTML
        # According to test: data.ahadith.result contains HTML
        if 'ahadith' in data and isinstance(data['ahadith'], dict) and 'result' in data['ahadith']:
            html_content = data['ahadith']['result']
            
            if not html_content or not isinstance(html_content, str):
                logger.warning("محتوى HTML فارغ أو غير صحيح")
                return []
            
            logger.info("تم استلام محتوى HTML من API")
            
            # استخراج الأحاديث من HTML
            # Extract hadiths from HTML using regex
            hadiths = []
            
            # نمط محسّن لاستخراج الحديث مع معلوماته
            # البحث عن كل حديث مع div.hadith-info التالي له
            hadith_pattern = r'<div class="hadith"[^>]*>(.*?)</div>\s*<div class="hadith-info"[^>]*>(.*?)</div>'
            matches = re.findall(hadith_pattern, html_content, re.DOTALL)
            
            logger.info(f"تم العثور على {len(matches)} حديث كامل مع معلوماته")
            
            for idx, (hadith_html, info_html) in enumerate(matches[:10]):  # أول 10 فقط
                # إزالة HTML tags من نص الحديث
                clean_text = re.sub(r'<[^>]+>', '', hadith_html)
                clean_text = clean_text.strip()
                clean_text = re.sub(r'^\d+\s*-\s*', '', clean_text)  # إزالة الترقيم
                
                if not clean_text or len(clean_text) < 10:
                    continue
                
                # استخراج الراوي
                narrator = ""
                narrator_match = re.search(r'الراوي:\s*</span>\s*([^<\n]+)', info_html)
                if narrator_match:
                    narrator = narrator_match.group(1).strip()
                    if narrator == '-':
                        narrator = ""
                
                # استخراج المحدث/المصدر  
                source = ""
                source_match = re.search(r'المحدث:\s*</span>\s*([^<\n]+)', info_html)
                if source_match:
                    source = source_match.group(1).strip()
                
                # استخراج درجة الحديث - الدرجة موجودة داخل <span> بعد "خلاصة حكم المحدث:"
                grade = ""
                # النمط: خلاصة حكم المحدث:</span>  <span >الدرجة</span>
                grade_match = re.search(r'خلاصة حكم المحدث:</span>\s*<span[^>]*>([^<]+)</span>', info_html)
                if grade_match:
                    grade = grade_match.group(1).strip()
                    # تنظيف النص من الفراغات الزائدة
                    grade = ' '.join(grade.split())
                
                # استخراج رابط الشرح الكامل من موقع الدرر
                explanation_link = ""
                # البحث عن رابط الشرح في info_html
                link_match = re.search(r'href=["\']([^"\']*(?:hadith|sharh|explain)[^"\']*)["\']', info_html, re.IGNORECASE)
                if link_match:
                    explanation_link = link_match.group(1)
                    if not explanation_link.startswith('http'):
                        explanation_link = f"https://dorar.net{explanation_link}"
                else:
                    # إنشاء رابط بحث عن الحديث في الدرر
                    explanation_link = f"https://dorar.net/hadith/search?q={requests.utils.quote(clean_text[:50])}"
                
                hadiths.append({
                    'id': str(idx + 1),
                    'text': clean_text,
                    'narrator': narrator if narrator and narrator != '-' else '',
                    'source': source,
                    'grade': grade,
                    'explanation': '',
                    'explanation_link': explanation_link
                })
            
            if hadiths:
                logger.info(f"تم تنسيق {len(hadiths)} حديث بنجاح")
                return hadiths
            else:
                logger.warning("لم يتم استخراج أي أحاديث من HTML")
                return []
        else:
            logger.warning("تنسيق غير متوقع للبيانات من API")
            logger.debug(f"البيانات: {str(data)[:200]}")
            return []
            
    except requests.exceptions.RequestException as e:
        logger.error(f"خطأ في الاتصال بـ API: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"خطأ في تحليل JSON: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"خطأ في البحث عن الحديث: {str(e)}")
        return []


def download_background_video(query=None):
    """
    تحميل فيديو خلفية من Pexels أو توليده بالذكاء الاصطناعي
    Download background video from Pexels or generate with AI
    
    Args:
        query (str): نوع الفيديو المطلوب
        
    Returns:
        str: مسار الفيديو المحمل أو None
    """
    try:
        # محاولة توليد صورة بالذكاء الاصطناعي أولاً ثم تحويلها لفيديو
        if AI_GENERATOR_AVAILABLE:
            openai_gen = OpenAIImageGenerator()
            if openai_gen.is_available():
                logger.info("محاولة توليد صورة خلفية بالذكاء الاصطناعي...")
                prompt_gen = PromptGenerator()
                prompt = prompt_gen.generate_image_prompt("", query or 'nature')
                
                image_path = os.path.join(config.TEMP_FOLDER, 'ai_background.png')
                result = openai_gen.generate_image(prompt, image_path)
                
                if result:
                    # تحويل الصورة إلى فيديو بسيط
                    video_path = os.path.join(config.TEMP_FOLDER, 'background.mp4')
                    if _image_to_video(result, video_path, duration=30):
                        return video_path
        
        if not config.PEXELS_API_KEY or config.PEXELS_API_KEY == "YOUR_PEXELS_API_KEY_HERE":
            logger.error("مفتاح Pexels API غير موجود")
            return None
        
        # اختيار استعلام بحث عشوائي إذا لم يتم تحديده
        if not query:
            query = random.choice(config.PEXELS_SEARCH_QUERIES)
        
        logger.info(f"البحث عن فيديو خلفية: {query}")
        
        headers = {
            'Authorization': config.PEXELS_API_KEY
        }
        
        url = f"https://api.pexels.com/videos/search?query={query}&per_page=15"
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        if 'videos' in data and len(data['videos']) > 0:
            # اختيار فيديو عشوائي
            video = random.choice(data['videos'])
            
            # البحث عن أفضل جودة (1080p أو أعلى)
            video_url = None
            for file in video['video_files']:
                if file.get('quality') == 'hd' and file.get('width', 0) >= 1920:
                    video_url = file['link']
                    break
            
            # إذا لم يتم العثور على HD، استخدم أعلى جودة متاحة
            if not video_url and video['video_files']:
                video_url = video['video_files'][0]['link']
            
            if video_url:
                logger.info(f"تحميل الفيديو من: {video_url}")
                
                # تحميل الفيديو
                video_response = requests.get(video_url, stream=True, timeout=60)
                video_response.raise_for_status()
                
                video_path = os.path.join(config.TEMP_FOLDER, 'background.mp4')
                
                with open(video_path, 'wb') as f:
                    for chunk in video_response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                logger.info(f"تم تحميل الفيديو بنجاح: {video_path}")
                return video_path
        
        logger.warning("لم يتم العثور على فيديو مناسب")
        return None
        
    except Exception as e:
        logger.error(f"خطأ في تحميل فيديو الخلفية: {str(e)}")
        return None


def _image_to_video(image_path, output_path, duration=30):
    """
    تحويل صورة إلى فيديو مع تأثير Ken Burns
    Convert image to video with Ken Burns effect
    """
    try:
        from moviepy.editor import ImageClip
        
        # إنشاء مقطع من الصورة
        clip = ImageClip(image_path, duration=duration)
        
        # تغيير الحجم إلى دقة الفيديو
        clip = clip.resize((config.VIDEO_WIDTH, config.VIDEO_HEIGHT))
        
        # تطبيق تأثير Ken Burns (تكبير تدريجي)
        if VIDEO_ENHANCER_AVAILABLE:
            enhancer = VideoEnhancer(getattr(config, 'LOCAL_VIDEO_ENHANCEMENT', {}))
            advanced_settings = getattr(config, 'ADVANCED_VISUAL_EFFECTS', {})
            if advanced_settings.get('ken_burns', True):
                zoom = advanced_settings.get('ken_burns_zoom', 1.1)
                clip = enhancer.apply_ken_burns(clip, zoom)
        
        # حفظ الفيديو
        clip.write_videofile(
            output_path,
            fps=config.VIDEO_FPS,
            codec='libx264',
            audio=False,
            logger=None
        )
        
        clip.close()
        return True
        
    except Exception as e:
        logger.error(f"خطأ في تحويل الصورة إلى فيديو: {str(e)}")
        return False


# ===========================
# Video Processing - معالجة الفيديو
# ===========================

import asyncio
import edge_tts

def prepare_audio_text(hadith_data):
    """
    تحضير النص للقراءة الصوتية مع المعلومات الكاملة
    Prepare text for audio reading with complete information
    
    Args:
        hadith_data (dict): بيانات الحديث
        
    Returns:
        str: النص المُعد للقراءة
    """
    audio_settings = getattr(config, 'AUDIO_READING', {})
    
    parts = []
    
    # مقدمة الحديث
    intro = audio_settings.get('intro_text', 'قال رسول الله صلى الله عليه وسلم')
    parts.append(intro)
    
    # نص الحديث
    hadith_text = hadith_data.get('text', '').strip()
    if hadith_text:
        parts.append(hadith_text)
    
    # الراوي
    narrator = hadith_data.get('narrator', '').strip()
    if narrator and audio_settings.get('include_narrator', True):
        narrator_intro = audio_settings.get('narrator_intro', 'رواه')
        parts.append(f"{narrator_intro} {narrator}")
    
    # المحدث/المصدر
    source = hadith_data.get('source', '').strip()
    if source and audio_settings.get('include_source', True):
        parts.append(f"أخرجه {source}")
    
    # درجة الحديث
    grade = hadith_data.get('grade', '').strip()
    if grade and audio_settings.get('include_grade', True):
        grade_intro = audio_settings.get('grade_intro', 'والحديث')
        parts.append(f"{grade_intro} {grade}")
    
    # دمج الأجزاء مع فواصل طبيعية
    full_text = '. '.join(parts)
    
    return full_text


def generate_audio(text, output_path, hadith_data=None):
    """
    توليد ملف صوتي من النص بصوت رجولي واضح
    Generate audio file from text with clear male voice
    
    Args:
        text (str): النص المراد تحويله
        output_path (str): مسار حفظ الملف
        hadith_data (dict): بيانات الحديث الكاملة (اختياري)
        
    Returns:
        str: مسار الملف الصوتي أو None
    """
    try:
        logger.info("توليد الملف الصوتي بصوت رجولي واضح")
        
        # إذا تم تمرير بيانات الحديث، استخدم التحضير المحسن
        if hadith_data:
            text = prepare_audio_text(hadith_data)
            logger.info("تم تحضير النص مع معلومات الحديث الكاملة")
        
        # محاولة استخدام ElevenLabs أولاً
        if AI_GENERATOR_AVAILABLE:
            elevenlabs = ElevenLabsGenerator()
            if elevenlabs.is_available():
                logger.info("استخدام ElevenLabs لتوليد الصوت...")
                result = elevenlabs.generate_speech(text, output_path)
                if result:
                    # تحسين الصوت محلياً
                    if AUDIO_ENHANCER_AVAILABLE:
                        settings = getattr(config, 'LOCAL_AUDIO_ENHANCEMENT', {})
                        if settings.get('enabled', True):
                            logger.info("تحسين الصوت محلياً...")
                            result = enhance_audio(result, settings)
                    return result
        
        # استخدام Edge TTS للحصول على صوت رجولي عربي
        voice = getattr(config, 'EDGE_TTS_VOICE', 'ar-SA-HamedNeural')
        rate = getattr(config, 'EDGE_TTS_RATE', '-15%')
        pitch = getattr(config, 'EDGE_TTS_PITCH', '-2Hz')
        
        logger.info(f"إعدادات الصوت: Voice={voice}, Rate={rate}, Pitch={pitch}")
        
        async def _generate():
            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
            await communicate.save(output_path)
        
        # تشغيل الدالة المتزامنة
        asyncio.run(_generate())
        
        # تحسين الصوت محلياً
        if AUDIO_ENHANCER_AVAILABLE:
            settings = getattr(config, 'LOCAL_AUDIO_ENHANCEMENT', {})
            if settings.get('enabled', True):
                logger.info("تحسين الصوت محلياً...")
                output_path = enhance_audio(output_path, settings)
        
        logger.info(f"تم حفظ الملف الصوتي: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"خطأ في توليد الصوت بـ Edge TTS: {str(e)}")
        # الرجوع إلى gTTS كخيار احتياطي
        try:
            logger.info("استخدام gTTS كخيار احتياطي")
            tts = gTTS(text=text, lang=config.TTS_LANG, slow=config.TTS_SLOW)
            tts.save(output_path)
            logger.info(f"تم حفظ الملف الصوتي (gTTS): {output_path}")
            return output_path
        except Exception as e2:
            logger.error(f"خطأ في توليد الصوت: {str(e2)}")
            return None


def draw_rounded_rectangle(draw, coords, radius, fill):
    """
    رسم مستطيل بزوايا دائرية
    Draw rounded rectangle
    """
    x1, y1, x2, y2 = coords
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    draw.pieslice([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=fill)
    draw.pieslice([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=fill)
    draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=fill)


def draw_text_with_effects(draw, position, text, font, fill, shadow=True, outline=True):
    """
    رسم نص مع تأثيرات (ظل وحدود)
    Draw text with effects (shadow and outline)
    """
    x, y = position
    text_settings = getattr(config, 'TEXT_SETTINGS', {})
    
    # رسم الظل
    if shadow and text_settings.get('shadow_color'):
        shadow_offset = text_settings.get('shadow_offset', (3, 3))
        shadow_color = text_settings.get('shadow_color', (0, 0, 0, 180))
        draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font, fill=shadow_color)
    
    # رسم الحدود (outline)
    if outline and text_settings.get('outline_color'):
        outline_width = text_settings.get('outline_width', 2)
        outline_color = text_settings.get('outline_color', (0, 0, 0, 255))
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
    
    # رسم النص الأصلي
    draw.text((x, y), text, font=font, fill=fill)


def create_text_clip(text, duration, fontsize, position, color='white', bg_color=None):
    """
    إنشاء مقطع نصي للفيديو باستخدام PIL مع تأثيرات محسنة
    Create text clip for video using PIL with enhanced effects
    
    Args:
        text (str): النص
        duration (float): مدة العرض
        fontsize (int): حجم الخط
        position (tuple or str): موقع النص
        color (str): لون النص
        bg_color (str): لون الخلفية (اختياري)
        
    Returns:
        ImageClip: مقطع النص
    """
    try:
        # الحصول على إعدادات النص
        text_settings = getattr(config, 'TEXT_SETTINGS', {})
        video_effects = getattr(config, 'VIDEO_EFFECTS', {})
        
        # تنسيق النص العربي
        formatted_text = format_arabic_text(text)
        
        # إنشاء صورة للنص
        img_width = config.VIDEO_WIDTH - 150
        img_height = 600  # ارتفاع مؤقت أكبر
        
        # إنشاء صورة شفافة
        img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # تحميل الخط مع خيار احتياطي
        font = None
        font_paths = [
            config.FONT_PATH,
            getattr(config, 'FONT_PATH_BACKUP', 'static/fonts/NotoNaskhArabic-Bold.ttf'),
            getattr(config, 'FONT_PATH_FALLBACK', 'C:/Windows/Fonts/arial.ttf'),
            'C:/Windows/Fonts/tahoma.ttf'
        ]
        
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, fontsize)
                    logger.info(f"تم تحميل الخط: {font_path}")
                    break
            except Exception as font_error:
                logger.warning(f"فشل تحميل الخط {font_path}: {font_error}")
                continue
        
        if font is None:
            font = ImageFont.load_default()
            logger.warning("استخدام الخط الافتراضي")
        
        # تقسيم النص إلى أسطر
        max_chars_per_line = text_settings.get('max_chars_per_line', 28)
        words = formatted_text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars_per_line:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        # حساب ارتفاع النص الإجمالي
        line_spacing = text_settings.get('line_spacing', 1.4)
        line_height = int(fontsize * line_spacing)
        total_height = len(lines) * line_height
        
        # إعدادات الخلفية
        padding = text_settings.get('background_padding', 30)
        bg_opacity = text_settings.get('background_opacity', 180)
        bg_radius = text_settings.get('background_radius', 15)
        
        # رسم خلفية شبه شفافة للنص إذا طلبت
        if bg_color:
            bg_x1 = 50
            bg_y1 = 10
            bg_x2 = img_width - 50
            bg_y2 = total_height + padding * 2 + 10
            
            # رسم مستطيل بزوايا دائرية
            draw_rounded_rectangle(
                draw,
                (bg_x1, bg_y1, bg_x2, bg_y2),
                bg_radius,
                (0, 0, 0, bg_opacity)
            )
        
        # تحويل اللون إلى tuple
        if isinstance(color, str):
            if color.startswith('#'):
                color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5)) + (255,)
            elif color == 'white':
                color = (255, 255, 255, 255)
            elif color == 'gold' or color == 'yellow':
                color = (255, 215, 0, 255)
            else:
                color = (255, 255, 255, 255)
        
        # رسم كل سطر
        y_position = padding + 15
        use_shadow = video_effects.get('text_shadow', True)
        use_outline = video_effects.get('text_outline', True)
        
        for line in lines:
            # حساب عرض السطر للتوسيط
            try:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
            except:
                text_width = len(line) * (fontsize // 2)
            
            x_position = (img_width - text_width) // 2
            
            # رسم النص مع التأثيرات
            draw_text_with_effects(
                draw, 
                (x_position, y_position), 
                line, 
                font, 
                color,
                shadow=use_shadow,
                outline=use_outline
            )
            y_position += line_height
        
        # قص الصورة للحجم الفعلي
        final_height = total_height + padding * 2 + 30
        img = img.crop((0, 0, img_width, final_height))
        
        # تحويل إلى numpy array
        img_array = np.array(img)
        
        # إنشاء ImageClip
        img_clip = ImageClip(img_array, duration=duration, ismask=False)
        
        # تحديد الموقع
        img_clip = img_clip.set_position(position)
        
        return img_clip
        
    except Exception as e:
        logger.error(f"خطأ في إنشاء مقطع النص: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def create_hadith_video(hadith_data, background_video_path, audio_path, output_path):
    """
    إنشاء فيديو الحديث النهائي مع تصميم محسن ومنظم
    Create final hadith video with improved and organized design
    
    Args:
        hadith_data (dict): بيانات الحديث
        background_video_path (str): مسار فيديو الخلفية
        audio_path (str): مسار الملف الصوتي
        output_path (str): مسار حفظ الفيديو النهائي
        
    Returns:
        str: مسار الفيديو النهائي أو None
    """
    try:
        logger.info("بدء إنشاء فيديو الحديث بالتصميم المحسن")
        
        # تحميل فيديو الخلفية
        video_clip = VideoFileClip(background_video_path)
        
        # تحميل الملف الصوتي
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration
        
        # استخدام مدة الصوت فقط (بدون إضافة وقت إضافي لتجنب مشاكل المزامنة)
        final_duration = audio_duration
        
        logger.info(f"مدة الصوت: {audio_duration} ثانية")
        logger.info(f"مدة الفيديو الأصلي: {video_clip.duration} ثانية")
        
        if video_clip.duration < final_duration:
            # تكرار الفيديو إذا كان أقصر
            video_clip = video_clip.loop(duration=final_duration)
        else:
            video_clip = video_clip.subclip(0, final_duration)
        
        # تغيير حجم الفيديو
        logger.info("تغيير حجم الفيديو...")
        video_clip = video_clip.resize((config.VIDEO_WIDTH, config.VIDEO_HEIGHT))
        
        # إضافة تعتيم للخلفية لإبراز النص
        darken_value = getattr(config, 'VIDEO_EFFECTS', {}).get('darken_background', 0.55)
        
        # إنشاء طبقة تعتيم
        from moviepy.editor import ColorClip
        darken_layer = ColorClip(
            size=(config.VIDEO_WIDTH, config.VIDEO_HEIGHT),
            color=(0, 0, 0)
        ).set_opacity(darken_value).set_duration(final_duration)
        
        # دمج الخلفية مع طبقة التعتيم
        darkened_video = CompositeVideoClip([video_clip, darken_layer])
        
        # إضافة الصوت للفيديو - استخدام نفس المدة بالضبط
        logger.info("إضافة الصوت...")
        darkened_video = darkened_video.set_audio(audio_clip)
        darkened_video = darkened_video.set_duration(final_duration)
        
        # إنشاء النصوص
        clips = [darkened_video]
        
        # ========== نص الحديث (في المنتصف) ==========
        hadith_text = hadith_data.get('text', '')
        if hadith_text and len(hadith_text) > 10:
            logger.info("إضافة نص الحديث...")
            # تقصير النص إذا كان طويلاً جداً
            if len(hadith_text) > 400:
                hadith_text = hadith_text[:400] + "..."
            
            hadith_clip = create_hadith_text_clip(
                hadith_text,
                final_duration,
                config.HADITH_FONT_SIZE,
                'hadith'
            )
            if hadith_clip:
                clips.append(hadith_clip)
        
        # ========== معلومات الحديث (في الأسفل) ==========
        narrator = hadith_data.get('narrator', '').strip()
        source = hadith_data.get('source', '').strip()
        grade = hadith_data.get('grade', '').strip()
        
        hadith_display = getattr(config, 'HADITH_DISPLAY', {})
        
        # إنشاء شريط المعلومات السفلي
        info_clip = create_info_bar_clip(
            narrator=narrator,
            source=source,
            grade=grade,
            duration=final_duration,
            settings=hadith_display
        )
        if info_clip:
            clips.append(info_clip)
        
        # دمج جميع المقاطع
        logger.info("دمج المقاطع...")
        final_clip = CompositeVideoClip(clips, size=(config.VIDEO_WIDTH, config.VIDEO_HEIGHT))
        final_clip = final_clip.set_duration(final_duration)
        
        # تطبيق تأثيرات الظهور والاختفاء
        fade_duration = min(getattr(config, 'VIDEO_EFFECTS', {}).get('fade_duration', 2.0), final_duration / 4)
        final_clip = final_clip.fx(fadein, fade_duration)
        final_clip = final_clip.fx(fadeout, fade_duration)
        
        # حفظ الفيديو النهائي بجودة عالية
        logger.info(f"حفظ الفيديو النهائي: {output_path}")
        video_bitrate = getattr(config, 'VIDEO_BITRATE', '8000k')
        video_preset = getattr(config, 'VIDEO_PRESET', 'medium')
        final_clip.write_videofile(
            output_path,
            fps=config.VIDEO_FPS,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=os.path.join(config.TEMP_FOLDER, 'temp_audio.m4a'),
            remove_temp=True,
            threads=6,
            preset=video_preset,
            bitrate=video_bitrate,
            audio_bitrate='192k',
            logger=None
        )
        
        # إغلاق المقاطع
        logger.info("إغلاق المقاطع...")
        video_clip.close()
        audio_clip.close()
        final_clip.close()
        
        logger.info("✅ تم إنشاء الفيديو بنجاح")
        return output_path
        
    except Exception as e:
        logger.error(f"خطأ في إنشاء الفيديو: {str(e)}")
        import traceback
        logger.error(f"تفاصيل الخطأ:\n{traceback.format_exc()}")
        
        # محاولة إغلاق المقاطع في حالة الخطأ
        try:
            if 'video_clip' in locals():
                video_clip.close()
            if 'audio_clip' in locals():
                audio_clip.close()
            if 'final_clip' in locals():
                final_clip.close()
        except:
            pass
        
        return None


def create_hadith_text_clip(text, duration, fontsize, text_type='hadith'):
    """
    إنشاء مقطع نص الحديث بتصميم محسن
    Create hadith text clip with improved design
    """
    try:
        text_settings = getattr(config, 'TEXT_SETTINGS', {})
        video_effects = getattr(config, 'VIDEO_EFFECTS', {})
        
        # تنسيق النص العربي
        formatted_text = format_arabic_text(text)
        
        # حساب أبعاد الصورة
        img_width = config.VIDEO_WIDTH - 200
        img_height = 700
        
        # إنشاء صورة شفافة
        img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # تحميل الخط
        font = load_font(fontsize)
        
        # تقسيم النص إلى أسطر
        max_chars = text_settings.get('max_chars_per_line', 30)
        lines = split_text_to_lines(formatted_text, max_chars)
        
        # حساب الأبعاد
        line_spacing = text_settings.get('line_spacing', 1.9)
        line_height = int(fontsize * line_spacing)
        total_height = len(lines) * line_height
        
        # إعدادات الخلفية
        padding = text_settings.get('background_padding', 50)
        bg_opacity = text_settings.get('background_opacity', 210)
        bg_radius = text_settings.get('background_radius', 25)
        
        # رسم خلفية شبه شفافة
        bg_x1 = 30
        bg_y1 = 20
        bg_x2 = img_width - 30
        bg_y2 = total_height + padding * 2 + 20
        
        draw_rounded_rectangle(
            draw,
            (bg_x1, bg_y1, bg_x2, bg_y2),
            bg_radius,
            (20, 20, 40, bg_opacity)  # لون أزرق داكن شبه شفاف
        )
        
        # رسم حدود ذهبية للإطار
        draw_frame_border(draw, (bg_x1, bg_y1, bg_x2, bg_y2), bg_radius, (255, 215, 0, 180))
        
        # رسم النص
        y_position = padding + 30
        use_shadow = video_effects.get('text_shadow', True)
        use_outline = video_effects.get('text_outline', True)
        
        for line in lines:
            try:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
            except:
                text_width = len(line) * (fontsize // 2)
            
            x_position = (img_width - text_width) // 2
            
            draw_text_with_effects(
                draw, 
                (x_position, y_position), 
                line, 
                font, 
                (255, 255, 255, 255),
                shadow=use_shadow,
                outline=use_outline
            )
            y_position += line_height
        
        # قص الصورة للحجم الفعلي
        final_height = total_height + padding * 2 + 50
        img = img.crop((0, 0, img_width, final_height))
        
        # تحويل إلى ImageClip
        img_array = np.array(img)
        img_clip = ImageClip(img_array, duration=duration, ismask=False)
        
        # وضع النص في المنتصف
        img_clip = img_clip.set_position(('center', 'center'))
        
        return img_clip
        
    except Exception as e:
        logger.error(f"خطأ في إنشاء مقطع نص الحديث: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def create_info_bar_clip(narrator, source, grade, duration, settings):
    """
    إنشاء شريط المعلومات السفلي (الراوي، المحدث، درجة الصحة)
    Create bottom info bar (narrator, source, grade)
    """
    try:
        text_settings = getattr(config, 'TEXT_SETTINGS', {})
        info_colors = getattr(config, 'INFO_COLORS', {})
        grade_colors = getattr(config, 'GRADE_COLORS', {})
        
        # أبعاد الشريط
        bar_width = config.VIDEO_WIDTH - 100
        bar_height = 200
        
        img = Image.new('RGBA', (bar_width, bar_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # خط أصغر للمعلومات
        info_fontsize = getattr(config, 'RAWI_FONT_SIZE', 34)
        grade_fontsize = getattr(config, 'GRADE_FONT_SIZE', 36)
        
        info_font = load_font(info_fontsize)
        grade_font = load_font(grade_fontsize)
        
        # رسم خلفية الشريط
        draw_rounded_rectangle(
            draw,
            (10, 10, bar_width - 10, bar_height - 10),
            20,
            (0, 0, 0, 200)
        )
        
        y_offset = 30
        line_height = 55
        
        # عرض الراوي
        if narrator and settings.get('show_narrator', True):
            narrator_prefix = settings.get('narrator_prefix', 'الراوي')
            narrator_text = f"📜 {narrator_prefix}: {narrator}"
            formatted_narrator = format_arabic_text(narrator_text)
            
            try:
                bbox = draw.textbbox((0, 0), formatted_narrator, font=info_font)
                text_width = bbox[2] - bbox[0]
            except:
                text_width = len(formatted_narrator) * (info_fontsize // 2)
            
            x_pos = (bar_width - text_width) // 2
            
            # لون أزرق سماوي للراوي
            narrator_color = hex_to_rgba(info_colors.get('narrator', '#87CEEB'))
            draw_text_with_effects(draw, (x_pos, y_offset), formatted_narrator, info_font, narrator_color)
            y_offset += line_height
        
        # عرض المحدث
        if source and settings.get('show_source', True):
            source_prefix = settings.get('source_prefix', 'المحدث')
            source_text = f"📚 {source_prefix}: {source}"
            formatted_source = format_arabic_text(source_text)
            
            try:
                bbox = draw.textbbox((0, 0), formatted_source, font=info_font)
                text_width = bbox[2] - bbox[0]
            except:
                text_width = len(formatted_source) * (info_fontsize // 2)
            
            x_pos = (bar_width - text_width) // 2
            
            # لون أخضر فاتح للمصدر
            source_color = hex_to_rgba(info_colors.get('source', '#98FB98'))
            draw_text_with_effects(draw, (x_pos, y_offset), formatted_source, info_font, source_color)
            y_offset += line_height
        
        # عرض درجة الصحة بشكل بارز
        if grade and settings.get('show_grade', True):
            grade_prefix = settings.get('grade_prefix', 'الحكم')
            grade_text = f"⭐ {grade_prefix}: {grade}"
            formatted_grade = format_arabic_text(grade_text)
            
            try:
                bbox = draw.textbbox((0, 0), formatted_grade, font=grade_font)
                text_width = bbox[2] - bbox[0]
            except:
                text_width = len(formatted_grade) * (grade_fontsize // 2)
            
            x_pos = (bar_width - text_width) // 2
            
            # تحديد لون الدرجة حسب نوعها
            grade_color = get_grade_color(grade, grade_colors)
            draw_text_with_effects(draw, (x_pos, y_offset), formatted_grade, grade_font, grade_color, shadow=True, outline=True)
        
        # قص الصورة
        img = img.crop((0, 0, bar_width, y_offset + 50))
        
        # تحويل إلى ImageClip
        img_array = np.array(img)
        img_clip = ImageClip(img_array, duration=duration, ismask=False)
        
        # وضع الشريط في الأسفل
        img_clip = img_clip.set_position(('center', config.VIDEO_HEIGHT - img.height - 30))
        
        return img_clip
        
    except Exception as e:
        logger.error(f"خطأ في إنشاء شريط المعلومات: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def load_font(fontsize):
    """تحميل الخط مع خيارات احتياطية"""
    font_paths = [
        config.FONT_PATH,
        getattr(config, 'FONT_PATH_BACKUP', 'static/fonts/NotoNaskhArabic-Bold.ttf'),
        getattr(config, 'FONT_PATH_FALLBACK', 'C:/Windows/Fonts/arial.ttf'),
        'C:/Windows/Fonts/tahoma.ttf'
    ]
    
    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, fontsize)
        except Exception:
            continue
    
    logger.warning("استخدام الخط الافتراضي")
    return ImageFont.load_default()


def split_text_to_lines(text, max_chars):
    """تقسيم النص إلى أسطر"""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line) + len(word) + 1 <= max_chars:
            current_line += word + " "
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "
    
    if current_line:
        lines.append(current_line.strip())
    
    return lines


def hex_to_rgba(hex_color):
    """تحويل لون hex إلى RGBA"""
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b, 255)


def get_grade_color(grade, grade_colors):
    """الحصول على لون درجة الصحة"""
    if 'صحيح' in grade:
        return hex_to_rgba(grade_colors.get('صحيح', '#4CAF50'))
    elif 'حسن' in grade:
        return hex_to_rgba(grade_colors.get('حسن', '#FFC107'))
    elif 'ضعيف' in grade:
        return hex_to_rgba(grade_colors.get('ضعيف', '#FF5722'))
    elif 'موضوع' in grade:
        return hex_to_rgba(grade_colors.get('موضوع', '#9E9E9E'))
    else:
        return hex_to_rgba(grade_colors.get('default', '#2196F3'))


def draw_frame_border(draw, coords, radius, color):
    """رسم حدود الإطار"""
    x1, y1, x2, y2 = coords
    # رسم حدود بسيطة
    for i in range(3):
        draw.rounded_rectangle(
            [x1 + i, y1 + i, x2 - i, y2 - i],
            radius=radius,
            outline=color,
            width=1
        )


# ===========================
# Flask Routes - مسارات Flask
# ===========================

@app.route('/')
def index():
    """الصفحة الرئيسية - Home page"""
    return render_template('index.html')


@app.route('/api/search', methods=['POST'])
def api_search():
    """
    API للبحث عن الأحاديث مع معالجة أخطاء محسنة
    API endpoint for searching hadiths with improved error handling
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'لم يتم استلام بيانات صالحة',
                'hadiths': [],
                'count': 0
            }), 400
        
        keyword = data.get('keyword', '').strip()
        
        if not keyword:
            return jsonify({
                'success': False,
                'error': 'الرجاء إدخال كلمة مفتاحية للبحث',
                'hadiths': [],
                'count': 0
            }), 400
        
        if len(keyword) < 2:
            return jsonify({
                'success': False,
                'error': 'كلمة البحث قصيرة جداً، الرجاء إدخال حرفين على الأقل',
                'hadiths': [],
                'count': 0
            }), 400
        
        logger.info(f"البحث عن: {keyword}")
        hadiths = search_hadith(keyword)
        
        if not hadiths:
            return jsonify({
                'success': True,
                'hadiths': [],
                'count': 0,
                'message': 'لم يتم العثور على نتائج مطابقة'
            })
        
        return jsonify({
            'success': True,
            'hadiths': hadiths,
            'count': len(hadiths),
            'message': f'تم العثور على {len(hadiths)} حديث'
        })
        
    except json.JSONDecodeError:
        logger.error("خطأ في تحليل JSON")
        return jsonify({
            'success': False,
            'error': 'خطأ في البيانات المرسلة',
            'hadiths': [],
            'count': 0
        }), 400
    except Exception as e:
        logger.error(f"خطأ في API البحث: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'حدث خطأ في الخادم، الرجاء المحاولة مرة أخرى',
            'hadiths': [],
            'count': 0
        }), 500


@app.route('/api/generate', methods=['POST'])
def api_generate():
    """
    API لتوليد فيديو الحديث مع التحسينات الشاملة ومعالجة أخطاء محسنة
    API endpoint for generating hadith video with comprehensive improvements and better error handling
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'لم يتم استلام بيانات صالحة'
            }), 400
        
        hadith_data = data.get('hadith', {})
        video_type = data.get('video_type', None)
        use_ai_voice = data.get('use_ai_voice', True)
        use_ai_background = data.get('use_ai_background', False)
        enhance_locally = data.get('enhance_locally', True)
        custom_prompt = data.get('custom_prompt', '')
        
        if not hadith_data or not hadith_data.get('text'):
            return jsonify({
                'success': False,
                'error': 'بيانات الحديث غير صحيحة أو فارغة'
            }), 400
        
        # Validate hadith text length
        if len(hadith_data.get('text', '')) < 10:
            return jsonify({
                'success': False,
                'error': 'نص الحديث قصير جداً'
            }), 400
        
        logger.info(f"بدء توليد فيديو للحديث: {hadith_data.get('text', '')[:50]}...")
        
        # تنظيف المجلد المؤقت
        clean_temp_folder()
        
        # توليد الملف الصوتي مع المعلومات الكاملة
        audio_path = os.path.join(config.TEMP_FOLDER, 'audio.mp3')
        
        logger.info("توليد الملف الصوتي...")
        audio_result = generate_audio(None, audio_path, hadith_data=hadith_data)
        
        if not audio_result:
            return jsonify({
                'success': False,
                'error': 'فشل في توليد الصوت. الرجاء المحاولة مرة أخرى.'
            }), 500
        
        # تحميل فيديو الخلفية
        logger.info("تحميل فيديو الخلفية...")
        background_video = download_background_video(video_type)
        
        if not background_video:
            return jsonify({
                'success': False,
                'error': 'فشل في تحميل فيديو الخلفية. تحقق من اتصال الإنترنت.'
            }), 500
        
        # تحسين الفيديو محلياً (اختياري)
        if enhance_locally and VIDEO_ENHANCER_AVAILABLE:
            settings = getattr(config, 'LOCAL_VIDEO_ENHANCEMENT', {})
            if settings.get('enabled', True):
                logger.info("تحسين الفيديو محلياً...")
                enhanced_path = os.path.join(config.TEMP_FOLDER, 'background_enhanced.mp4')
                background_video = enhance_video(background_video, settings) or background_video
        
        # إنشاء الفيديو النهائي
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"hadith_video_{timestamp}.mp4"
        output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)
        
        logger.info("إنشاء الفيديو النهائي...")
        video_result = create_hadith_video(hadith_data, background_video, audio_path, output_path)
        
        if not video_result:
            return jsonify({
                'success': False,
                'error': 'فشل في إنشاء الفيديو النهائي. الرجاء المحاولة مرة أخرى.'
            }), 500
        
        # تنظيف الملفات المؤقتة
        clean_temp_folder()
        
        logger.info(f"✅ تم إنشاء الفيديو بنجاح: {output_filename}")
        
        return jsonify({
            'success': True,
            'video_path': output_filename,
            'message': 'تم إنشاء الفيديو بنجاح'
        })
        
    except MemoryError:
        logger.error("خطأ في الذاكرة أثناء توليد الفيديو")
        return jsonify({
            'success': False,
            'error': 'نفدت الذاكرة المتاحة. جرب فيديو بدقة أقل.'
        }), 500
    except Exception as e:
        logger.error(f"خطأ في API التوليد: {str(e)}")
        import traceback
        logger.error(f"تفاصيل الخطأ:\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': 'حدث خطأ أثناء إنشاء الفيديو. الرجاء المحاولة مرة أخرى.'
        }), 500


@app.route('/api/generate_prompt', methods=['POST'])
def api_generate_prompt():
    """
    API لتوليد أمر نصي (Prompt) للفيديو
    API endpoint for generating video prompt
    """
    try:
        data = request.get_json()
        hadith_text = data.get('hadith_text', '')
        style = data.get('style', 'islamic')
        
        if not AI_GENERATOR_AVAILABLE:
            return jsonify({'error': 'وحدة AI غير متوفرة'}), 500
        
        generator = PromptGenerator()
        prompt = generator.generate_video_prompt(hadith_text, style)
        
        return jsonify({
            'success': True,
            'prompt': prompt,
            'available_styles': generator.list_styles()
        })
        
    except Exception as e:
        logger.error(f"خطأ في توليد الأمر: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai_status', methods=['GET'])
def api_ai_status():
    """
    API للحصول على حالة خدمات الذكاء الاصطناعي
    API endpoint to get AI services status
    """
    try:
        status = {
            'elevenlabs': False,
            'openai_image': False,
            'stability': False,
            'gemini': False,
            'openrouter': False,
            'ollama': False,
            'kling': False,
            'veo': False,
            'video_gen': False,
            'local_video': True,
            'audio_enhancer': AUDIO_ENHANCER_AVAILABLE,
            'video_enhancer': VIDEO_ENHANCER_AVAILABLE
        }
        
        if AI_GENERATOR_AVAILABLE:
            # Voice
            elevenlabs = ElevenLabsGenerator()
            status['elevenlabs'] = elevenlabs.is_available()
            
            # Image Generation
            openai_gen = OpenAIImageGenerator()
            status['openai_image'] = openai_gen.is_available()
            
            stability_gen = StabilityImageGenerator()
            status['stability'] = stability_gen.is_available()
            
            gemini_gen = GeminiImageGenerator()
            status['gemini'] = gemini_gen.is_available()
            
            openrouter_gen = OpenRouterImageGenerator()
            status['openrouter'] = openrouter_gen.is_available()
            
            ollama_gen = OllamaGenerator()
            status['ollama'] = ollama_gen.is_available()
            
            # Video Generation
            video_gen = VideoGenerator()
            status['video_gen'] = video_gen.is_available()
            
            # Check specific video providers
            status['kling'] = bool(getattr(config, 'KLING_API_KEY', ''))
            status['veo'] = bool(getattr(config, 'VEO_API_KEY', '') or getattr(config, 'GEMINI_API_KEY', ''))
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"خطأ في جلب حالة AI: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def api_stats():
    """
    API للحصول على إحصائيات التطبيق
    API endpoint to get application statistics
    """
    try:
        # حساب عدد الفيديوهات المنشأة
        video_count = 0
        if os.path.exists(config.OUTPUT_FOLDER):
            for file in os.listdir(config.OUTPUT_FOLDER):
                if file.endswith('.mp4'):
                    video_count += 1
        
        return jsonify({
            'success': True,
            'total_videos': video_count
        })
        
    except Exception as e:
        logger.error(f"خطأ في جلب الإحصائيات: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate_ai_prompt', methods=['POST'])
def api_generate_ai_prompt():
    """
    API لتوليد أمر نصي احترافي باستخدام AI
    API endpoint for generating professional prompt using AI
    """
    try:
        data = request.get_json()
        description = data.get('description', '')
        style = data.get('style', 'cinematic')
        provider = data.get('provider', 'gemini')
        
        if not description:
            return jsonify({'error': 'الرجاء إدخال وصف'}), 400
        
        if not AI_GENERATOR_AVAILABLE:
            return jsonify({'error': 'وحدة AI غير متوفرة'}), 500
        
        # تحديد المزود
        prompt = ""
        if provider == 'gemini':
            gen = GeminiImageGenerator()
            if gen.is_available():
                prompt = gen.generate_prompt(description, style)
        elif provider == 'openrouter':
            gen = OpenRouterImageGenerator()
            if gen.is_available():
                prompt = gen.generate_prompt(description, style)
        elif provider == 'ollama':
            gen = OllamaGenerator()
            if gen.is_available():
                prompt = gen.generate_prompt(description, style)
        else:
            # استخدام PromptGenerator العام
            gen = PromptGenerator()
            prompt = gen.generate_ai_prompt(description, style)
        
        if not prompt:
            prompt = description
        
        return jsonify({
            'success': True,
            'prompt': prompt,
            'provider': provider
        })
        
    except Exception as e:
        logger.error(f"خطأ في توليد الأمر AI: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate_images', methods=['POST'])
def api_generate_images():
    """
    API لتوليد صور متعددة من أوامر نصية
    API endpoint for generating multiple images from prompts
    """
    try:
        data = request.get_json()
        prompts = data.get('prompts', [])
        provider = data.get('provider', 'openai')
        
        if not prompts:
            return jsonify({'error': 'الرجاء إدخال أوامر نصية'}), 400
        
        if not AI_GENERATOR_AVAILABLE:
            return jsonify({'error': 'وحدة AI غير متوفرة'}), 500
        
        generated_images = []
        
        for i, prompt in enumerate(prompts[:5]):  # أقصى 5 صور
            image_path = os.path.join(config.TEMP_FOLDER, f'generated_image_{i}.png')
            
            # استخدام مولد الصور حسب المزود
            result = None
            if provider == 'openai':
                openai_gen = OpenAIImageGenerator()
                if openai_gen.is_available():
                    result = openai_gen.generate_image(prompt, image_path)
            elif provider == 'stability':
                stability_gen = StabilityImageGenerator()
                if stability_gen.is_available():
                    result = stability_gen.generate_image(prompt, image_path)
            elif provider == 'gemini':
                gemini_gen = GeminiImageGenerator()
                if gemini_gen.is_available():
                    result = gemini_gen.generate_image(prompt, image_path)
            elif provider == 'openrouter':
                openrouter_gen = OpenRouterImageGenerator()
                if openrouter_gen.is_available():
                    result = openrouter_gen.generate_image(prompt, image_path)
            
            if result:
                generated_images.append(result)
        
        return jsonify({
            'success': True,
            'images': generated_images,
            'count': len(generated_images)
        })
        
    except Exception as e:
        logger.error(f"خطأ في توليد الصور: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate_local_video', methods=['POST'])
def api_generate_local_video():
    """
    API لتوليد فيديو محلياً من صور
    API endpoint for generating video locally from images
    """
    try:
        data = request.get_json()
        image_paths = data.get('image_paths', [])
        audio_path = data.get('audio_path', None)
        
        if not image_paths:
            return jsonify({'error': 'الرجاء تحديد مسارات الصور'}), 400
        
        # التحقق من وجود الصور
        valid_images = [p for p in image_paths if os.path.exists(p)]
        
        if not valid_images:
            return jsonify({'error': 'لم يتم العثور على صور صالحة'}), 400
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"local_video_{timestamp}.mp4"
        output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)
        
        if AI_GENERATOR_AVAILABLE:
            # استخدام مولد الفيديو المحلي
            local_gen = LocalVideoGenerator()
            result = local_gen.generate_from_images(valid_images, output_path, audio_path)
        else:
            return jsonify({'error': 'وحدة التوليد غير متوفرة'}), 500
        
        if result:
            return jsonify({
                'success': True,
                'video_path': output_filename,
                'message': 'تم توليد الفيديو بنجاح'
            })
        else:
            return jsonify({'error': 'فشل في توليد الفيديو'}), 500
        
    except Exception as e:
        logger.error(f"خطأ في توليد الفيديو المحلي: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/providers', methods=['GET'])
def api_get_providers():
    """
    API للحصول على قائمة المزودين المتاحين
    API endpoint to get available providers
    """
    try:
        providers = {
            'image': {
                'openai': {'name': 'OpenAI DALL-E', 'available': False},
                'stability': {'name': 'Stability AI', 'available': False},
                'gemini': {'name': 'Google Gemini', 'available': False},
                'openrouter': {'name': 'OpenRouter', 'available': False}
            },
            'video': {
                'local': {'name': 'Local (Ken Burns)', 'available': True},
                'runway': {'name': 'Runway ML', 'available': False},
                'pika': {'name': 'Pika Labs', 'available': False},
                'kling': {'name': 'Kling AI', 'available': False},
                'veo': {'name': 'Google Veo', 'available': False},
                'replicate': {'name': 'Replicate', 'available': False}
            },
            'voice': {
                'edge_tts': {'name': 'Edge TTS', 'available': True},
                'elevenlabs': {'name': 'ElevenLabs', 'available': False}
            },
            'prompt': {
                'local': {'name': 'Local Templates', 'available': True},
                'gemini': {'name': 'Gemini AI', 'available': False},
                'openrouter': {'name': 'OpenRouter', 'available': False},
                'ollama': {'name': 'Ollama (Local)', 'available': False}
            }
        }
        
        if AI_GENERATOR_AVAILABLE:
            # Image providers
            providers['image']['openai']['available'] = OpenAIImageGenerator().is_available()
            providers['image']['stability']['available'] = StabilityImageGenerator().is_available()
            providers['image']['gemini']['available'] = GeminiImageGenerator().is_available()
            providers['image']['openrouter']['available'] = OpenRouterImageGenerator().is_available()
            
            # Video providers
            providers['video']['runway']['available'] = bool(getattr(config, 'RUNWAY_API_KEY', ''))
            providers['video']['pika']['available'] = bool(getattr(config, 'PIKA_API_KEY', ''))
            providers['video']['kling']['available'] = bool(getattr(config, 'KLING_API_KEY', ''))
            providers['video']['veo']['available'] = bool(getattr(config, 'GEMINI_API_KEY', ''))
            providers['video']['replicate']['available'] = bool(getattr(config, 'REPLICATE_API_KEY', ''))
            
            # Voice providers
            providers['voice']['elevenlabs']['available'] = ElevenLabsGenerator().is_available()
            
            # Prompt providers
            providers['prompt']['gemini']['available'] = GeminiImageGenerator().is_available()
            providers['prompt']['openrouter']['available'] = OpenRouterImageGenerator().is_available()
            providers['prompt']['ollama']['available'] = OllamaGenerator().is_available()
        
        return jsonify({
            'success': True,
            'providers': providers
        })
        
    except Exception as e:
        logger.error(f"خطأ في جلب المزودين: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings', methods=['GET'])
def api_get_settings():
    """
    API للحصول على الإعدادات الحالية
    API endpoint to get current settings
    """
    try:
        settings = {
            'video': {
                'width': config.VIDEO_WIDTH,
                'height': config.VIDEO_HEIGHT,
                'fps': config.VIDEO_FPS,
                'bitrate': config.VIDEO_BITRATE
            },
            'audio_enhancement': getattr(config, 'LOCAL_AUDIO_ENHANCEMENT', {}),
            'video_enhancement': getattr(config, 'LOCAL_VIDEO_ENHANCEMENT', {}),
            'visual_effects': getattr(config, 'ADVANCED_VISUAL_EFFECTS', {}),
            'prompt_templates': getattr(config, 'PROMPT_TEMPLATES', {}),
            'available_voices': ['ar-SA-HamedNeural', 'ar-EG-ShakirNeural', 'ar-AE-HamdanNeural']
        }
        
        return jsonify({
            'success': True,
            'settings': settings
        })
        
    except Exception as e:
        logger.error(f"خطأ في جلب الإعدادات: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<filename>')
def api_download(filename):
    """
    API لتحميل الفيديو
    API endpoint for downloading video
    """
    try:
        file_path = os.path.join(config.OUTPUT_FOLDER, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'الملف غير موجود'}), 404
        
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"خطأ في تحميل الفيديو: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/preview/<filename>')
def api_preview(filename):
    """
    API لمعاينة الفيديو
    API endpoint for video preview
    """
    try:
        file_path = os.path.join(config.OUTPUT_FOLDER, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'الملف غير موجود'}), 404
        
        return send_file(file_path, mimetype='video/mp4')
        
    except Exception as e:
        logger.error(f"خطأ في معاينة الفيديو: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ===========================
# Main - التشغيل الرئيسي
# ===========================

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("تطبيق توليد فيديوهات الأحاديث النبوية")
    logger.info("Hadith Video Generator Application")
    logger.info("=" * 50)
    
    # التحقق من مفتاح API
    if config.PEXELS_API_KEY == "YOUR_PEXELS_API_KEY_HERE":
        logger.warning("تحذير: لم يتم تعيين مفتاح Pexels API")
        logger.warning("الرجاء تعديل ملف config.py وإضافة مفتاح API")
    
    # تشغيل التطبيق
    app.run(debug=True, host='0.0.0.0', port=5000)
