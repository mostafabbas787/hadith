# 🔧 إصلاح API موقع dorar.net

## المشكلة
كان API موقع dorar.net يستخدم تنسيق JSONP (JSON with Padding) بدلاً من JSON العادي، مما كان يسبب خطأ في قراءة البيانات.

## الحل

### 1. التعديلات على الكود

تم تعديل دالة `search_hadith()` في ملف [main.py](main.py) لدعم JSONP:

#### قبل التعديل:
```python
url = f"{config.DORAR_API_URL}?skey={keyword}"
response = requests.get(url, timeout=10)
data = response.json()  # هذا كان يفشل مع JSONP
```

#### بعد التعديل:
```python
# إضافة callback parameter
url = f"{config.DORAR_API_URL}?skey={keyword}&callback=processDorar"
response = requests.get(url, timeout=10)

# معالجة JSONP - استخراج JSON من callback wrapper
json_match = re.search(r'processDorar\((.*)\);?$', response_text, re.DOTALL)
if json_match:
    json_str = json_match.group(1)
    data = json.loads(json_str)
```

### 2. شرح JSONP

**JSONP** هو تقنية قديمة للتغلب على قيود CORS في المتصفحات:

#### JSON العادي:
```json
{"ahadith": {"result": [...]}}
```

#### JSONP:
```javascript
processDorar({"ahadith": {"result": [...]}});
```

الاستجابة تكون مُغلفة في دالة JavaScript، لذا نحتاج:
1. إضافة `callback` parameter في URL
2. استخراج JSON من داخل الدالة باستخدام Regular Expression

### 3. التحسينات الإضافية

#### دعم أكثر من تنسيق:
```python
if isinstance(data['ahadith'], dict) and 'result' in data['ahadith']:
    hadiths = data['ahadith']['result']
elif isinstance(data['ahadith'], list):
    hadiths = data['ahadith']
```

#### معالجة أخطاء أفضل:
```python
except json.JSONDecodeError as e:
    logger.error(f"خطأ في تحليل JSON: {str(e)}")
    return []
```

## الاختبار

تم إنشاء ملف [test_api.py](test_api.py) لاختبار API:

```bash
python test_api.py
```

هذا السكريبت:
- ✅ يختبر الاتصال بـ API
- ✅ يعرض تنسيق الاستجابة
- ✅ يستخرج ويعرض أول حديث
- ✅ يوضح البيانات المتاحة

## مثال على الاستخدام

### Python:
```python
from main import search_hadith

results = search_hadith("الصلاة")
for hadith in results:
    print(f"النص: {hadith['text']}")
    print(f"الراوي: {hadith['narrator']}")
    print(f"الدرجة: {hadith['grade']}")
```

### JavaScript (في المتصفح):
```javascript
$.getJSON("https://dorar.net/dorar_api.json?skey=الصلاة&callback=?", 
    function(data) {
        $.each(data.ahadith, function(index, item) {
            console.log(item.th);  // نص الحديث
        });
    }
);
```

## التوافق

الكود الجديد يدعم:
- ✅ JSONP (مع callback)
- ✅ JSON العادي (fallback)
- ✅ تنسيقات متعددة للبيانات
- ✅ معالجة أخطاء شاملة

## الملفات المعدلة

1. **main.py**: 
   - تحديث `search_hadith()` function
   - إضافة imports: `re`, `json`
   - معالجة JSONP

2. **test_api.py** (جديد):
   - سكريبت اختبار شامل
   - عرض تفصيلي للنتائج

3. **README.md**:
   - إضافة خطوة اختبار API

4. **QUICKSTART.md**:
   - إضافة خطوة اختبار API

## التحقق من النجاح

بعد التعديلات، يمكنك:

1. **اختبار API**:
   ```bash
   python test_api.py
   ```

2. **تشغيل التطبيق**:
   ```bash
   python main.py
   ```

3. **البحث عن حديث**:
   - افتح http://localhost:5000
   - ابحث عن "الصلاة"
   - يجب أن تظهر النتائج بنجاح

## المصادر

- **Dorar.net API**: https://dorar.net/dorar_api.json
- **JSONP Documentation**: https://en.wikipedia.org/wiki/JSONP
- **Python Regex**: https://docs.python.org/3/library/re.html

---

**تم الإصلاح بنجاح! ✅**

الآن API dorar.net يعمل بشكل صحيح مع التطبيق.
