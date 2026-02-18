# البدء السريع - Quick Start Guide

## خطوات التشغيل السريعة

### 1. تثبيت المكتبات
```bash
pip install -r requirements.txt
```

### 2. إضافة مفتاح Pexels API

افتح ملف [config.py](config.py) واستبدل:
```python
PEXELS_API_KEY = "YOUR_PEXELS_API_KEY_HERE"
```

**احصل على مفتاح مجاني من**: https://www.pexels.com/api/

### 2.5. اختبار API (اختياري)
```bash
python test_api.py
```
هذا سيتحقق من عمل API dorar.net بشكل صحيح.

### 3. تشغيل التطبيق
```bash
python main.py
```

### 4. افتح المتصفح
```
http://localhost:5000
```

---

## استكشاف الأخطاء السريع

### ❌ خطأ: "No module named 'flask'"
```bash
pip install Flask
```

### ❌ خطأ: "مفتاح Pexels API غير موجود"
- أضف مفتاح API في ملف `config.py`
- احصل على مفتاح من https://www.pexels.com/api/

### ❌ خطأ: "moviepy error"
```bash
pip install moviepy==1.0.3
# أو
pip install moviepy --upgrade
```

### ❌ الخط العربي لا يظهر
- حمّل خط Amiri من: https://fonts.google.com/specimen/Amiri
- ضعه في: `static/fonts/Amiri-Regular.ttf`

---

## مثال على الاستخدام

1. **البحث**: اكتب "الصلاة" في حقل البحث
2. **اختر نوع الفيديو**: مثلاً "طبيعة"
3. **إنشاء الفيديو**: اضغط على زر "إنشاء فيديو"
4. **انتظر**: العملية تستغرق 2-5 دقائق
5. **شاهد وحمّل**: الفيديو النهائي جاهز!

---

## هل تحتاج مساعدة؟

اقرأ [README.md](README.md) الكامل للحصول على تعليمات مفصلة.
