#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اختبار بسيط لتوليد صورة مع نص عربي
"""

from PIL import Image, ImageDraw, ImageFont
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import os

def test_arabic_text():
    """Test Arabic text rendering with different examples"""
    
    font_path = 'static/fonts/NotoSansArabic-Bold.ttf'
    if not os.path.exists(font_path):
        print(f"ERROR: Font not found: {font_path}")
        return False
    
    # Test texts - same as what appears in videos
    test_cases = [
        # Hadith text
        'إياكم والكذبَ فإن الكذبَ يهدي إلى الفجورِ',
        # Rawi and grade with dash separator
        'أبو هريرة - صحيح البخاري - إسناده صحيح',
        # Simple Arabic
        'بسم الله الرحمن الرحيم',
        # Mixed with numbers
        'حديث رقم 123',
    ]
    
    # Create test image
    img_width = 1080
    img_height = 600
    img = Image.new('RGBA', (img_width, img_height), (30, 30, 60, 255))
    draw = ImageDraw.Draw(img)
    
    # Load font
    font = ImageFont.truetype(font_path, 42)
    
    y = 50
    for i, text in enumerate(test_cases):
        # Process Arabic text
        reshaped = reshape(text)
        bidi_text = get_display(reshaped)
        
        # Draw shadow first
        draw.text((img_width//2 + 3, y + 3), bidi_text, font=font, fill=(0, 0, 0, 180), anchor='mt')
        # Draw text
        draw.text((img_width//2, y), bidi_text, font=font, fill=(255, 255, 255, 255), anchor='mt')
        
        y += 100
        print(f"✅ Rendered: {text[:50]}...")
    
    # Add info
    info_font = ImageFont.truetype(font_path, 24)
    info_text = "Font: NotoSansArabic-Bold.ttf - Separator: dash (-)"
    draw.text((img_width//2, img_height - 50), info_text, font=info_font, fill=(200, 200, 200, 255), anchor='mt')
    
    # Save
    output_path = 'temp/arabic_text_test.png'
    img.save(output_path)
    print(f"\n✅ Test image saved: {output_path}")
    print(f"   Size: {img_width}x{img_height}")
    print(f"   Font: {font_path}")
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("🧪 اختبار عرض النص العربي")
    print("=" * 60)
    
    success = test_arabic_text()
    
    if success:
        print("\n✅ All tests passed!")
        print("\nPlease check the generated image at: temp/arabic_text_test.png")
    else:
        print("\n❌ Test failed!")
