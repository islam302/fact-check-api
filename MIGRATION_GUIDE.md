# دليل الترقية من v1.x إلى v2.0

## 📋 نظرة عامة

هذا الدليل يساعدك في ترقية تطبيقك من الإصدار v1.x (الذي يدعم 3 حالات) إلى v2.0 (الذي يدعم حالتين فقط).

## 🔴 التغيير الرئيسي

تم إزالة حالة **"كاذب" (False)** من النظام. الآن يدعم النظام حالتين فقط:
- ✅ **حقيقي (True)**
- ⚠️ **غير مؤكد (Uncertain)**

## 🚀 خطوات الترقية

### الخطوة 1: فهم التغيير

**قبل (v1.x):**
```json
{
  "case": "حقيقي"  // أو "كاذب" أو "غير مؤكد"
}
```

**بعد (v2.0):**
```json
{
  "case": "حقيقي"  // أو "غير مؤكد" فقط
}
```

### الخطوة 2: تحديث كود Frontend

#### React/JavaScript

**قبل:**
```javascript
function FactCheckResult({ case: caseValue }) {
  if (caseValue === 'حقيقي' || caseValue === 'True') {
    return <div className="true">✅ صحيح</div>;
  } else if (caseValue === 'كاذب' || caseValue === 'False') {
    return <div className="false">❌ كاذب</div>;
  } else {
    return <div className="uncertain">⚠️ غير مؤكد</div>;
  }
}
```

**بعد:**
```javascript
function FactCheckResult({ case: caseValue }) {
  if (caseValue === 'حقيقي' || caseValue === 'True') {
    return <div className="true">✅ صحيح</div>;
  } else {
    // فقط حالة واحدة أخرى: غير مؤكد
    return <div className="uncertain">⚠️ غير مؤكد</div>;
  }
}
```

#### Vue.js

**قبل:**
```vue
<template>
  <div :class="resultClass">
    <span v-if="case === 'حقيقي'">✅ صحيح</span>
    <span v-else-if="case === 'كاذب'">❌ كاذب</span>
    <span v-else>⚠️ غير مؤكد</span>
  </div>
</template>
```

**بعد:**
```vue
<template>
  <div :class="resultClass">
    <span v-if="case === 'حقيقي'">✅ صحيح</span>
    <span v-else>⚠️ غير مؤكد</span>
  </div>
</template>
```

#### Angular

**قبل:**
```typescript
getCaseIcon(caseValue: string): string {
  switch(caseValue) {
    case 'حقيقي': return '✅';
    case 'كاذب': return '❌';
    case 'غير مؤكد': return '⚠️';
    default: return '⚠️';
  }
}
```

**بعد:**
```typescript
getCaseIcon(caseValue: string): string {
  return caseValue === 'حقيقي' ? '✅' : '⚠️';
}
```

### الخطوة 3: تحديث CSS

**قبل:**
```css
.fact-check-result.true {
  background: #d4edda;
  color: #155724;
}

.fact-check-result.false {
  background: #f8d7da;
  color: #721c24;
}

.fact-check-result.uncertain {
  background: #fff3cd;
  color: #856404;
}
```

**بعد:**
```css
.fact-check-result.true {
  background: #d4edda;
  color: #155724;
}

/* يمكن إزالة false أو إعادة تسميته لـ uncertain */
.fact-check-result.uncertain {
  background: #fff3cd;
  color: #856404;
}
```

### الخطوة 4: تحديث قاعدة البيانات

إذا كنت تحفظ النتائج في قاعدة بيانات:

#### SQL

```sql
-- تحديث جميع السجلات "كاذب" إلى "غير مؤكد"
UPDATE fact_checks 
SET case_status = 'غير مؤكد' 
WHERE case_status = 'كاذب';

-- للإنجليزية
UPDATE fact_checks 
SET case_status = 'Uncertain' 
WHERE case_status = 'False';

-- للفرنسية
UPDATE fact_checks 
SET case_status = 'Incertain' 
WHERE case_status = 'Faux';

-- يمكنك أيضاً إضافة قيد CHECK
ALTER TABLE fact_checks
ADD CONSTRAINT chk_case_status 
CHECK (case_status IN ('حقيقي', 'غير مؤكد'));
```

