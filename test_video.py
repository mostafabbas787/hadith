#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اختبار توليد الفيديو - Video Generation Test
"""

import sys
import os
import io

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import search_hadith, generate_audio, download_background_video, create_hadith_video
import config

def test_video_generation():
    """اختبار توليد فيديو كامل"""
    print("=" * 60)
    print("🎬 اختبار توليد الفيديو")
    print("=" * 60)
    
    # 1. البحث عن حديث
    print("\n📝 الخطوة 1: البحث عن حديث...")
    hadiths = search_hadith("الصدق")
    
    if not hadiths:
        print("❌ فشل البحث")
        return False
    
    hadith = hadiths[0]
    print(f"✅ تم اختيار الحديث: {hadith['text'][:50]}...")
    print(f"   الدرجة: {hadith.get('grade', 'غير متوفر')}")
    
    # 2. توليد الصوت
    print("\n🔊 الخطوة 2: توليد الصوت...")
    audio_path = os.path.join(config.TEMP_FOLDER, 'test_audio.mp3')
    try:
        result = generate_audio(hadith['text'][:200], audio_path)
        if result:
            print(f"✅ تم توليد الصوت: {audio_path}")
        else:
            print("❌ فشل توليد الصوت")
            return False
    except Exception as e:
        print(f"❌ خطأ في توليد الصوت: {e}")
        return False
    
    # 3. تحميل فيديو الخلفية
    print("\n🎥 الخطوة 3: تحميل فيديو الخلفية...")
    try:
        bg_video = download_background_video()
        if bg_video:
            print(f"✅ تم تحميل الفيديو: {bg_video}")
        else:
            print("❌ فشل تحميل فيديو الخلفية")
            return False
    except Exception as e:
        print(f"❌ خطأ في تحميل الفيديو: {e}")
        return False
    
    # 4. إنشاء الفيديو النهائي
    print("\n🎬 الخطوة 4: إنشاء الفيديو النهائي...")
    output_path = os.path.join(config.OUTPUT_FOLDER, 'test_video.mp4')
    try:
        result = create_hadith_video(hadith, bg_video, audio_path, output_path)
        if result:
            print(f"✅ تم إنشاء الفيديو: {result}")
            return True
        else:
            print("❌ فشل إنشاء الفيديو")
            return False
    except Exception as e:
        print(f"❌ خطأ في إنشاء الفيديو: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_video_generation()
        print("\n" + "=" * 60)
        if success:
            print("✅ اختبار توليد الفيديو ناجح!")
        else:
            print("❌ فشل اختبار توليد الفيديو")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ خطأ عام: {e}")
        import traceback
        traceback.print_exc()
