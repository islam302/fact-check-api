# Fact-Check API

API للتحقق من الأخبار وصياغة المحتوى الإخباري باستخدام OpenAI و SerpAPI.

## ⚠️ ملاحظة هامة

النظام يدعم **حالتين فقط** لنتيجة الفحص:
- ✅ **حقيقي (True)** - عندما يتم التأكد من صحة الخبر من مصادر موثوقة
- ⚠️ **غير مؤكد (Uncertain)** - عندما لا توجد معلومات كافية أو مصادر واضحة

**لا توجد حالة "كاذب" (False)** - إذا لم يتم التأكد من صحة الخبر، يتم تصنيفه تلقائياً كـ "غير مؤكد" بدلاً من "كاذب".

## المميزات

- ✅ التحقق من صحة الأخبار والادعاءات
- 📰 صياغة مقالات إخبارية احترافية
- 🐦 صياغة تغريدات للمنصات الاجتماعية
- 🔍 البحث عن المصادر الموثوقة
- 🌍 دعم متعدد اللغات (العربية، الإنجليزية، الفرنسية، الإسبانية، وغيرها)

## التثبيت

```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# إعداد ملف .env
SERPAPI_KEY=your_serpapi_key
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o
SERPAPI_HL=ar
SERPAPI_GL=
NEWS_AGENCIES=aljazeera.net,una-oic.org,bbc.com

# تشغيل السيرفر
python manage.py runserver
```

## API Endpoints

### 1. التحقق من الأخبار (Fact-Check)

**الطريقة:** `POST /fact_check_with_openai/`

**الطلب:**
```json
{
  "query": "نص الخبر أو الادعاء المراد التحقق منه",
  "generate_news": true,  // اختياري: توليد مقال إخباري مباشرة
  "preserve_sources": false,  // اختياري: الاحتفاظ بالمصادر حتى للنتائج غير المؤكدة
  "generate_tweet": true  // اختياري: توليد تغريدة مباشرة
}
```

**الاستجابة:**
```json
{
  "ok": true,
  "query": "النص المدخل",
  "case": "حقيقي / غير مؤكد",
  "talk": "التحليل المفصل لنتيجة الفحص",
  "sources": [
    {
      "title": "عنوان المصدر",
      "url": "رابط المصدر"
    }
  ],
  "news_article": "المقال الإخباري (إذا كان generate_news=true)",
  "x_tweet": "التغريدة (إذا كان generate_tweet=true)"
}
```

### 2. صياغة خبر من نتيجة الفحص

**الطريقة:** `POST /fact_check_with_openai/compose_news/`

يتيح لك هذا Endpoint صياغة مقال إخباري احترافي بعد إجراء الفحص، باستخدام النتيجة مباشرة **دون حفظها في قاعدة البيانات**.

**الطلب:**
```json
{
  "claim_text": "النص المراد فحصه",
  "case": "حقيقي / غير مؤكد",
  "talk": "التحليل الناتج من الفحص",
  "sources": [
    {
      "title": "عنوان المصدر",
      "url": "رابط المصدر",
      "snippet": "ملخص المصدر"
    }
  ],
  "lang": "ar"  // اختياري، الافتراضي: ar
}
```

**الاستجابة:**
```json
{
  "ok": true,
  "news_article": "المقال الإخباري المصاغ بشكل احترافي"
}
```

**مثال استخدام:**
```bash
curl -X POST http://localhost:8000/fact_check_with_openai/compose_news/ \
  -H "Content-Type: application/json" \
  -d '{
    "claim_text": "تم افتتاح مطار جديد في الرياض",
    "case": "حقيقي",
    "talk": "تم التأكد من افتتاح المطار من خلال مصادر رسمية",
    "sources": [
      {
        "title": "الهيئة العامة للطيران المدني تعلن افتتاح المطار",
        "url": "https://example.com/news",
        "snippet": "أعلنت الهيئة عن افتتاح المطار الجديد"
      }
    ],
    "lang": "ar"
  }'
```

### 3. صياغة تغريدة من نتيجة الفحص

**الطريقة:** `POST /fact_check_with_openai/compose_tweet/`

يتيح لك هذا Endpoint صياغة تغريدة احترافية بعد إجراء الفحص، باستخدام النتيجة مباشرة **دون حفظها في قاعدة البيانات**.

