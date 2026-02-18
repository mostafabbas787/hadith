#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
فحص بنية HTML من API
"""
import requests
import json
import re

def debug_api():
    url = "https://dorar.net/dorar_api.json?skey=الصدق"
    
    response = requests.get(url, timeout=15)
    response.encoding = 'utf-8'
    text = response.text
    
    # استخراج JSON من JSONP
    match = re.search(r'processDorar\((.*)\)', text, re.DOTALL)
    if match:
        json_str = match.group(1)
        data = json.loads(json_str)
        html = data.get('ahadith', {}).get('result', '')
        
        # حفظ HTML للفحص
        with open('debug_html.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("✅ تم حفظ HTML في debug_html.html")
        
        # عرض جزء من HTML
        print("\n📋 أول 3000 حرف من HTML:")
        print("=" * 60)
        print(html[:3000])
        print("=" * 60)
        
        # البحث عن أنماط الدرجة
        print("\n🔍 البحث عن أنماط درجة الحديث:")
        
        # نمط 1
        pattern1 = r'خلاصة حكم المحدث'
        matches1 = re.findall(pattern1, html)
        print(f"   'خلاصة حكم المحدث': {len(matches1)} مرة")
        
        # نمط 2
        pattern2 = r'الدرجة'
        matches2 = re.findall(pattern2, html)
        print(f"   'الدرجة': {len(matches2)} مرة")
        
        # نمط 3 - ابحث عن صحيح/حسن/ضعيف
        for word in ['صحيح', 'حسن', 'ضعيف', 'إسناده']:
            count = len(re.findall(word, html))
            print(f"   '{word}': {count} مرة")
        
        # استخراج info-subtitle
        info_subtitles = re.findall(r'info-subtitle[^>]*>([^<]+)', html)
        print(f"\n📌 info-subtitle موجودة:")
        for subtitle in set(info_subtitles[:20]):
            print(f"   - {subtitle}")
        
if __name__ == "__main__":
    debug_api()
