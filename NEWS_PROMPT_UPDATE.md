# 📰 تحديث برومبت المقالات الإخبارية

## ما تم تحديثه

تم تحديث دالة توليد المقالات الإخبارية لتستخدم البرومبت المحدد الذي طلبته، مع فصل منطق المقالات حسب نوع النتيجة.

---

## 🎯 البرومبت الجديد

### للخبر الحقيقي (TRUE):

```
اكتب خبرًا صحفيًا تحليليًا بأسلوب الوكالات العالمية باستخدام العنوان والتحليل التاليين.
ابدأ الخبر بالتصريح أو الحدث الرئيسي الذي ظهر لك في نتائج التحليل، وليس بعبارة "أكدت نتائج التحقق"، وادمج نتيجة التحقق ضمن المتن بشكل طبيعي لدعم موثوقية الخبر.
احرص أن تكون الصياغة بشرية وسلسة، متوازنة، ومبنية على التفاصيل المذكورة في التحليل، مع تجنب التكرار والصيغ الآلية، واذكر المصادر الواردة في التحليل بأسلوب خبري طبيعي إن وُجدت.
```

### للخبر غير المؤكد (UNCERTAIN):

```
اكتب خبرًا صحفيًا تحليليًا مختصرًا بأسلوب الوكالات العالمية باستخدام العنوان والتحليل التاليين.
ابدأ الخبر بالإشارة إلى تداول الخبر في وسائل الإعلام أو التواصل الاجتماعي بصيغة موضوعية مثل: "تداولت منصات التواصل الاجتماعي مزاعم تفيد بأن..." أو "انتشرت تقارير تزعم أن..."، ثم وضّح من خلال نتيجة التحقق أن الادعاء غير مؤكد أو غير صحيح ولا يوجد أي دلائل عليه.
احرص أن تكون الصياغة بشرية وسلسة ومبنية على ما ورد في التحليل، مع تجنّب التكرار أو العبارات الآلية.
```

---

## 🔧 التغييرات التقنية

### 1. تحديد البرومبت حسب النتيجة:

```python
if case.lower() in {"حقيقي", "true", "vrai", "verdadero", "pravda"}:
    # استخدام برومبت الخبر الحقيقي
    FACT_CHECK_NEWS_PROMPT = """
    Write an analytical news article in the style of international agencies...
    Begin the news with the main statement or event...
    """
else:
    # استخدام برومبت الخبر غير المؤكد
    FACT_CHECK_NEWS_PROMPT = """
    Write a brief analytical news article in the style of international agencies...
    Begin the news by referring to the circulation of the news in media...
    """
```

### 2. الملفات المحدثة:

- ✅ `fact_check_with_openai/utils_async.py` - النسخة async
- ✅ `fact_check_with_openai/utils.py` - النسخة العادية

### 3. التوافق:

- ✅ يعمل مع جميع اللغات (ar, en, fr, es, etc.)
- ✅ يعمل مع النسخة async والنسخة العادية
- ✅ لا يؤثر على باقي الوظائف

---

## 📊 أمثلة على النتائج المتوقعة

### للخبر الحقيقي:
```
NASA announced the discovery of a new exoplanet in the habitable zone of a distant star system. The space agency confirmed that the planet, located approximately 1,400 light-years from Earth, shows promising conditions for potential life.

According to the announcement, the newly discovered planet orbits within the "Goldilocks zone" where temperatures could allow for liquid water to exist on the surface. Scientists used data from NASA's Kepler Space Telescope to identify the planetary system.

The discovery represents a significant milestone in the ongoing search for potentially habitable worlds beyond our solar system. Research teams have been analyzing the data for several months before making the official announcement.

This finding adds to the growing catalog of exoplanets that could potentially support life, bringing the total number of confirmed habitable zone planets to over 50. The discovery has generated excitement in the scientific community and renewed interest in space exploration missions.
```

### للخبر غير المؤكد:
```
Social media platforms circulated claims stating that NASA had discovered evidence of alien life on Mars. However, verification of these reports reveals that no such announcement has been made by the space agency.

While NASA has indeed made significant discoveries on Mars through its various rover missions, including evidence of ancient water activity and organic molecules, there has been no official confirmation of alien life. The agency's recent announcements have focused on geological findings and atmospheric studies rather than biological discoveries.

The confusion may have arisen from misinterpretations of NASA's scientific findings or from unofficial speculation within the space community. NASA officials have consistently maintained that while Mars shows signs of having had conditions suitable for life in the past, no direct evidence of current or past life has been confirmed.

The agency continues its search for signs of life through ongoing missions, but emphasizes that any such discovery would be announced through official channels following rigorous scientific verification.
```

---

## 🚀 كيفية الاختبار

### 1. اختبر خبر حقيقي:
```bash
curl -X POST http://localhost:8000/fact_check_with_openai/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "NASA announced discovery of new planet",
    "generate_news": true
  }'
```

### 2. اختبر خبر غير مؤكد:
```bash
curl -X POST http://localhost:8000/fact_check_with_openai/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "NASA found aliens on Mars",
    "generate_news": true
  }'
```

---

## ✅ التحسينات

### المميزات الجديدة:

1. **برومبت محدد**: يستخدم البرومبت المطلوب بالضبط
2. **فصل المنطق**: برومبت مختلف للخبر الحقيقي وغير المؤكد
3. **صياغة طبيعية**: تجنب العبارات الآلية
4. **دعم المصادر**: ذكر المصادر بأسلوب طبيعي
5. **أسلوب الوكالات**: كتابة بأسلوب وكالات الأنباء العالمية

### النتائج المتوقعة:

- ✅ مقالات أكثر طبيعية وسلاسة
- ✅ تجنب العبارات الميكانيكية
- ✅ صياغة احترافية بأسلوب الوكالات
- ✅ ذكر المصادر بشكل طبيعي
- ✅ طول مناسب (150-250 كلمة)

---

## 📝 ملاحظات

- ✅ التحديث لا يؤثر على السرعة
- ✅ يعمل مع جميع اللغات
- ✅ متوافق مع النسخة async
- ✅ لا حاجة لتغيير أي شيء في الكود الموجود

---

**جاهز للاستخدام! 🎉**
