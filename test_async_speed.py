"""
Test script to compare sync vs async performance
This demonstrates the speed improvements with async operations
"""
import time
import asyncio
import os
import sys
import io

# Fix Windows console encoding for Unicode/Emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Config.settings')
import django
django.setup()

from fact_check_with_openai.utils_async import check_fact_simple_async


async def test_async_fact_check():
    """Test the async fact-checking function"""
    print("=" * 80)
    print("⚡ ASYNC FACT-CHECKING PERFORMANCE TEST")
    print("=" * 80)
    
    test_claim = "أعلنت وكالة الفضاء الأمريكية ناسا عن اكتشاف كوكب جديد"
    
    print(f"\n📝 Testing claim: {test_claim}")
    print(f"⏱️  Starting timer...")
    
    start_time = time.time()
    
    # Test with all features enabled to see parallel execution
    result = await check_fact_simple_async(
        claim_text=test_claim,
        k_sources=10,
        generate_news=True,
        preserve_sources=True,
        generate_tweet=True
    )
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    print("\n" + "=" * 80)
    print(f"✅ COMPLETED IN: {elapsed:.2f} seconds")
    print("=" * 80)
    
    print(f"\n📊 Results:")
    print(f"   - Case: {result.get('case', 'N/A')}")
    print(f"   - Talk length: {len(result.get('talk', ''))} characters")
    print(f"   - Sources found: {len(result.get('sources', []))}")
    print(f"   - News article: {'✅ Generated' if result.get('news_article') else '❌ Not generated'}")
    print(f"   - Tweet: {'✅ Generated' if result.get('x_tweet') else '❌ Not generated'}")
    
    if result.get('source_statistics'):
        stats = result['source_statistics']
        print(f"\n📈 Source Statistics:")
        print(f"   - Total sources: {stats.get('total_sources', 0)}")
        print(f"   - Supporting: {stats.get('supporting_percentage', 0)}%")
        print(f"   - Opposing: {stats.get('opposing_percentage', 0)}%")
        print(f"   - Neutral: {stats.get('neutral_percentage', 0)}%")
    
    # Performance evaluation
    print(f"\n🚀 Performance Analysis:")
    if elapsed <= 5:
        print(f"   ⭐ EXCELLENT! Completed in {elapsed:.2f}s (target: ≤5s)")
    elif elapsed <= 8:
        print(f"   ✅ GOOD! Completed in {elapsed:.2f}s")
    elif elapsed <= 12:
        print(f"   ⚠️  ACCEPTABLE! Completed in {elapsed:.2f}s")
    else:
        print(f"   ❌ SLOW! Completed in {elapsed:.2f}s (needs optimization)")
    
    print("\n" + "=" * 80)
    print("📝 Key Improvements with Async:")
    print("   1. ⚡ Parallel API calls to SerpAPI (multiple domains at once)")
    print("   2. ⚡ Concurrent OpenAI requests (fact-check + news + tweet)")
    print("   3. ⚡ Non-blocking I/O operations (aiohttp instead of requests)")
    print("   4. ⚡ Efficient resource usage (asyncio event loop)")
    print("=" * 80)
    
    return result


def main():
    """Main test function"""
    try:
        print("\n🔧 Initializing async test...")
        result = asyncio.run(test_async_fact_check())
        print("\n✅ Test completed successfully!")
        return 0
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

