# سجل التغييرات (Changelog)

## [v2.0.0] - 2024-10-10

### 🔴 تغييرات جوهرية (Breaking Changes)

#### إزالة حالة "كاذب" (False)
تم تحديث النظام ليدعم **حالتين فقط** بدلاً من ثلاث حالات:

**قبل:**
- ✅ حقيقي (True)
- ❌ كاذب (False)
- ⚠️ غير مؤكد (Uncertain)

**بعد:**
- ✅ حقيقي (True) - عندما يتم التأكد من صحة الخبر من مصادر موثوقة
- ⚠️ غير مؤكد (Uncertain) - عندما لا توجد معلومات كافية أو مصادر واضحة

### 📝 التفاصيل

#### السبب
تم إزالة حالة "كاذب" لأن:
1. **الدقة الأخلاقية**: تصنيف خبر كـ"كاذب" يتطلب دليل قاطع على التزوير أو الكذب المتعمد
2. **الحيادية**: في معظم الحالات، عدم وجود دليل على صحة الخبر لا يعني بالضرورة أنه كاذب
3. **المسؤولية المهنية**: الصحافة المسؤولة تتطلب حذر أكبر في إطلاق أحكام "الكذب"

#### التأثير على الكود الموجود

إذا كنت تستخدم API في تطبيق موجود، قد تحتاج إلى:

1. **تحديث منطق معالجة النتائج:**
   ```javascript
   // قبل
   if (result.case === "كاذب") {
     showFalseNews();
   }
   
   // بعد
   if (result.case === "غير مؤكد") {
     showUncertainNews();
   }
   ```

2. **تحديث واجهة المستخدم:**
   - إزالة أيقونات/رموز "كاذب" (❌)
   - استخدام "غير مؤكد" (⚠️) بدلاً منها

3. **تحديث قاعدة البيانات (إن وجدت):**
   ```sql
   UPDATE fact_checks 
   SET case = 'غير مؤكد' 
   WHERE case = 'كاذب';
   ```

### ✨ التحديثات

#### الكود الأساسي
- ✅ تحديث `FACT_PROMPT_SYSTEM` في `utils.py`
- ✅ تحديث دالة `generate_x_tweet` في `utils.py`
- ✅ إزالة جميع المراجع لحالة "كاذب"

#### التوثيق
- ✅ تحديث `README.md` مع ملاحظة واضحة
- ✅ تحديث `API_DOCUMENTATION_AR.md`
- ✅ إضافة تحذيرات في جميع الأمثلة

#### الأمثلة والاختبارات
- ✅ تحديث `example_usage.py`
- ✅ تحديث `test_endpoints.ps1`
- ✅ تحديث `test_endpoints.sh`
- ✅ تحديث `Fact_Check_API.postman_collection.json`
- ✅ إزالة جميع الأمثلة التي تستخدم "كاذب"

### 🔄 دليل الترقية

#### للمطورين

1. **اقرأ التغييرات الجوهرية أعلاه**
2. **حدّث كود التطبيق الخاص بك**
3. **اختبر جميع الحالات**
4. **حدّث قاعدة البيانات إذا لزم الأمر**

#### مثال كامل للترقية

```python
# قبل الترقية
def handle_fact_check_result(result):
    if result['case'] == 'حقيقي':
        return "✅ الخبر صحيح"
    elif result['case'] == 'كاذب':
        return "❌ الخبر كاذب"
    else:
        return "⚠️ الخبر غير مؤكد"

# بعد الترقية
def handle_fact_check_result(result):
    if result['case'] == 'حقيقي':
        return "✅ الخبر صحيح"
    else:  # فقط حالة واحدة أخرى: غير مؤكد
        return "⚠️ الخبر غير مؤكد"
```

### 📊 إحصائيات التغييرات

- **الملفات المحدثة**: 8 ملفات
- **الأسطر المضافة**: ~100 سطر
- **الأسطر المحذوفة**: ~80 سطر
- **الأمثلة المحذوفة**: 4 أمثلة (كانت تستخدم "كاذب")

### 🔍 التفاصيل التقنية

#### التغييرات في `utils.py`

**الـ Prompt الجديد:**
```python
FACT_PROMPT_SYSTEM = (
    "You are a rigorous fact-checking assistant. Use ONLY the sources provided below.\n"
    "- You can ONLY return TWO possible verdicts: True OR Uncertain.\n"
    "- If the claim is supported by credible sources with clear evidence → verdict: True\n"
    "- If evidence is insufficient, conflicting, unclear, or off-topic → verdict: Uncertain\n"
    "- IMPORTANT: There is NO 'False' option. If you cannot confirm something as True, mark it as Uncertain.\n"
    # ... المزيد
)
```

**التعامل مع النتائج:**
```python
# تم تبسيط المنطق
if case.lower() in {"حقيقي", "true", "vrai", "verdadero", "pravda"}:
    result_emoji = "✅"
    result_text = "حقيقي" if lang == "ar" else "TRUE"
    tone = "confirming"
else:  # فقط uncertain
    result_emoji = "⚠️"
    result_text = "غير مؤكد" if lang == "ar" else "UNCERTAIN"
    tone = "uncertain"
```

---

## [v1.0.0] - 2024-10-10

### ✨ الإصدار الأول

- ✅ إضافة endpoints للتحقق من الأخبار
- ✅ إضافة endpoints لصياغة الأخبار والتغريدات
- ✅ دعم متعدد اللغات
- ✅ توثيق شامل
- ✅ أمثلة واختبارات

---

## دعم الإصدارات

| الإصدار | الحالة | نهاية الدعم |
|---------|--------|-------------|
| v2.x | ✅ مدعوم | - |
| v1.x | ⚠️ قديم | 2024-12-31 |

## ملاحظات الترقية

- يُنصح بالترقية إلى v2.0.0 في أقرب وقت
- الإصدار v1.x سيستمر دعمه حتى نهاية 2024
- بعد ذلك، سيتم إيقاف دعم v1.x تماماً

---

**للمزيد من المعلومات:**
- [README.md](README.md)
- [API_DOCUMENTATION_AR.md](API_DOCUMENTATION_AR.md)

