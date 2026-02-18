# تعليمات تحميل الخط العربي
# Arabic Font Installation Instructions

## الخطوط العربية المدعومة

يمكنك استخدام أي من الخطوط العربية التالية:

### 1. خط Amiri (موصى به)
- الموقع: https://fonts.google.com/specimen/Amiri
- تحميل مباشر: https://fonts.google.com/download?family=Amiri
- بعد التحميل، استخرج الملف `Amiri-Regular.ttf` وضعه في مجلد `static/fonts/`

### 2. خط Cairo
- الموقع: https://fonts.google.com/specimen/Cairo
- تحميل مباشر: https://fonts.google.com/download?family=Cairo

### 3. خط Noto Sans Arabic
- الموقع: https://fonts.google.com/specimen/Noto+Sans+Arabic
- تحميل مباشر: https://fonts.google.com/download?family=Noto+Sans+Arabic

## طريقة التثبيت

1. قم بتحميل الخط من أحد الروابط أعلاه
2. استخرج ملف `.ttf` من الملف المضغوط
3. انسخه إلى مجلد `static/fonts/` في المشروع
4. تأكد من تحديث المسار في ملف `config.py`:

```python
FONT_PATH = "static/fonts/Amiri-Regular.ttf"
# أو
FONT_PATH = "static/fonts/Cairo-Regular.ttf"
# أو
FONT_PATH = "static/fonts/NotoSansArabic-Regular.ttf"
```

## ملاحظة

إذا لم تقم بتحميل خط عربي، سيستخدم التطبيق الخط الافتراضي (Arial) 
ولكن قد لا يظهر النص العربي بشكل صحيح في الفيديو.

## استخدام خط من النظام

يمكنك أيضاً استخدام خط مثبت على نظامك:

### Windows:
```python
FONT_PATH = "C:/Windows/Fonts/arial.ttf"
```

### Mac:
```python
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"
```

### Linux:
```python
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
```
