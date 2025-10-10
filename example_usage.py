"""
مثال توضيحي لاستخدام API التحقق من الأخبار وصياغة المحتوى

⚠️ ملاحظة هامة: النظام يدعم حالتين فقط:
   ✅ حقيقي (True)
   ⚠️ غير مؤكد (Uncertain)
   
   ❌ لا توجد حالة "كاذب" (False)

هذا الملف يوضح كيفية استخدام الـ endpoints الجديدة:
1. الفحص الأساسي للخبر
2. صياغة خبر من نتيجة الفحص (دون حفظ)
3. صياغة تغريدة من نتيجة الفحص (دون حفظ)
"""

import requests
import json

# عنوان الـ API (تأكد من تشغيل السيرفر أولاً)
BASE_URL = "http://localhost:8000/fact_check_with_openai"


def example_1_basic_fact_check():
    """
    مثال 1: الفحص الأساسي للخبر فقط
    """
    print("\n" + "="*60)
    print("مثال 1: الفحص الأساسي للخبر")
    print("="*60)
    
    url = f"{BASE_URL}/"
    payload = {
        "query": "تم افتتاح مطار جديد في الرياض اليوم"
    }
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    print(f"\n✅ الحالة: {result['case']}")
    print(f"\n📝 التحليل: {result['talk'][:200]}...")
    print(f"\n🔗 عدد المصادر: {len(result.get('sources', []))}")
    
    return result


def example_2_fact_check_with_news():
    """
    مثال 2: فحص الخبر مع صياغة مقال إخباري في خطوة واحدة
    """
    print("\n" + "="*60)
    print("مثال 2: فحص + صياغة خبر في خطوة واحدة")
    print("="*60)
    
    url = f"{BASE_URL}/"
    payload = {
        "query": "تم افتتاح مطار جديد في الرياض اليوم",
        "generate_news": True,
        "generate_tweet": True
    }
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    print(f"\n✅ الحالة: {result['case']}")
    print(f"\n📰 المقال الإخباري:\n{result.get('news_article', 'لا يوجد')}")
    print(f"\n🐦 التغريدة:\n{result.get('x_tweet', 'لا يوجد')}")
    
    return result


def example_3_separate_compose_news():
    """
    مثال 3: الفحص ثم صياغة الخبر بشكل منفصل
    (الطريقة الموصى بها - تعطيك تحكم أفضل)
    """
    print("\n" + "="*60)
    print("مثال 3: فحص ثم صياغة خبر بشكل منفصل")
    print("="*60)
    
    # الخطوة 1: فحص الخبر
    print("\n📍 الخطوة 1: فحص الخبر...")
    fact_check_url = f"{BASE_URL}/"
    fact_check_payload = {
        "query": "تم افتتاح مطار جديد في الرياض اليوم"
    }
    
    fact_check_response = requests.post(fact_check_url, json=fact_check_payload)
    fact_check_result = fact_check_response.json()
    
    print(f"✅ نتيجة الفحص: {fact_check_result['case']}")
    print(f"📝 التحليل: {fact_check_result['talk'][:150]}...")
    
    # الخطوة 2: صياغة الخبر من النتيجة (بدون حفظ)
    print("\n📍 الخطوة 2: صياغة الخبر من النتيجة...")
    compose_news_url = f"{BASE_URL}/compose_news/"
    compose_news_payload = {
        "claim_text": fact_check_payload["query"],
        "case": fact_check_result["case"],
        "talk": fact_check_result["talk"],
        "sources": fact_check_result.get("sources", []),
        "lang": "ar"
    }
    
    compose_news_response = requests.post(compose_news_url, json=compose_news_payload)
    compose_news_result = compose_news_response.json()
    
    print(f"\n📰 المقال المصاغ:\n{compose_news_result.get('news_article', 'لا يوجد')}")
    
    return compose_news_result


def example_4_separate_compose_tweet():
    """
    مثال 4: الفحص ثم صياغة تغريدة بشكل منفصل
    """
    print("\n" + "="*60)
    print("مثال 4: فحص ثم صياغة تغريدة بشكل منفصل")
    print("="*60)
    
    # الخطوة 1: فحص الخبر
    print("\n📍 الخطوة 1: فحص الخبر...")
    fact_check_url = f"{BASE_URL}/"
    fact_check_payload = {
        "query": "تم افتتاح مطار جديد في الرياض اليوم"
    }
    
    fact_check_response = requests.post(fact_check_url, json=fact_check_payload)
    fact_check_result = fact_check_response.json()
    
    print(f"✅ نتيجة الفحص: {fact_check_result['case']}")
    
    # الخطوة 2: صياغة التغريدة من النتيجة (بدون حفظ)
    print("\n📍 الخطوة 2: صياغة التغريدة من النتيجة...")
    compose_tweet_url = f"{BASE_URL}/compose_tweet/"
    compose_tweet_payload = {
        "claim_text": fact_check_payload["query"],
        "case": fact_check_result["case"],
        "talk": fact_check_result["talk"],
        "sources": fact_check_result.get("sources", []),
        "lang": "ar"
    }
    
    compose_tweet_response = requests.post(compose_tweet_url, json=compose_tweet_payload)
    compose_tweet_result = compose_tweet_response.json()
    
    print(f"\n🐦 التغريدة المصاغة:\n{compose_tweet_result.get('x_tweet', 'لا يوجد')}")
    print(f"\n📏 عدد الأحرف: {len(compose_tweet_result.get('x_tweet', ''))}")
    
    return compose_tweet_result


