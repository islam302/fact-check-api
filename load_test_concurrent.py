"""
Load Testing Script - Test concurrent requests to fact-checking API
This script simulates multiple users sending requests at the same time
"""
import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import List, Dict
import statistics

# Configuration
API_URL = "http://localhost:8000/fact_check_with_openai/"
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


class LoadTester:
    def __init__(self, api_url: str, num_concurrent_users: int = 10):
        self.api_url = api_url
        self.num_concurrent_users = num_concurrent_users
        self.results = []
        self.errors = []
        
    async def send_request(self, session: aiohttp.ClientSession, user_id: int, query: str) -> Dict:
        """Send a single request and measure response time"""
        start_time = time.time()
        
        try:
            payload = {
                "query": query,
                "generate_news": True,
                "generate_tweet": True,
                "preserve_sources": True
            }
            
            print(f"👤 User {user_id}: Sending request at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
            
            async with session.post(
                self.api_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)  # 2 minutes timeout
            ) as response:
                end_time = time.time()
                duration = end_time - start_time
                
                if response.status == 200:
                    data = await response.json()
                    result = {
                        "user_id": user_id,
                        "query": query,
                        "status": "success",
                        "duration": duration,
                        "response_time": f"{duration:.2f}s",
                        "case": data.get("case", "N/A"),
                        "sources_count": len(data.get("sources", [])),
                        "has_news": bool(data.get("news_article")),
                        "has_tweet": bool(data.get("x_tweet")),
                        "timestamp": datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    }
                    print(f"✅ User {user_id}: Completed in {duration:.2f}s")
                    return result
                else:
                    end_time = time.time()
                    duration = end_time - start_time
                    error = {
                        "user_id": user_id,
                        "query": query,
                        "status": "error",
                        "error": f"HTTP {response.status}",
                        "duration": duration,
                        "timestamp": datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    }
                    print(f"❌ User {user_id}: Error - HTTP {response.status}")
                    return error
                    
        except asyncio.TimeoutError:
            end_time = time.time()
            duration = end_time - start_time
            error = {
                "user_id": user_id,
                "query": query,
                "status": "timeout",
                "error": "Request timeout (>120s)",
                "duration": duration,
                "timestamp": datetime.now().strftime('%H:%M:%S.%f')[:-3]
            }
            print(f"⏱️  User {user_id}: Timeout after {duration:.2f}s")
            return error
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            error = {
                "user_id": user_id,
                "query": query,
                "status": "error",
                "error": str(e),
                "duration": duration,
                "timestamp": datetime.now().strftime('%H:%M:%S.%f')[:-3]
            }
            print(f"❌ User {user_id}: Exception - {str(e)}")
            return error
    
    async def run_concurrent_test(self):
        """Run concurrent load test"""
        print("=" * 100)
        print(f"🚀 LOAD TEST - {self.num_concurrent_users} CONCURRENT USERS")
        print("=" * 100)
        print(f"API URL: {self.api_url}")
        print(f"Test queries: {len(TEST_QUERIES)} different queries")
        print(f"Concurrent users: {self.num_concurrent_users}")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 100)
        print()
        
        # Create tasks for concurrent requests
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(self.num_concurrent_users):
                query = TEST_QUERIES[i % len(TEST_QUERIES)]
                task = self.send_request(session, i + 1, query)
                tasks.append(task)
            
            # Start all requests at the same time
            print(f"⏱️  Starting {self.num_concurrent_users} requests simultaneously...")
            test_start = time.time()
            
            results = await asyncio.gather(*tasks)
            
            test_end = time.time()
            total_duration = test_end - test_start
            
            # Analyze results
            self.analyze_results(results, total_duration)
    
    def analyze_results(self, results: List[Dict], total_duration: float):
        """Analyze and display test results"""
        print()
        print("=" * 100)
        print("📊 TEST RESULTS ANALYSIS")
        print("=" * 100)
        
        successful = [r for r in results if r["status"] == "success"]
        errors = [r for r in results if r["status"] == "error"]
        timeouts = [r for r in results if r["status"] == "timeout"]
        
        # Basic statistics
        print(f"\n📈 Basic Statistics:")
        print(f"   Total requests: {len(results)}")
        print(f"   ✅ Successful: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
        print(f"   ❌ Errors: {len(errors)} ({len(errors)/len(results)*100:.1f}%)")
        print(f"   ⏱️  Timeouts: {len(timeouts)} ({len(timeouts)/len(results)*100:.1f}%)")
        
        # Response time statistics
        if successful:
            durations = [r["duration"] for r in successful]
            print(f"\n⏱️  Response Time Statistics (successful requests):")
            print(f"   Fastest: {min(durations):.2f}s")
            print(f"   Slowest: {max(durations):.2f}s")
            print(f"   Average: {statistics.mean(durations):.2f}s")
            print(f"   Median: {statistics.median(durations):.2f}s")
            if len(durations) > 1:
                print(f"   Std Dev: {statistics.stdev(durations):.2f}s")
        
        # Total test duration
        print(f"\n🕐 Total Test Duration:")
        print(f"   {total_duration:.2f}s ({total_duration/60:.2f} minutes)")
        
        # Throughput
        print(f"\n📊 Throughput:")
        print(f"   Requests per second: {len(results)/total_duration:.2f} req/s")
        if successful:
            print(f"   Successful per second: {len(successful)/total_duration:.2f} req/s")
        
        # Concurrent capacity analysis
        print(f"\n🎯 Concurrent Capacity Analysis:")
        print(f"   Tested with: {len(results)} concurrent users")
        
        if successful:
            avg_duration = statistics.mean([r["duration"] for r in successful])
            
            if len(successful) == len(results):
                print(f"   ✅ Server handled all {len(results)} concurrent requests successfully!")
                print(f"   ✅ Average response time: {avg_duration:.2f}s")
                
                if avg_duration <= 20:
                    print(f"   ✅ EXCELLENT: Response times are good (≤20s)")
                    print(f"   💡 Server can likely handle {len(results)} or slightly more concurrent users")
                elif avg_duration <= 40:
                    print(f"   ⚠️  ACCEPTABLE: Response times are acceptable (20-40s)")
                    print(f"   💡 Server is at its limit with {len(results)} concurrent users")
                else:
                    print(f"   ❌ SLOW: Response times are too slow (>40s)")
                    print(f"   💡 Server is overloaded with {len(results)} concurrent users")
            else:
                print(f"   ⚠️  Some requests failed or timed out")
                print(f"   💡 Server capacity: ~{len(successful)} concurrent users")
        
        # Detailed results table
        print(f"\n📋 Detailed Results:")
        print("-" * 100)
        print(f"{'User':<6} {'Status':<10} {'Duration':<12} {'Case':<15} {'Sources':<8} {'News':<6} {'Tweet':<6}")
        print("-" * 100)
        
        for r in sorted(results, key=lambda x: x["user_id"]):
            status_icon = "✅" if r["status"] == "success" else "❌" if r["status"] == "error" else "⏱️"
            duration = f"{r['duration']:.2f}s"
            case = r.get("case", "N/A")[:14] if r["status"] == "success" else r.get("error", "N/A")[:14]
            sources = str(r.get("sources_count", "-")) if r["status"] == "success" else "-"
            news = "✅" if r.get("has_news") else "❌"
            tweet = "✅" if r.get("has_tweet") else "❌"
            
            print(f"{status_icon} {r['user_id']:<4} {r['status']:<10} {duration:<12} {case:<15} {sources:<8} {news:<6} {tweet:<6}")
        
        print("-" * 100)
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        
        if len(successful) == len(results) and statistics.mean([r["duration"] for r in successful]) <= 20:
            print(f"   ✅ Your server is performing EXCELLENT with {len(results)} concurrent users!")
            print(f"   ✅ You can safely handle {len(results)} or slightly more concurrent users")
            print(f"   💡 Consider testing with {len(results) + 5} users to find the limit")
        elif len(successful) >= len(results) * 0.8:
            print(f"   ⚠️  Your server is at its capacity with {len(results)} concurrent users")
            print(f"   💡 Current safe capacity: ~{len(successful)} concurrent users")
            print(f"   💡 Consider upgrading if you need to handle more users")
        else:
            print(f"   ❌ Your server is overloaded with {len(results)} concurrent users")
            print(f"   💡 Current safe capacity: ~{len(successful)} concurrent users")
            print(f"   ⚠️  Recommended: Upgrade server or implement load balancing")
        
        # Server recommendation
        print(f"\n🖥️  Server Recommendations:")
        capacity = len(successful)
        
        if capacity <= 4:
            print(f"   Current capacity: ~{capacity} concurrent users")
            print(f"   📦 Recommended: Standard (2 GB RAM, 1 CPU) - $25/month")
        elif capacity <= 8:
            print(f"   Current capacity: ~{capacity} concurrent users")
            print(f"   📦 Recommended: Pro (4 GB RAM, 2 CPU) - $85/month")
        elif capacity <= 15:
            print(f"   Current capacity: ~{capacity} concurrent users")
            print(f"   📦 Recommended: Pro Plus (8 GB RAM, 4 CPU) - $175/month")
        elif capacity <= 25:
            print(f"   Current capacity: ~{capacity} concurrent users")
            print(f"   📦 Recommended: Pro Max (16 GB RAM, 4 CPU) - $225/month")
        else:
            print(f"   Current capacity: ~{capacity} concurrent users")
            print(f"   📦 Recommended: Pro Ultra (32 GB RAM, 8 CPU) - $450/month")
            if capacity >= 50:
                print(f"   💡 Or consider: Load Balancer with multiple servers")
        
        print()
        print("=" * 100)
        
        # Save results to file
        self.save_results(results, total_duration)
    
    def save_results(self, results: List[Dict], total_duration: float):
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"load_test_results_{timestamp}.json"
        
        report = {
            "test_info": {
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "api_url": self.api_url,
                "concurrent_users": self.num_concurrent_users,
                "total_duration": total_duration,
            },
            "summary": {
                "total_requests": len(results),
                "successful": len([r for r in results if r["status"] == "success"]),
                "errors": len([r for r in results if r["status"] == "error"]),
                "timeouts": len([r for r in results if r["status"] == "timeout"]),
            },
            "results": results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Results saved to: {filename}")


async def main():
    """Main test function"""
    print()
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║          FACT-CHECK API LOAD TESTING TOOL                     ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    
    # Get configuration from user
    try:
        num_users = input("Enter number of concurrent users to test (default: 10): ").strip()
        num_users = int(num_users) if num_users else 10
    except ValueError:
        num_users = 10
        print("Invalid input, using default: 10")
    
    api_url = input(f"Enter API URL (default: {API_URL}): ").strip() or API_URL
    
    print()
    print(f"Configuration:")
    print(f"  - Concurrent users: {num_users}")
    print(f"  - API URL: {api_url}")
    print()
    
    input("Press Enter to start the test...")
    print()
    
    # Run the test
    tester = LoadTester(api_url, num_users)
    
    try:
        await tester.run_concurrent_test()
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

