# اختبار Endpoints الجديدة
# تأكد من تشغيل السيرفر أولاً: python manage.py runserver

$BASE_URL = "http://localhost:8000/fact_check_with_openai"

Write-Host "🚀 اختبار Endpoints الجديدة" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# 1. اختبار الفحص الأساسي
Write-Host "`n📍 اختبار 1: الفحص الأساسي" -ForegroundColor Blue
Write-Host "================================" -ForegroundColor Blue

$body1 = @{
    query = "تم افتتاح مطار جديد في الرياض اليوم"
} | ConvertTo-Json

$response1 = Invoke-RestMethod -Uri "$BASE_URL/" -Method Post -Body $body1 -ContentType "application/json"
$response1 | ConvertTo-Json -Depth 10

Write-Host "`n✅ اختبار 1 انتهى" -ForegroundColor Green
Read-Host "اضغط Enter للمتابعة..."

# 2. اختبار الفحص مع صياغة الخبر والتغريدة
Write-Host "`n📍 اختبار 2: فحص + صياغة خبر وتغريدة في خطوة واحدة" -ForegroundColor Blue
Write-Host "================================" -ForegroundColor Blue

$body2 = @{
    query = "تم افتتاح مطار جديد في الرياض اليوم"
    generate_news = $true
    generate_tweet = $true
} | ConvertTo-Json

$response2 = Invoke-RestMethod -Uri "$BASE_URL/" -Method Post -Body $body2 -ContentType "application/json"
$response2 | ConvertTo-Json -Depth 10

Write-Host "`n✅ اختبار 2 انتهى" -ForegroundColor Green
Read-Host "اضغط Enter للمتابعة..."

# 3. اختبار صياغة الخبر من النتيجة
Write-Host "`n📍 اختبار 3: صياغة خبر من نتيجة الفحص" -ForegroundColor Blue
Write-Host "================================" -ForegroundColor Blue

$body3 = @{
    claim_text = "تم افتتاح مطار جديد في الرياض اليوم"
    case = "حقيقي"
    talk = "تم التأكد من صحة الخبر من خلال مصادر رسمية موثوقة. أعلنت الهيئة العامة للطيران المدني عن افتتاح المطار الجديد في الرياض، والذي يعد أحد أكبر المطارات في المنطقة."
    sources = @(
        @{
            title = "الهيئة العامة للطيران المدني تعلن افتتاح المطار"
            url = "https://example.com/news1"
            snippet = "أعلنت الهيئة العامة للطيران المدني عن افتتاح المطار الجديد"
        }
    )
    lang = "ar"
} | ConvertTo-Json -Depth 10

Write-Host "`nملاحظة: النظام يدعم حالتين فقط - حقيقي وغير مؤكد (لا توجد حالة كاذب)" -ForegroundColor Yellow

$response3 = Invoke-RestMethod -Uri "$BASE_URL/compose_news/" -Method Post -Body $body3 -ContentType "application/json"
$response3 | ConvertTo-Json -Depth 10

Write-Host "`n✅ اختبار 3 انتهى" -ForegroundColor Green
Read-Host "اضغط Enter للمتابعة..."

# 4. اختبار صياغة التغريدة من النتيجة
Write-Host "`n📍 اختبار 4: صياغة تغريدة من نتيجة الفحص" -ForegroundColor Blue
Write-Host "================================" -ForegroundColor Blue

$body4 = @{
    claim_text = "تم افتتاح مطار جديد في الرياض اليوم"
    case = "حقيقي"
    talk = "تم التأكد من صحة الخبر من خلال مصادر رسمية موثوقة."
    sources = @(
        @{
            title = "الهيئة العامة للطيران المدني تعلن افتتاح المطار"
            url = "https://example.com/news1"
            snippet = "أعلنت الهيئة العامة للطيران المدني عن افتتاح المطار الجديد"
        }
    )
    lang = "ar"
} | ConvertTo-Json -Depth 10

$response4 = Invoke-RestMethod -Uri "$BASE_URL/compose_tweet/" -Method Post -Body $body4 -ContentType "application/json"
$response4 | ConvertTo-Json -Depth 10

Write-Host "`n✅ اختبار 4 انتهى" -ForegroundColor Green

Write-Host "`n🎉 اكتملت جميع الاختبارات!" -ForegroundColor Yellow