def example_5_complete_workflow():
    """
    مثال 5: سير عمل كامل - فحص ثم صياغة خبر وتغريدة
    """
    print("\n" + "="*60)
    print("مثال 5: سير عمل كامل")
    print("="*60)
    
    claim_text = "تم افتتاح مطار جديد في الرياض اليوم"
    
    # الخطوة 1: فحص
    print("\n📍 الخطوة 1: فحص الخبر...")
    fact_check_url = f"{BASE_URL}/"
    fact_check_response = requests.post(
        fact_check_url, 
        json={"query": claim_text}
    )
    fact_check_result = fact_check_response.json()
    
    print(f"✅ نتيجة الفحص: {fact_check_result['case']}")
    
    # الخطوة 2: صياغة خبر
    print("\n📍 الخطوة 2: صياغة خبر...")
    compose_news_url = f"{BASE_URL}/compose_news/"
    news_response = requests.post(
        compose_news_url,
        json={
            "claim_text": claim_text,
            "case": fact_check_result["case"],
            "talk": fact_check_result["talk"],
            "sources": fact_check_result.get("sources", []),
            "lang": "ar"
        }
    )
    news_result = news_response.json()
    
    print(f"📰 تم صياغة المقال بنجاح!")
    
    # الخطوة 3: صياغة تغريدة
    print("\n📍 الخطوة 3: صياغة تغريدة...")
    compose_tweet_url = f"{BASE_URL}/compose_tweet/"
    tweet_response = requests.post(
        compose_tweet_url,
        json={
            "claim_text": claim_text,
            "case": fact_check_result["case"],
            "talk": fact_check_result["talk"],
            "sources": fact_check_result.get("sources", []),
            "lang": "ar"
        }
    )
    tweet_result = tweet_response.json()
    
    print(f"🐦 تم صياغة التغريدة بنجاح!")
    
    # عرض النتائج النهائية
    print("\n" + "="*60)
    print("📊 النتائج النهائية")
    print("="*60)
    print(f"\n✅ حالة الفحص: {fact_check_result['case']}")
    print(f"\n📝 التحليل:\n{fact_check_result['talk']}")
    print(f"\n📰 المقال:\n{news_result.get('news_article', 'لا يوجد')}")
    print(f"\n🐦 التغريدة:\n{tweet_result.get('x_tweet', 'لا يوجد')}")
    print(f"\n🔗 عدد المصادر: {len(fact_check_result.get('sources', []))}")
    
    return {
        "fact_check": fact_check_result,
        "news": news_result,
        "tweet": tweet_result
    }


if __name__ == "__main__":
    print("🚀 أمثلة استخدام API التحقق من الأخبار")
    print("\nتأكد من تشغيل السيرفر أولاً: python manage.py runserver")
    print("\nاختر مثالاً لتشغيله:")
    print("1. الفحص الأساسي")
    print("2. فحص + صياغة في خطوة واحدة")
    print("3. فحص ثم صياغة خبر بشكل منفصل (موصى به)")
    print("4. فحص ثم صياغة تغريدة بشكل منفصل")
    print("5. سير عمل كامل (فحص + خبر + تغريدة)")
    print("6. تشغيل جميع الأمثلة")
    
    choice = input("\nأدخل رقم المثال (1-6): ").strip()
    
    try:
        if choice == "1":
            example_1_basic_fact_check()
        elif choice == "2":
            example_2_fact_check_with_news()
        elif choice == "3":
            example_3_separate_compose_news()
        elif choice == "4":
            example_4_separate_compose_tweet()
        elif choice == "5":
            example_5_complete_workflow()
        elif choice == "6":
            example_1_basic_fact_check()
            example_2_fact_check_with_news()
            example_3_separate_compose_news()
            example_4_separate_compose_tweet()
            example_5_complete_workflow()
        else:
            print("❌ اختيار غير صحيح!")
    except requests.exceptions.ConnectionError:
        print("\n❌ خطأ: تأكد من تشغيل السيرفر أولاً!")
        print("   قم بتشغيل: python manage.py runserver")
    except Exception as e:
        print(f"\n❌ حدث خطأ: {e}")