#### MongoDB

```javascript
// تحديث جميع المستندات
db.fact_checks.updateMany(
  { case: 'كاذب' },
  { $set: { case: 'غير مؤكد' } }
);

// للتأكد من النجاح
db.fact_checks.find({ case: 'كاذب' }).count(); // يجب أن يرجع 0
```

#### PostgreSQL

```sql
-- إنشاء ENUM جديد
CREATE TYPE case_status_v2 AS ENUM ('حقيقي', 'غير مؤكد');

-- تحديث العمود
ALTER TABLE fact_checks 
ALTER COLUMN case_status TYPE case_status_v2 
USING (
  CASE 
    WHEN case_status = 'كاذب' THEN 'غير مؤكد'::case_status_v2
    ELSE case_status::text::case_status_v2
  END
);
```

### الخطوة 5: تحديث الاختبارات

#### Jest/Vitest

**قبل:**
```javascript
describe('FactCheck', () => {
  it('should handle true case', () => {
    expect(getResult('حقيقي')).toBe('✅ صحيح');
  });
  
  it('should handle false case', () => {
    expect(getResult('كاذب')).toBe('❌ كاذب');
  });
  
  it('should handle uncertain case', () => {
    expect(getResult('غير مؤكد')).toBe('⚠️ غير مؤكد');
  });
});
```

**بعد:**
```javascript
describe('FactCheck', () => {
  it('should handle true case', () => {
    expect(getResult('حقيقي')).toBe('✅ صحيح');
  });
  
  it('should handle uncertain case', () => {
    expect(getResult('غير مؤكد')).toBe('⚠️ غير مؤكد');
  });
  
  // حذف اختبار false
});
```

### الخطوة 6: تحديث التوثيق

تأكد من تحديث:
- 📝 توثيق API الخاص بك
- 📚 دليل المستخدم
- 🎓 أمثلة الكود
- 📊 لوحات التحكم (Dashboards)

### الخطوة 7: إعلام المستخدمين

إذا كان لديك واجهة مستخدم، أضف إشعار:

```javascript
// مثال Toast Notification
function showMigrationNotice() {
  toast.info(
    'تحديث: لم يعد النظام يصنف الأخبار كـ"كاذبة". ' +
    'بدلاً من ذلك، يتم تصنيفها كـ"غير مؤكدة" إذا لم يتم التأكد من صحتها.',
    { duration: 10000 }
  );
}
```

## 🔧 أمثلة الترقية الكاملة

### مثال: تطبيق React كامل

```javascript
// قبل
import React from 'react';

function NewsCard({ article }) {
  const getCaseColor = (caseValue) => {
    if (caseValue === 'حقيقي') return 'green';
    if (caseValue === 'كاذب') return 'red';
    return 'yellow';
  };

  const getCaseText = (caseValue) => {
    if (caseValue === 'حقيقي') return '✅ صحيح';
    if (caseValue === 'كاذب') return '❌ كاذب';
    return '⚠️ غير مؤكد';
  };

  return (
    <div className={`card ${getCaseColor(article.case)}`}>
      <h3>{article.title}</h3>
      <p>{article.content}</p>
      <div className="status">{getCaseText(article.case)}</div>
    </div>
  );
}

export default NewsCard;
```

```javascript
// بعد
import React from 'react';

function NewsCard({ article }) {
  const isTrue = article.case === 'حقيقي' || article.case === 'True';
  
  return (
    <div className={`card ${isTrue ? 'green' : 'yellow'}`}>
      <h3>{article.title}</h3>
      <p>{article.content}</p>
      <div className="status">
        {isTrue ? '✅ صحيح' : '⚠️ غير مؤكد'}
      </div>
    </div>
  );
}

export default NewsCard;
```

