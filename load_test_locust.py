"""
Locust Load Testing File
Run with: locust -f load_test_locust.py --host=http://localhost:8000

This provides a web UI for load testing with real-time statistics
Access the UI at: http://localhost:8089
"""
from locust import HttpUser, task, between
import random

# Test queries
TEST_QUERIES = [
    "أعلنت وكالة الفضاء الأمريكية ناسا عن اكتشاف كوكب جديد",
    "الرئيس الأمريكي يزور المملكة العربية السعودية",
    "ارتفاع أسعار النفط إلى مستويات قياسية جديدة",
    "منظمة الصحة العالمية تحذر من فيروس جديد",
    "البنك المركزي يرفع أسعار الفائدة",
    "شركة تسلا تطلق سيارة كهربائية جديدة",
    "الأمم المتحدة تعقد قمة طارئة للمناخ",
    "اكتشاف علاج جديد لمرض السكري",
    "افتتاح أكبر مطار في الشرق الأوسط",
    "إطلاق قمر صناعي جديد للاتصالات",
]


class FactCheckUser(HttpUser):
    """Simulates a user checking facts"""
    
    # Wait between 1-5 seconds between tasks
    wait_time = between(1, 5)
    
    @task(3)  # Weight 3: Most common - just fact check
    def check_fact_simple(self):
        """Simple fact check without content generation"""
        query = random.choice(TEST_QUERIES)
        
        self.client.post(
            "/fact_check_with_openai/",
            json={
                "query": query,
                "generate_news": False,
                "generate_tweet": False,
                "preserve_sources": False
            },
            name="Fact Check (Simple)"
        )
    
    @task(2)  # Weight 2: Common - fact check with news
    def check_fact_with_news(self):
        """Fact check with news article generation"""
        query = random.choice(TEST_QUERIES)
        
        self.client.post(
            "/fact_check_with_openai/",
            json={
                "query": query,
                "generate_news": True,
                "generate_tweet": False,
                "preserve_sources": True
            },
            name="Fact Check + News"
        )
    
    @task(1)  # Weight 1: Less common - fact check with everything
    def check_fact_full(self):
        """Full fact check with all features"""
        query = random.choice(TEST_QUERIES)
        
        self.client.post(
            "/fact_check_with_openai/",
            json={
                "query": query,
                "generate_news": True,
                "generate_tweet": True,
                "preserve_sources": True
            },
            name="Fact Check (Full)"
        )
    
    def on_start(self):
        """Called when a simulated user starts"""
        print(f"🚀 New user started")
    
    def on_stop(self):
        """Called when a simulated user stops"""
        print(f"🛑 User stopped")


"""
USAGE INSTRUCTIONS:

1. Start your Django server:
   python manage.py runserver

2. In another terminal, run Locust:
   locust -f load_test_locust.py --host=http://localhost:8000

3. Open browser and go to:
   http://localhost:8089

4. Configure the test:
   - Number of users: Start with 10
   - Spawn rate: 1-2 users per second
   - Host: http://localhost:8000

5. Click "Start swarming" to begin the test

6. Watch the real-time statistics:
   - Requests per second
   - Response times (average, min, max)
   - Failures
   - Number of users

RECOMMENDED TESTS:

Test 1: Light load (2-5 users)
- See how the system performs normally

Test 2: Medium load (10-15 users)
- Test concurrent capacity

Test 3: Heavy load (20-30 users)
- Find the breaking point

Test 4: Spike test
- Start with 5 users
- Suddenly increase to 20 users
- See how system handles sudden load

MONITORING:
- Watch response times
- Check failure rate
- Monitor server resources (CPU, RAM)
- Note when response times start increasing significantly
"""