**الطلب:**
```json
{
  "claim_text": "النص المراد فحصه",
  "case": "حقيقي / غير مؤكد",
  "talk": "التحليل الناتج من الفحص",
  "sources": [
    {
      "title": "عنوان المصدر",
      "url": "رابط المصدر",
      "snippet": "ملخص المصدر"
    }
  ],
  "lang": "ar"  // اختياري، الافتراضي: ar
}
```

**الاستجابة:**
```json
{
  "ok": true,
  "x_tweet": "التغريدة المصاغة بشكل احترافي (أقل من 280 حرف)"
}
```

**مثال استخدام:**
```bash
curl -X POST http://localhost:8000/fact_check_with_openai/compose_tweet/ \
  -H "Content-Type: application/json" \
  -d '{
    "claim_text": "تم افتتاح مطار جديد في الرياض",
    "case": "حقيقي",
    "talk": "تم التأكد من افتتاح المطار من خلال مصادر رسمية",
    "sources": [
      {
        "title": "الهيئة العامة للطيران المدني تعلن افتتاح المطار",
        "url": "https://example.com/news",
        "snippet": "أعلنت الهيئة عن افتتاح المطار الجديد"
      }
    ],
    "lang": "ar"
  }'
```

### 4. صياغة مقال تحليلي

**الطريقة:** `POST /fact_check_with_openai/analytical_news/`

**الطلب:**
```json
{
  "headline": "عنوان الخبر",
  "analysis": "التحليل التحققي",
  "lang": "ar"  // اختياري، الافتراضي: ar
}
```

**الاستجابة:**
```json
{
  "ok": true,
  "headline": "عنوان الخبر",
  "analysis": "التحليل التحققي",
  "analytical_article": "المقال التحليلي المصاغ"
}
```

## سير العمل (Workflow)

### الطريقة الأولى: كل شيء دفعة واحدة
```javascript
// فحص وصياغة في خطوة واحدة
const response = await fetch('/fact_check_with_openai/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "نص الخبر",
    generate_news: true,
    generate_tweet: true
  })
});

const result = await response.json();
// ستحصل على: case, talk, sources, news_article, x_tweet
```

### الطريقة الثانية: الفحص ثم الصياغة (موصى بها للتحكم الأفضل)
```javascript
// 1. أولاً: فحص الخبر
const checkResponse = await fetch('/fact_check_with_openai/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "نص الخبر"
  })
});

const checkResult = await checkResponse.json();
// checkResult يحتوي على: case, talk, sources

// 2. ثانياً: صياغة خبر (بدون حفظ في قاعدة البيانات)
const newsResponse = await fetch('/fact_check_with_openai/compose_news/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    claim_text: "نص الخبر",
    case: checkResult.case,
    talk: checkResult.talk,
    sources: checkResult.sources,
    lang: "ar"
  })
});

const newsResult = await newsResponse.json();
// newsResult.news_article يحتوي على المقال

// 3. أو: صياغة تغريدة (بدون حفظ في قاعدة البيانات)
const tweetResponse = await fetch('/fact_check_with_openai/compose_tweet/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    claim_text: "نص الخبر",
    case: checkResult.case,
    talk: checkResult.talk,
    sources: checkResult.sources,
    lang: "ar"
  })
});

const tweetResult = await tweetResponse.json();
// tweetResult.x_tweet يحتوي على التغريدة
```

## ملاحظات هامة

1. **عدم الحفظ في قاعدة البيانات**: جميع endpoints لا تحفظ أي بيانات في قاعدة البيانات، فقط معالجة فورية
2. **المصادر**: في حالة النتائج غير المؤكدة، يتم إفراغ المصادر تلقائياً ما لم تستخدم `preserve_sources=true`
3. **اللغات المدعومة**: العربية (ar)، الإنجليزية (en)، الفرنسية (fr)، الإسبانية (es)، التشيكية (cs)، وغيرها
4. **حد التغريدات**: التغريدات محدودة تلقائياً بـ 280 حرف

## التطوير

```bash
# تشغيل السيرفر للتطوير
python manage.py runserver

# اختبار الأداء
locust -f locustfile.py
```

## الترخيص

هذا المشروع مملوك لـ UNA-OIC
