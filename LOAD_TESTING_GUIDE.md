# 🧪 Load Testing Guide - How to Test Your Server Capacity

This guide shows you how to test your fact-checking API under high load to determine its real capacity.

---

## 📋 What We're Testing

### Key Metrics:
1. **Concurrent Users**: How many users can use the system at the same time?
2. **Response Time**: How long does each request take?
3. **Failure Rate**: Do requests fail under load?
4. **Throughput**: How many requests per second can the system handle?
5. **Breaking Point**: At what load does the system start to fail?

---

## 🛠️ Testing Tools Provided

### Tool 1: Simple Concurrent Test (Recommended for beginners)
**File**: `load_test_concurrent.py`

**Features**:
- ✅ Simple to use
- ✅ Tests exact number of concurrent users
- ✅ Detailed analysis and recommendations
- ✅ Saves results to JSON
- ✅ No additional setup needed

**Usage**:
```bash
# Make sure your server is running
python manage.py runserver

# In another terminal, run the test
python load_test_concurrent.py

# Follow the prompts:
# - Enter number of users (e.g., 10)
# - Press Enter to start
```

**Example Output**:
```
🚀 LOAD TEST - 10 CONCURRENT USERS
=====================================
API URL: http://localhost:8000/fact_check_with_openai/
Test queries: 10 different queries
Concurrent users: 10
Start time: 2025-01-22 15:30:00
=====================================

👤 User 1: Sending request at 15:30:00.123
👤 User 2: Sending request at 15:30:00.125
...
✅ User 1: Completed in 12.34s
✅ User 3: Completed in 13.45s
...

📊 TEST RESULTS ANALYSIS
=====================================
📈 Basic Statistics:
   Total requests: 10
   ✅ Successful: 10 (100.0%)
   ❌ Errors: 0 (0.0%)
   ⏱️  Timeouts: 0 (0.0%)

⏱️  Response Time Statistics:
   Fastest: 10.23s
   Slowest: 16.45s
   Average: 13.42s
   Median: 13.15s

🎯 Concurrent Capacity Analysis:
   ✅ Server handled all 10 concurrent requests successfully!
   ✅ Average response time: 13.42s
   ✅ EXCELLENT: Response times are good (≤20s)
   💡 Server can likely handle 10 or slightly more concurrent users

💡 Recommendations:
   ✅ Your server is performing EXCELLENT with 10 concurrent users!
   💡 Consider testing with 15 users to find the limit
```

---

### Tool 2: Locust Load Testing (Advanced, with Web UI)
**File**: `load_test_locust.py`

**Features**:
- ✅ Professional web-based UI
- ✅ Real-time statistics and graphs
- ✅ Gradual load increase
- ✅ Multiple user behaviors
- ✅ Industry-standard tool

**Usage**:
```bash
# Make sure your server is running
python manage.py runserver

# In another terminal, start Locust
locust -f load_test_locust.py --host=http://localhost:8000

# Open browser and go to:
# http://localhost:8089

# Configure test:
# - Number of users: 10
# - Spawn rate: 2 users/second
# - Click "Start swarming"
```

**Web UI Features**:
- Real-time graphs of response times
- Requests per second (RPS)
- Failure rate
- Statistics table
- Download reports (CSV, HTML)

---

## 🧪 Testing Scenarios

### Scenario 1: Find Your Server's Capacity (Recommended First Test)

**Objective**: Determine how many concurrent users your current server can handle

**Steps**:
```bash
# Test 1: Light load (2 users)
python load_test_concurrent.py
# Enter: 2

# Test 2: Light-Medium (5 users)
python load_test_concurrent.py
# Enter: 5

# Test 3: Medium (10 users)
python load_test_concurrent.py
# Enter: 10

# Test 4: Heavy (15 users)
python load_test_concurrent.py
# Enter: 15

# Test 5: Very Heavy (20 users)
python load_test_concurrent.py
# Enter: 20
```

**Analysis**:
- If average response time stays under 20s → ✅ Server can handle it
- If average response time is 20-40s → ⚠️ Server is at limit
- If average response time is over 40s → ❌ Server is overloaded
- If requests fail or timeout → ❌ Server cannot handle this load

---

### Scenario 2: Sustained Load Test

**Objective**: Test if server can maintain performance over time

**Using Locust**:
```bash
locust -f load_test_locust.py --host=http://localhost:8000

# In web UI:
# - Users: 10
# - Spawn rate: 2/second
# - Let it run for 10-15 minutes

# Monitor:
# - Does response time stay consistent?
# - Does failure rate increase over time?
# - Are there memory leaks?
```

---

### Scenario 3: Spike Test

**Objective**: Test how server handles sudden traffic increase

**Using Locust**:
```bash
locust -f load_test_locust.py --host=http://localhost:8000

# Phase 1: Start with 5 users
# Phase 2: Wait 2 minutes
# Phase 3: Increase to 20 users suddenly
# Phase 4: Observe recovery

# Check:
# - Does server crash?
# - How long to recover?
# - Do existing users experience issues?
```

---

### Scenario 4: Stress Test

**Objective**: Find the absolute breaking point

**Steps**:
```bash
# Keep increasing users until something breaks
python load_test_concurrent.py  # 10 users
python load_test_concurrent.py  # 20 users
python load_test_concurrent.py  # 30 users
python load_test_concurrent.py  # 40 users
# Continue until failures occur
```

---

## 📊 Understanding Results

