# -*- coding: utf-8 -*-
"""
اختبار API موقع dorar.net
Test script for dorar.net API
"""

import requests
import re
import json

def test_dorar_api(keyword):
    """اختبار API مع كلمة مفتاحية"""
    print(f"\n{'='*60}")
    print(f"اختبار البحث عن: {keyword}")
    print(f"{'='*60}\n")
    
    try:
        # URL مع callback
        url = f"https://dorar.net/dorar_api.json?skey={keyword}&callback=processDorar"
        print(f"URL: {url}\n")
        
        # إرسال الطلب
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}\n")
        
        # عرض أول 200 حرف من الاستجابة
        print("Response Preview:")
        print(response.text[:200])
        print("...\n")
        
        # معالجة JSONP
        response_text = response.text
        
        # استخراج JSON من JSONP callback
        json_match = re.search(r'processDorar\((.*)\);?\s*$', response_text, re.DOTALL)
        
        if json_match:
            print("✅ تم العثور على JSONP wrapper")
            json_str = json_match.group(1)
            data = json.loads(json_str)
        else:
            print("⚠️ لم يتم العثور على JSONP wrapper، محاولة JSON عادي")
            try:
                data = response.json()
            except:
                # محاولة استخراج JSON بأي طريقة
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                else:
                    print("❌ فشل في استخراج JSON")
                    return False
        
        # عرض النتائج
        if 'ahadith' in data:
            print("✅ تم العثور على مفتاح 'ahadith'\n")
            
            # التحقق من التنسيق
            if isinstance(data['ahadith'], dict) and 'result' in data['ahadith']:
                html_content = data['ahadith']['result']
                print(f"✅ data.ahadith.result يحتوي على HTML")
                print(f"طول المحتوى: {len(html_content)} حرف\n")
                
                # عرض جزء من HTML
                print("=" * 60)
                print("عينة من HTML:")
                print("=" * 60)
                print(html_content[:500])
                print("...\n")
                
                # استخراج الأحاديث من HTML
                hadith_pattern = r'<div class="hadith"[^>]*>(.*?)</div>'
                hadith_matches = re.findall(hadith_pattern, html_content, re.DOTALL)
                
                if not hadith_matches:
                    hadith_pattern = r'<div[^>]*class="hadith"[^>]*>(.*?)</div>'
                    hadith_matches = re.findall(hadith_pattern, html_content, re.DOTALL)
                
                print(f"✅ تم العثور على {len(hadith_matches)} حديث في HTML\n")
                
                if hadith_matches:
                    print("=" * 60)
                    print("أول حديث (HTML):")
                    print("=" * 60)
                    print(hadith_matches[0][:300])
                    print("...\n")
                    
                    # إزالة HTML tags
                    clean_text = re.sub(r'<[^>]+>', '', hadith_matches[0])
                    clean_text = clean_text.strip()
                    clean_text = re.sub(r'^\d+\s*-\s*', '', clean_text)
                    
                    print("=" * 60)
                    print("أول حديث (نص نظيف):")
                    print("=" * 60)
                    print(clean_text[:300])
                    print("...")
            else:
                print(f"❌ تنسيق غير متوقع")
                print(f"نوع ahadith: {type(data['ahadith'])}")
        else:
            print("❌ لم يتم العثور على مفتاح 'ahadith' في الاستجابة")
            print(f"المفاتيح المتاحة: {list(data.keys())}")
        
        print(f"\n{'='*60}")
        print("✅ الاختبار اكتمل بنجاح")
        print(f"{'='*60}\n")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ خطأ في تحليل JSON: {e}")
        print(f"الاستجابة الأصلية:\n{response.text[:500]}")
        return False
    except Exception as e:
        print(f"❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("اختبار API موقع dorar.net")
    print("Testing dorar.net API")
    print("="*60)
    
    # كلمات اختبار
    test_keywords = ["الصلاة", "الصدق", "الصبر"]
    
    for keyword in test_keywords:
        test_dorar_api(keyword)
        print("\n")
    
    print("="*60)
    print("انتهى الاختبار")
    print("="*60)
