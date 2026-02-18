#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اختبار كامل للنظام - Full System Test
"""

import sys
import os

# إضافة المجلد الحالي إلى المسار
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import search_hadith

def test_full_system():
    """اختبار كامل للنظام"""
    print("=" * 60)
    print("🧪 اختبار شامل للنظام")
    print("=" * 60)
    
    # 1. اختبار البحث
    print("\n📝 اختبار البحث عن الحديث...")
    keyword = "الصدق"
    hadiths = search_hadith(keyword)
    
    if not hadiths:
        print("❌ فشل البحث - لم يتم العثور على أحاديث")
        return False
    
    print(f"✅ تم العثور على {len(hadiths)} حديث")
    
    # 2. عرض النتائج
    print("\n📋 النتائج:")
    for idx, hadith in enumerate(hadiths[:3], 1):  # أول 3 فقط
        print(f"\n--- حديث {idx} ---")
        print(f"📖 النص: {hadith['text'][:100]}...")
        print(f"👤 الراوي: {hadith.get('narrator', 'غير متوفر')}")
        print(f"📚 المصدر: {hadith.get('source', 'غير متوفر')}")
        print(f"⭐ الدرجة: {hadith.get('grade', 'غير متوفر')}")
    
    # 3. التحقق من درجات الأحاديث
    grades_found = sum(1 for h in hadiths if h.get('grade'))
    print(f"\n📊 الإحصائيات:")
    print(f"   • عدد الأحاديث التي لها درجة: {grades_found}/{len(hadiths)}")
    
    if grades_found == 0:
        print("   ⚠️ لم يتم استخراج أي درجات!")
        print("   💡 ربما يحتاج نمط regex للتعديل")
        return False
    elif grades_found < len(hadiths) // 2:
        print(f"   ⚠️ تم استخراج {grades_found} درجة فقط من {len(hadiths)}")
        return False
    else:
        print(f"   ✅ تم استخراج الدرجات بنجاح!")
    
    return True

if __name__ == "__main__":
    try:
        success = test_full_system()
        print("\n" + "=" * 60)
        if success:
            print("✅ الاختبار ناجح - النظام يعمل بشكل صحيح!")
        else:
            print("❌ فشل الاختبار - يرجى مراجعة الأخطاء أعلاه")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ خطأ في الاختبار: {str(e)}")
        import traceback
        traceback.print_exc()