### مثال: API Client

```python
# قبل
class FactCheckClient:
    def check_news(self, text):
        response = requests.post(self.api_url, json={'query': text})
        result = response.json()
        
        if result['case'] == 'حقيقي':
            self.log_true(text)
        elif result['case'] == 'كاذب':
            self.log_false(text)
        else:
            self.log_uncertain(text)
        
        return result

    def log_false(self, text):
        logger.warning(f"False news detected: {text}")
```

```python
# بعد
class FactCheckClient:
    def check_news(self, text):
        response = requests.post(self.api_url, json={'query': text})
        result = response.json()
        
        if result['case'] == 'حقيقي':
            self.log_true(text)
        else:
            # كل شيء آخر هو غير مؤكد
            self.log_uncertain(text)
        
        return result

    # حذف log_false - لم تعد مطلوبة
```

## ⚠️ أخطاء شائعة

### خطأ 1: افتراض وجود 3 حالات

```javascript
// ❌ خطأ
const cases = ['حقيقي', 'كاذب', 'غير مؤكد'];

// ✅ صحيح
const cases = ['حقيقي', 'غير مؤكد'];
```

### خطأ 2: استخدام switch مع 3 حالات

```javascript
// ❌ خطأ
switch(result.case) {
  case 'حقيقي': return '✅';
  case 'كاذب': return '❌';
  case 'غير مؤكد': return '⚠️';
}

// ✅ صحيح
result.case === 'حقيقي' ? '✅' : '⚠️'
```

### خطأ 3: معالجة "كاذب" في الكود الجديد

```javascript
// ❌ خطأ - لا تتعامل مع "كاذب" بعد الترقية
if (case === 'كاذب') {
  // هذا الكود لن ينفذ أبداً في v2.0
}

// ✅ صحيح
if (case !== 'حقيقي') {
  // معالجة كل ما ليس حقيقي كـ "غير مؤكد"
}
```

## ✅ قائمة التحقق

استخدم هذه القائمة للتأكد من اكتمال الترقية:

- [ ] قراءة CHANGELOG.md
- [ ] فهم التغيير الأساسي
- [ ] تحديث كود Frontend
- [ ] تحديث CSS/Styles
- [ ] تحديث قاعدة البيانات (إن وجدت)
- [ ] تحديث الاختبارات
- [ ] حذف أو تحديث الأمثلة القديمة
- [ ] تحديث التوثيق
- [ ] اختبار جميع المسارات
- [ ] إعلام الفريق/المستخدمين
- [ ] نشر التحديث

## 🆘 الدعم

إذا واجهت مشاكل أثناء الترقية:

1. راجع [CHANGELOG.md](CHANGELOG.md)
2. راجع [API_DOCUMENTATION_AR.md](API_DOCUMENTATION_AR.md)
3. افحص أمثلة الكود في [example_usage.py](example_usage.py)
4. تحقق من Postman Collection

## 📊 مقارنة الإصدارات

| الميزة | v1.x | v2.0 |
|--------|------|------|
| عدد الحالات | 3 | 2 |
| حقيقي (True) | ✅ | ✅ |
| كاذب (False) | ✅ | ❌ |
| غير مؤكد (Uncertain) | ✅ | ✅ |
| الأداء | عادي | محسّن |
| الدقة الأخلاقية | متوسط | عالي |

## 🎯 الخلاصة

الترقية إلى v2.0 بسيطة ومباشرة:
1. استبدل جميع معالجات "كاذب" بـ "غير مؤكد"
2. بسّط المنطق من 3 حالات إلى 2
3. حدّث قاعدة البيانات إذا لزم الأمر
4. اختبر بشكل شامل

**الفائدة:** نظام أكثر مسؤولية وأخلاقية في التعامل مع الأخبار! 🎉

