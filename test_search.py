# -*- coding: utf-8 -*-
"""
اختبار سريع للبحث والدرجة
"""

import sys
sys.path.insert(0, 'c:\\Users\\ascom\\Documents\\augment-projects\\ai portfolio')

from main import search_hadith

print("=" * 60)
print("اختبار البحث عن الأحاديث")
print("=" * 60)

keyword = "الصلاة"
print(f"\nالبحث عن: {keyword}\n")

results = search_hadith(keyword)

print(f"عدد النتائج: {len(results)}\n")

if results:
    print("=" * 60)
    print("أول 3 نتائج:")
    print("=" * 60)
    
    for i, hadith in enumerate(results[:3], 1):
        print(f"\nالنتيجة {i}:")
        print(f"  📖 النص: {hadith.get('text', '')[:80]}...")
        print(f"  👤 الراوي: {hadith.get('narrator', 'غير محدد')}")
        print(f"  📚 المصدر: {hadith.get('source', 'غير محدد')}")
        print(f"  ⭐ الدرجة: {hadith.get('grade', 'غير محدد')}")
        print("-" * 60)
else:
    print("❌ لم يتم العثور على نتائج")

print("\n" + "=" * 60)
print("انتهى الاختبار")
print("=" * 60)
