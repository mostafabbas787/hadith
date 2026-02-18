# -*- coding: utf-8 -*-
"""
Test font rendering for Arabic text in video
"""
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import os

def test_font():
    # Font path
    font_path = 'static/fonts/NotoSansArabic-Bold.ttf'
    
    if not os.path.exists(font_path):
        print(f"Font not found: {font_path}")
        return
    
    # Load font
    font = ImageFont.truetype(font_path, 40)
    
    # Create image
    img = Image.new('RGB', (1000, 400), (30, 30, 50))
    draw = ImageDraw.Draw(img)
    
    # Test texts
    texts = [
        "الحكم صحيح - الراوي عبدالله - المصدر البخاري",
        "هذا اختبار للخط العربي في الفيديو",
        "قال رسول الله صلى الله عليه وسلم",
    ]
    
    y = 50
    for text in texts:
        # Format Arabic text
        reshaped = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped)
        
        # Draw text
        draw.text((50, y), bidi_text, font=font, fill=(255, 255, 255))
        y += 100
    
    # Save test image
    output_path = 'temp/font_test_full.png'
    img.save(output_path)
    print(f"Test image saved to: {output_path}")
    print("Font rendering test completed successfully!")

if __name__ == "__main__":
    test_font()
