# توثيق API التحقق من الأخبار

## ⚠️ ملاحظة هامة

النظام يدعم **حالتين فقط** لنتيجة الفحص:
- ✅ **حقيقي (True)** - عندما يتم التأكد من صحة الخبر من مصادر موثوقة
- ⚠️ **غير مؤكد (Uncertain)** - عندما لا توجد معلومات كافية أو مصادر واضحة

**❌ لا توجد حالة "كاذب" (False)** - إذا لم يتم التأكد من صحة الخبر، يتم تصنيفه تلقائياً كـ "غير مؤكد" بدلاً من "كاذب".

---

## 📋 جدول المحتويات
1. [نظرة عامة](#نظرة-عامة)
2. [Endpoints الرئيسية](#endpoints-الرئيسية)
3. [أمثلة الاستخدام](#أمثلة-الاستخدام)
4. [معالجة الأخطاء](#معالجة-الأخطاء)
5. [أفضل الممارسات](#أفضل-الممارسات)

---

## نظرة عامة

هذا API يوفر خدمات شاملة للتحقق من الأخبار وصياغة المحتوى الإخباري. جميع البيانات تُعالج مباشرة **بدون حفظ في قاعدة البيانات**، مما يوفر خصوصية وسرعة في المعالجة.

### المميزات الرئيسية
- ✅ التحقق التلقائي من صحة الأخبار
- 📰 صياغة مقالات إخبارية احترافية
- 🐦 صياغة تغريدات للمنصات الاجتماعية
- 🔍 البحث التلقائي في المصادر الموثوقة
- 🌍 دعم متعدد اللغات
- 🚀 معالجة فورية بدون حفظ

---

## Endpoints الرئيسية

### 1️⃣ التحقق من الأخبار

**Endpoint:** `POST /fact_check_with_openai/`

يقوم بفحص الخبر والتحقق من صحته من خلال البحث في المصادر الموثوقة.

#### المعاملات (Parameters)

| المعامل | النوع | إلزامي | الوصف | الافتراضي |
|---------|------|--------|-------|-----------|
| `query` | string | ✅ نعم | نص الخبر أو الادعاء المراد فحصه | - |
| `generate_news` | boolean | ❌ لا | توليد مقال إخباري مباشرة | `false` |
| `generate_tweet` | boolean | ❌ لا | توليد تغريدة مباشرة | `false` |
| `preserve_sources` | boolean | ❌ لا | الاحتفاظ بالمصادر حتى للنتائج غير المؤكدة | `false` |

#### مثال الطلب

```json
{
  "query": "تم افتتاح مطار جديد في الرياض اليوم",
  "generate_news": false,
  "generate_tweet": false,
  "preserve_sources": false
}
```

#### مثال الاستجابة

```json
{
  "ok": true,
  "query": "تم افتتاح مطار جديد في الرياض اليوم",
  "case": "حقيقي",
  "talk": "تم التأكد من صحة الخبر من خلال مصادر رسمية موثوقة...",
  "sources": [
    {
      "title": "الهيئة العامة للطيران المدني تعلن افتتاح المطار",
      "url": "https://example.com/news"
    }
  ],
  "news_article": null,
  "x_tweet": null
}
```

#### قيم الحالة (Case Values)

**ملاحظة:** النظام يدعم حالتين فقط:

| العربية | English | Français | Español |
|---------|---------|----------|---------|
| حقيقي | True | Vrai | Verdadero |
| غير مؤكد | Uncertain | Incertain | Incierto |

**لا توجد حالة "كاذب"** - إذا لم يتم التأكد من صحة الخبر، يتم تصنيفه كـ "غير مؤكد".

---

### 2️⃣ صياغة خبر من نتيجة الفحص

**Endpoint:** `POST /fact_check_with_openai/compose_news/`

يقوم بصياغة مقال إخباري احترافي من نتيجة الفحص **بدون حفظ في قاعدة البيانات**.

#### المعاملات (Parameters)

| المعامل | النوع | إلزامي | الوصف | الافتراضي |
|---------|------|--------|-------|-----------|
| `claim_text` | string | ✅ نعم | نص الخبر الأصلي | - |
| `case` | string | ✅ نعم | نتيجة الفحص (حقيقي/غير مؤكد) | - |
| `talk` | string | ✅ نعم | التحليل المفصل من الفحص | - |
| `sources` | array | ❌ لا | قائمة المصادر | `[]` |
| `lang` | string | ❌ لا | لغة المقال | `"ar"` |

#### مثال الطلب

```json
{
  "claim_text": "تم افتتاح مطار جديد في الرياض اليوم",
  "case": "حقيقي",
  "talk": "تم التأكد من صحة الخبر من خلال مصادر رسمية موثوقة. أعلنت الهيئة العامة للطيران المدني عن افتتاح المطار الجديد في الرياض، والذي يعد أحد أكبر المطارات في المنطقة.",
  "sources": [
    {
      "title": "الهيئة العامة للطيران المدني تعلن افتتاح المطار",
      "url": "https://example.com/news1",
      "snippet": "أعلنت الهيئة العامة للطيران المدني عن افتتاح المطار الجديد"
    }
  ],
  "lang": "ar"
}
```

#### مثال الاستجابة

```json
{
  "ok": true,
  "news_article": "**افتتاح مطار الرياض الجديد رسمياً**\n\nأعلنت الهيئة العامة للطيران المدني اليوم عن افتتاح المطار الجديد في الرياض، والذي يُعد أحد أكبر المطارات في المنطقة...\n\n[المقال الكامل]"
}
```

---

### 3️⃣ صياغة تغريدة من نتيجة الفحص

**Endpoint:** `POST /fact_check_with_openai/compose_tweet/`

يقوم بصياغة تغريدة احترافية (أقل من 280 حرف) من نتيجة الفحص **بدون حفظ في قاعدة البيانات**.

#### المعاملات (Parameters)

نفس معاملات endpoint صياغة الخبر.

#### مثال الطلب

```json
{
  "claim_text": "تم افتتاح مطار جديد في الرياض اليوم",
  "case": "حقيقي",
  "talk": "تم التأكد من صحة الخبر من خلال مصادر رسمية موثوقة.",
  "sources": [
    {
      "title": "الهيئة العامة للطيران المدني تعلن افتتاح المطار",
      "url": "https://example.com/news1"
    }
  ],
  "lang": "ar"
}
```

#### مثال الاستجابة

```json
{
  "ok": true,
  "x_tweet": "✅ حقيقي: افتتاح مطار الرياض الجديد\n\nتأكدت مصادر رسمية من افتتاح المطار الجديد في الرياض، أحد أكبر المطارات بالمنطقة. 🛫\n\n#الرياض #مطار_الرياض #السعودية"
}
```

---

### 4️⃣ صياغة مقال تحليلي

**Endpoint:** `POST /fact_check_with_openai/analytical_news/`

يقوم بصياغة مقال تحليلي احترافي بأسلوب الوكالات الإخبارية الدولية.

#### المعاملات (Parameters)

| المعامل | النوع | إلزامي | الوصف | الافتراضي |
|---------|------|--------|-------|-----------|
| `headline` | string | ✅ نعم | عنوان الخبر | - |
| `analysis` | string | ✅ نعم | التحليل التحققي | - |
| `lang` | string | ❌ لا | لغة المقال | `"ar"` |

#### مثال الطلب

```json
{
  "headline": "افتتاح مطار الرياض الجديد",
  "analysis": "تم التأكد من صحة الخبر من خلال مصادر رسمية موثوقة. أعلنت الهيئة العامة للطيران المدني عن افتتاح المطار الجديد.",
  "lang": "ar"
}
```

---

## أمثلة الاستخدام

### السيناريو الأول: كل شيء دفعة واحدة

استخدم هذا السيناريو عندما تريد الحصول على كل شيء (فحص + خبر + تغريدة) في طلب واحد.

```python
import requests

response = requests.post(
    'http://localhost:8000/fact_check_with_openai/',
    json={
        'query': 'تم افتتاح مطار جديد في الرياض اليوم',
        'generate_news': True,
        'generate_tweet': True
    }
)

result = response.json()
print(f"الحالة: {result['case']}")
print(f"المقال: {result['news_article']}")
print(f"التغريدة: {result['x_tweet']}")
```

### السيناريو الثاني: فحص ثم صياغة (موصى به)

استخدم هذا السيناريو للحصول على تحكم أفضل في العملية.

```python
import requests

# الخطوة 1: فحص الخبر
check_response = requests.post(
    'http://localhost:8000/fact_check_with_openai/',
    json={'query': 'تم افتتاح مطار جديد في الرياض اليوم'}
)
check_result = check_response.json()

# الخطوة 2: صياغة خبر من النتيجة
news_response = requests.post(
    'http://localhost:8000/fact_check_with_openai/compose_news/',
    json={
        'claim_text': 'تم افتتاح مطار جديد في الرياض اليوم',
        'case': check_result['case'],
        'talk': check_result['talk'],
        'sources': check_result['sources'],
        'lang': 'ar'
    }
)
news_result = news_response.json()

# الخطوة 3: صياغة تغريدة من النتيجة
tweet_response = requests.post(
    'http://localhost:8000/fact_check_with_openai/compose_tweet/',
    json={
        'claim_text': 'تم افتتاح مطار جديد في الرياض اليوم',
        'case': check_result['case'],
        'talk': check_result['talk'],
        'sources': check_result['sources'],
        'lang': 'ar'
    }
)
tweet_result = tweet_response.json()

print(f"الحالة: {check_result['case']}")
print(f"المقال: {news_result['news_article']}")
print(f"التغريدة: {tweet_result['x_tweet']}")
```

### مثال JavaScript/TypeScript

```javascript
// الفحص والصياغة
async function factCheckAndCompose(claimText) {
  // 1. فحص
  const checkResponse = await fetch('http://localhost:8000/fact_check_with_openai/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: claimText })
  });
  const checkResult = await checkResponse.json();
  
  // 2. صياغة خبر
  const newsResponse = await fetch('http://localhost:8000/fact_check_with_openai/compose_news/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      claim_text: claimText,
      case: checkResult.case,
      talk: checkResult.talk,
      sources: checkResult.sources,
      lang: 'ar'
    })
  });
  const newsResult = await newsResponse.json();
  
  // 3. صياغة تغريدة
  const tweetResponse = await fetch('http://localhost:8000/fact_check_with_openai/compose_tweet/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      claim_text: claimText,
      case: checkResult.case,
      talk: checkResult.talk,
      sources: checkResult.sources,
      lang: 'ar'
    })
  });
  const tweetResult = await tweetResponse.json();
  
  return {
    check: checkResult,
    news: newsResult.news_article,
    tweet: tweetResult.x_tweet
  };
}

// استخدام
const result = await factCheckAndCompose('تم افتتاح مطار جديد في الرياض اليوم');
console.log('الحالة:', result.check.case);
console.log('المقال:', result.news);
console.log('التغريدة:', result.tweet);
```

---

## معالجة الأخطاء

جميع الـ endpoints ترجع استجابات موحدة في حالة الخطأ:

```json
{
  "ok": false,
  "error": "وصف الخطأ",
  "trace": "تفاصيل الخطأ التقنية (في وضع التطوير فقط)"
}
```

### رموز حالة HTTP

| الرمز | الوصف | السبب |
|------|-------|-------|
| 200 | نجح الطلب | تمت المعالجة بنجاح |
| 400 | خطأ في الطلب | بيانات مفقودة أو غير صحيحة |
| 500 | خطأ في الخادم | خطأ في المعالجة |

### مثال معالجة الأخطاء

```python
try:
    response = requests.post(url, json=payload)
    response.raise_for_status()
    result = response.json()
    
    if not result.get('ok', False):
        print(f"خطأ في API: {result.get('error')}")
    else:
        # معالجة النتيجة الناجحة
        pass
        
except requests.exceptions.RequestException as e:
    print(f"خطأ في الاتصال: {e}")
except json.JSONDecodeError as e:
    print(f"خطأ في تحليل JSON: {e}")
```

---

## أفضل الممارسات

### 1. استخدام السيناريو المناسب

- **استخدم "كل شيء دفعة واحدة"** عندما: تريد سرعة وبساطة، لا تحتاج إلى مراجعة نتيجة الفحص قبل الصياغة
- **استخدم "فحص ثم صياغة"** عندما: تريد تحكم أفضل، تريد مراجعة النتيجة قبل الصياغة، تريد صياغة أنواع مختلفة من المحتوى

### 2. إدارة المصادر

```python
# احتفظ بالمصادر حتى للنتائج غير المؤكدة
response = requests.post(url, json={
    'query': 'خبر غير مؤكد',
    'preserve_sources': True
})
```

### 3. دعم متعدد اللغات

```python
# صياغة بلغات مختلفة
langs = ['ar', 'en', 'fr', 'es']
for lang in langs:
    news = compose_news(..., lang=lang)
```

### 4. التحقق من طول التغريدة

```python
tweet = result['x_tweet']
if len(tweet) <= 280:
    print("✅ التغريدة جاهزة للنشر")
else:
    print("⚠️ التغريدة طويلة جداً")
```

### 5. إدارة الأخطاء بشكل صحيح

```python
def safe_api_call(url, payload):
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        return {'ok': False, 'error': 'انتهت مهلة الطلب'}
    except requests.RequestException as e:
        return {'ok': False, 'error': str(e)}
```

### 6. الأداء والسرعة

- استخدم `preserve_sources=False` (الافتراضي) للنتائج غير المؤكدة لتقليل حجم البيانات
- قم بتخزين النتائج مؤقتاً في frontend لتجنب طلبات مكررة
- استخدم async/await في JavaScript للطلبات المتعددة

### 7. الأمان

- لا تشارك مفاتيح API الخاصة بك
- استخدم HTTPS في الإنتاج
- قم بتحديد معدل الطلبات (rate limiting) في frontend

---

## ملاحظات إضافية

### المراجع الزمنية

النظام يترجم تلقائياً المراجع الزمنية مثل "اليوم" إلى تواريخ محددة:

```python
# "تم افتتاح المطار اليوم" → "تم افتتاح المطار 2024-01-15"
```

### اللغات المدعومة

- 🇸🇦 العربية (ar)
- 🇬🇧 الإنجليزية (en)
- 🇫🇷 الفرنسية (fr)
- 🇪🇸 الإسبانية (es)
- 🇨🇿 التشيكية (cs)
- 🇩🇪 الألمانية (de)
- 🇹🇷 التركية (tr)
- 🇷🇺 الروسية (ru)

### وكالات الأنباء الافتراضية

يبحث النظام تلقائياً في:
- aljazeera.net
- una-oic.org
- bbc.com

يمكن تخصيصها في ملف `.env`:
```env
NEWS_AGENCIES=aljazeera.net,una-oic.org,bbc.com,reuters.com
```

---

## المتطلبات التقنية

- Python 3.8+
- Django 4.0+
- OpenAI API Key
- SerpAPI Key

## الدعم والمساعدة

للمزيد من المساعدة، راجع:
- [README.md](README.md) - توثيق المشروع الرئيسي
- [example_usage.py](example_usage.py) - أمثلة Python
- [test_endpoints.ps1](test_endpoints.ps1) - اختبارات PowerShell
- [Fact_Check_API.postman_collection.json](Fact_Check_API.postman_collection.json) - Postman Collection

---

**تم التطوير بواسطة:** UNA-OIC  
**الإصدار:** 1.0  
**آخر تحديث:** 2024