### Response Time Analysis

| Average Time | Status | Action |
|--------------|--------|--------|
| < 15s | ✅ Excellent | Server is comfortable |
| 15-20s | ✅ Good | Server is performing well |
| 20-30s | ⚠️ Acceptable | Server is at capacity |
| 30-40s | ⚠️ Slow | Server is overloaded |
| > 40s | ❌ Very Slow | Upgrade needed |
| Timeouts | ❌ Critical | Immediate upgrade needed |

### Success Rate Analysis

| Success Rate | Status | Action |
|--------------|--------|--------|
| 100% | ✅ Perfect | System is stable |
| 95-99% | ✅ Good | Minor issues, acceptable |
| 90-95% | ⚠️ Warning | Some problems appearing |
| 80-90% | ⚠️ Critical | System struggling |
| < 80% | ❌ Failure | System cannot handle load |

---

## 🎯 Capacity Estimation

### Based on Test Results:

If your test shows:
- **10 users, avg 13s, 100% success** → Your capacity is **~10 concurrent users**
- **10 users, avg 25s, 100% success** → Your capacity is **~8 concurrent users** (near limit)
- **10 users, avg 40s, 90% success** → Your capacity is **~6 concurrent users** (overloaded)
- **10 users, 50% timeouts** → Your capacity is **~4-5 concurrent users** (way overloaded)

### Real-World Usage Calculation:

```
If capacity = 10 concurrent users

Scenario A: Users check 1 fact per minute
- Can serve: 10 users × 60 minutes = 600 checks/hour
- Daily (8 hours): ~4,800 checks
- User count: 480 users/day (10 checks each)

Scenario B: Users check 1 fact per 10 minutes
- Can serve: 10 users × 6 checks/hour = 60 checks/hour
- But users are less active, so:
- Can serve: ~100-150 active users throughout the day

Scenario C: Peak hour usage
- All users active in 1 hour
- Can serve: ~10-15 users at peak
```

---

## 💡 Recommendations Based on Test Results

### If Testing with Standard (2GB, 1 CPU):

**Expected Results**:
- ✅ 2-4 concurrent users: Good performance
- ⚠️ 5-6 concurrent users: Acceptable performance
- ❌ 7+ concurrent users: Poor performance

**If results show less**:
- Check if server has other processes running
- Ensure async code is working properly
- Verify database/API connections are optimized

**If results show more**:
- Great! Your optimizations are working
- Cache may be helping significantly
- Consider documenting your setup

---

## 🔧 Troubleshooting

### Problem: All requests timeout
**Solution**:
- Check if server is running
- Verify API URL is correct
- Increase timeout in test script
- Check server logs for errors

### Problem: First few requests succeed, then all fail
**Solution**:
- Server is running out of resources (RAM/CPU)
- Check server resource usage
- Consider upgrading server
- Implement request queuing

### Problem: Inconsistent results
**Solution**:
- Run test multiple times
- Check for background processes
- Ensure stable internet connection
- Clear cache between tests

### Problem: Response times much slower than expected
**Solution**:
- Check OpenAI API response times
- Verify SerpAPI is responding quickly
- Check network latency
- Review server logs

---

## 📈 Monitoring During Tests

### What to Monitor:

1. **Server Resources** (using `htop` or Task Manager):
   - CPU usage: Should be < 80% sustained
   - RAM usage: Should have 20% free
   - Disk I/O: Should not be bottleneck
   - Network: Check bandwidth usage

2. **Application Logs**:
   ```bash
   # Watch Django logs
   python manage.py runserver
   
   # Or if using gunicorn
   tail -f gunicorn.log
   ```

3. **Database** (if using one):
   - Connection pool usage
   - Query times
   - Lock waits

---

## 📝 Test Report Template

After running tests, document your findings:

```markdown
## Load Test Report - [Date]

### Test Environment:
- Server: Standard (2GB RAM, 1 CPU)
- Location: [Your location]
- Django version: 5.2.1
- Python version: 3.13

### Test Configuration:
- Tool: load_test_concurrent.py
- Concurrent users: 10
- Test duration: ~2 minutes
- Test queries: 10 different queries

### Results:
- Total requests: 10
- Successful: 10 (100%)
- Failed: 0 (0%)
- Timeouts: 0 (0%)

### Response Times:
- Fastest: 10.2s
- Slowest: 16.4s
- Average: 13.4s
- Median: 13.1s

### Conclusions:
- ✅ Server handles 10 concurrent users well
- ✅ All requests completed successfully
- ✅ Response times acceptable (avg 13.4s)
- 💡 Estimated capacity: 10-12 concurrent users

### Recommendations:
- Current server is adequate for 10 concurrent users
- For 20+ users, consider upgrading to Pro
- Implement caching for better performance
```

---

## 🚀 Next Steps

After testing:

1. **Document Results**: Save test reports for future reference
2. **Set Baseline**: Know your current capacity
3. **Monitor Production**: Set up monitoring tools
4. **Plan Scaling**: Know when to upgrade
5. **Optimize**: Implement caching, CDN, etc.
6. **Re-test**: After any changes, test again

---

## 📞 Support

If you need help:
1. Read the error messages carefully
2. Check server logs
3. Verify all dependencies are installed
4. Ensure server is running
5. Test with smaller load first

---

**Ready to test?**

```bash
# Start simple
python load_test_concurrent.py

# Enter: 10
# Press Enter

# Watch the results! 🚀
```

