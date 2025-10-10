#!/bin/bash

# اختبار Endpoints الجديدة
# تأكد من تشغيل السيرفر أولاً: python manage.py runserver

BASE_URL="http://localhost:8000/fact_check_with_openai"

echo "🚀 اختبار Endpoints الجديدة"
echo "================================"

# ألوان للـ output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. اختبار الفحص الأساسي
echo -e "\n${BLUE}📍 اختبار 1: الفحص الأساسي${NC}"
echo "================================"
curl -X POST "${BASE_URL}/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "تم افتتاح مطار جديد في الرياض اليوم"
  }' | python -m json.tool

echo -e "\n${GREEN}✅ اختبار 1 انتهى${NC}"
read -p "اضغط Enter للمتابعة..."

# 2. اختبار الفحص مع صياغة الخبر والتغريدة
echo -e "\n${BLUE}📍 اختبار 2: فحص + صياغة خبر وتغريدة في خطوة واحدة${NC}"
echo "================================"
curl -X POST "${BASE_URL}/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "تم افتتاح مطار جديد في الرياض اليوم",
    "generate_news": true,
    "generate_tweet": true
  }' | python -m json.tool

echo -e "\n${GREEN}✅ اختبار 2 انتهى${NC}"
read -p "اضغط Enter للمتابعة..."

# 3. اختبار صياغة الخبر من النتيجة
echo -e "\n${BLUE}📍 اختبار 3: صياغة خبر من نتيجة الفحص${NC}"
echo "================================"
curl -X POST "${BASE_URL}/compose_news/" \
  -H "Content-Type: application/json" \
  -d '{
    "claim_text": "تم افتتاح مطار جديد في الرياض اليوم",
    "case": "حقيقي",
    "talk": "تم التأكد من صحة الخبر من خلال مصادر رسمية موثوقة. أعلنت الهيئة العامة للطيران المدني عن افتتاح المطار الجديد في الرياض، والذي يعد أحد أكبر المطارات في المنطقة. يأتي هذا الافتتاح ضمن خطط توسعة البنية التحتية للنقل الجوي في المملكة.",
    "sources": [
      {
        "title": "الهيئة العامة للطيران المدني تعلن افتتاح المطار",
        "url": "https://example.com/news1",
        "snippet": "أعلنت الهيئة العامة للطيران المدني عن افتتاح المطار الجديد"
      },
      {
        "title": "افتتاح مطار الرياض الجديد",
        "url": "https://example.com/news2",
        "snippet": "شهد اليوم افتتاح رسمي للمطار الجديد في الرياض"
      }
    ],
    "lang": "ar"
  }' | python -m json.tool

echo -e "\n${GREEN}✅ اختبار 3 انتهى${NC}"
read -p "اضغط Enter للمتابعة..."

# 4. اختبار صياغة التغريدة من النتيجة
echo -e "\n${BLUE}📍 اختبار 4: صياغة تغريدة من نتيجة الفحص${NC}"
echo "================================"
curl -X POST "${BASE_URL}/compose_tweet/" \
  -H "Content-Type: application/json" \
  -d '{
    "claim_text": "تم افتتاح مطار جديد في الرياض اليوم",
    "case": "حقيقي",
    "talk": "تم التأكد من صحة الخبر من خلال مصادر رسمية موثوقة. أعلنت الهيئة العامة للطيران المدني عن افتتاح المطار الجديد في الرياض.",
    "sources": [
      {
        "title": "الهيئة العامة للطيران المدني تعلن افتتاح المطار",
        "url": "https://example.com/news1",
        "snippet": "أعلنت الهيئة العامة للطيران المدني عن افتتاح المطار الجديد"
      }
    ],
    "lang": "ar"
  }' | python -m json.tool

echo -e "\n${GREEN}✅ اختبار 4 انتهى${NC}"

# 5. اختبار مع نتيجة غير مؤكدة
echo -e "\n${BLUE}📍 اختبار 5: صياغة تغريدة من نتيجة غير مؤكدة${NC}"
echo "================================"
echo -e "${YELLOW}ملاحظة: النظام يدعم حالتين فقط - حقيقي وغير مؤكد (لا توجد حالة كاذب)${NC}"
curl -X POST "${BASE_URL}/compose_tweet/" \
  -H "Content-Type: application/json" \
  -d '{
    "claim_text": "ستنطلق رحلة فضائية جديدة الأسبوع القادم",
    "case": "غير مؤكد",
    "talk": "لم يتم العثور على معلومات كافية لتأكيد هذا الخبر. لا توجد تصريحات رسمية من وكالات الفضاء المعنية بهذا الشأن في الوقت الحالي.",
    "sources": [],
    "lang": "ar"
  }' | python -m json.tool

echo -e "\n${GREEN}✅ اختبار 5 انتهى${NC}"

echo -e "\n${YELLOW}🎉 اكتملت جميع الاختبارات!${NC}"

