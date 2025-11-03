"""
Test file for news content validation
يختبر نظام التحقق من الأخبار على عناوين متنوعة
"""

import asyncio
import sys
import os

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from utils_async import is_news_content_async


# عناوين إخبارية صحيحة (يجب قبولها)
VALID_NEWS_HEADLINES = [
    "إنشاء قطار يربط الدوحة بالرياض",
    "وزارة الخارجية تعلن عن اتفاقية جديدة مع فرنسا",
    "رئيس الوزراء يلتقي نظيره البريطاني في لندن",
    "إطلاق مشروع بناء جسر جديد بين البحرين والسعودية",
    "وزارة التعليم تعلن عن مناهج جديدة للعام الدراسي",
    "قطر تعلن عن استضافة كأس العالم 2030",
    "انخفاض أسعار النفط في الأسواق العالمية",
    "مؤتمر قمة عربية في الرياض",
    "زلزال يضرب جنوب تركيا",
    "إطلاق قمر صناعي جديد للإمارات",
    "اتفاقية تجارية بين مصر والسودان",
    "افتتاح مطار جديد في الرياض",
    "وزير الصحة يعلن عن حملة تطعيم جديدة",
    "مباراة نهائي كأس آسيا بين قطر واليابان",
    "انطلاق قمة منظمة التعاون الإسلامي في جدة",
    "عاصفة ثلجية تضرب شمال أوروبا",
    "إعلان نتائج الانتخابات الرئاسية",
    "قمة دولية حول التغير المناخي",
    "اتفاقية سلام بين دولتين متحاربتين",
    "افتتاح خط مترو جديد في دبي",
]

# نصوص غير إخبارية (يجب رفضها)
INVALID_NON_NEWS = [
    "طريقة عمل المحشي",
    "كيف أتعلم البرمجة",
    "وصفة كعك العيد",
    "نصائح لإنقاص الوزن",
    "مرحبا كيف حالك",
    "شكرا لك على مساعدتك",
    "ما رأيك في الطقس اليوم؟",
    "ما هو أفضل وقت للنوم؟",
    "كيف تعمل محرك السيارة؟",
    "طريقة تحضير القهوة التركية",
    "ما هي فوائد الشاي الأخضر؟",
    "كيف أطور مهاراتي في اللغة الإنجليزية؟",
    "ما هو أفضل نظام غذائي للرياضيين؟",
    "طريقة زراعة الطماطم في المنزل",
    "ما هو معنى الحياة؟",
    "كيف تصنع بيتزا في المنزل",
    "نصائح للدراسة بفعالية",
    "ما هي أعراض الإنفلونزا؟",
    "كيف تختار الملابس المناسبة؟",
    "طريقة تنظيف المنزل بسرعة",
]


async def test_validation():
    """اختبار التحقق من العناوين"""
    
    print("=" * 80)
    print("اختبار نظام التحقق من الاخبار")
    print("=" * 80)
    
    # اختبار العناوين الإخبارية الصحيحة
    print("\n[+] اختبار العناوين الاخبارية (يجب قبولها):")
    print("-" * 80)
    
    passed_valid = 0
    failed_valid = 0
    
    for i, headline in enumerate(VALID_NEWS_HEADLINES, 1):
        try:
            is_valid, reason = await is_news_content_async(headline)
            status = "[OK]" if is_valid else "[X]"
            result_text = "قبلت" if is_valid else f"رفضت: {reason}"
            
            print(f"{i:2d}. {status} {headline[:60]:<60} → {result_text}")
            
            if is_valid:
                passed_valid += 1
            else:
                failed_valid += 1
        except Exception as e:
            print(f"{i:2d}. [ERROR] {headline[:60]:<60} -> خطأ: {str(e)}")
            failed_valid += 1
    
    # اختبار النصوص غير الإخبارية
    print("\n\n[-] اختبار النصوص غير الاخبارية (يجب رفضها):")
    print("-" * 80)
    
    passed_invalid = 0
    failed_invalid = 0
    
    for i, text in enumerate(INVALID_NON_NEWS, 1):
        try:
            is_valid, reason = await is_news_content_async(text)
            status = "[OK]" if not is_valid else "[X]"
            result_text = "رفضت ✓" if not is_valid else f"قبلت ✗ (يجب رفضها)"
            
            print(f"{i:2d}. {status} {text[:60]:<60} → {result_text}")
            
            if not is_valid:
                passed_invalid += 1
            else:
                failed_invalid += 1
        except Exception as e:
            print(f"{i:2d}. [ERROR] {text[:60]:<60} -> خطأ: {str(e)}")
            failed_invalid += 1
    
    # ملخص النتائج
    print("\n" + "=" * 80)
    print("ملخص النتائج:")
    print("=" * 80)
    print(f"\n[+] العناوين الاخبارية:")
    print(f"   - تم قبولها بشكل صحيح: {passed_valid}/{len(VALID_NEWS_HEADLINES)}")
    print(f"   - تم رفضها (خطأ):      {failed_valid}/{len(VALID_NEWS_HEADLINES)}")
    
    print(f"\n[-] النصوص غير الاخبارية:")
    print(f"   - تم رفضها بشكل صحيح:  {passed_invalid}/{len(INVALID_NON_NEWS)}")
    print(f"   - تم قبولها (خطأ):      {failed_invalid}/{len(INVALID_NON_NEWS)}")
    
    total_tests = len(VALID_NEWS_HEADLINES) + len(INVALID_NON_NEWS)
    total_passed = passed_valid + passed_invalid
    total_failed = failed_valid + failed_invalid
    
    print(f"\n[=] اجمالي:")
    print(f"   - النجاح: {total_passed}/{total_tests} ({total_passed*100/total_tests:.1f}%)")
    print(f"   - الفشل:  {total_failed}/{total_tests} ({total_failed*100/total_tests:.1f}%)")
    print("=" * 80)


async def test_specific_headlines():
    """اختبار عناوين محددة للمستخدم"""
    print("\n" + "=" * 80)
    print("اختبار عناوين محددة")
    print("=" * 80)
    
    test_cases = [
        "إنشاء قطار يربط الدوحة بالرياض",
        "طريقة عمل المحشي",
    ]
    
    for text in test_cases:
        print(f"\n[TEST] اختبار: {text}")
        try:
            is_valid, reason = await is_news_content_async(text)
            status = "[OK] قبلت" if is_valid else "[X] رفضت"
            print(f"   النتيجة: {status}")
            if reason:
                print(f"   السبب: {reason}")
        except Exception as e:
            print(f"   [ERROR] خطأ: {str(e)}")


if __name__ == "__main__":
    # تشغيل الاختبارات
    asyncio.run(test_validation())
    asyncio.run(test_specific_headlines())

