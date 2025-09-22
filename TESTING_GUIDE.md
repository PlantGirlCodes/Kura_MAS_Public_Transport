# 🧪 COMPLETE TESTING GUIDE
## Multi-Agent Public Transport System

Follow these steps EXACTLY to test your system before the competition!

## 📋 PRE-TESTING CHECKLIST

### 1. Check Your API Keys
```bash
# Open your .env file and verify all keys are set
cat .env
```

**Required Keys:**
- ✅ `OPENAI_API_KEY=sk-...` (not "your-openai-key-here")
- ✅ `GOOGLE_MAPS_API_KEY=AIza...` (not "your-google-maps-key-here")
- ✅ `WEATHER_API_KEY=...` (from OpenWeatherMap)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create Logs Directory
```bash
mkdir -p logs
```

---

## 🚀 STEP-BY-STEP TESTING

### **STEP 1: Basic System Test**

#### 1.1 Start the System
```bash
python main.py
```

**Expected Output:**
```
🚀 Initializing Multi-Agent Direction System...
🔧 Building LangGraph workflow...
✅ LangGraph workflow built successfully
✅ All API keys found!
📊 API Documentation: http://localhost:8000/docs
🧪 Test endpoint: http://localhost:8000/test
```

**❌ If you see errors:**
- Missing API keys → Update your .env file
- Port already in use → Kill process: `lsof -ti:8000 | xargs kill`
- Import errors → Run `pip install -r requirements.txt`

#### 1.2 Test Health Endpoint
**Open new terminal:**
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "agents": {
    "supervisor": "active",
    "location_agent": "active",
    "weather_agent": "active",
    "traffic_agent": "active",
    "route_agent": "active",
    "direction_agent": "active"
  },
  "timestamp": "2024-...",
  "workflow": "langgraph"
}
```

### **STEP 2: Test Individual Components**

#### 2.1 Test Location Detection
```bash
curl -X POST http://localhost:8000/directions \
  -H "Content-Type: application/json" \
  -d '{"query": "where am I?"}'
```

**Check logs for:**
```
[TIMESTAMP] INFO: 🤖 Starting location_agent
[TIMESTAMP] INFO: 🌐 API call to IP Geolocation
[TIMESTAMP] INFO: ✅ Completed location_agent
```

#### 2.2 Test Public Transit Query
```bash
curl -X POST http://localhost:8000/directions \
  -H "Content-Type: application/json" \
  -d '{"query": "public transport to Times Square"}'
```

**Watch for:**
- All 5 agents executing in sequence
- API calls to Google Maps, Weather, OpenAI
- Final directions with transit options (bus/subway/train)

### **STEP 3: Mobile-Friendly Test**

#### 3.1 Test Short Queries (Mobile Style)
```bash
# Test 1: Short destination
curl -X POST http://localhost:8000/directions \
  -H "Content-Type: application/json" \
  -d '{"query": "to airport"}'

# Test 2: Transit specific
curl -X POST http://localhost:8000/directions \
  -H "Content-Type: application/json" \
  -d '{"query": "bus to downtown"}'

# Test 3: With weather consideration
curl -X POST http://localhost:8000/directions \
  -H "Content-Type: application/json" \
  -d '{"query": "subway to Central Park"}'
```

**Expected Response Format:**
```json
{
  "directions": "🚌 Public Transport to Times Square:\n\n📍 From your location: New York, NY\n🌤️ Weather: Clear, 22°C\n\n🚇 Recommended Route:\n1. Walk to Metro Station (3 min)\n2. Take Blue Line to Union Square (15 min)\n3. Transfer to Express Train (2 min)\n4. Take Express to Times Square (8 min)\n\n⏱️ Total Time: 28 minutes\n💰 Cost: $2.90\n\n⚠️ Note: Clear weather conditions, perfect for walking to station!",
  "processing_time": 3.45,
  "messages_exchanged": 6,
  "errors_encountered": 0
}
```

### **STEP 4: Error Handling Test**

#### 4.1 Test Empty Query
```bash
curl -X POST http://localhost:8000/directions \
  -H "Content-Type: application/json" \
  -d '{"query": ""}'
```

**Expected:** HTTP 400 error with helpful message

#### 4.2 Test Invalid Destination
```bash
curl -X POST http://localhost:8000/directions \
  -H "Content-Type: application/json" \
  -d '{"query": "to nowhere123xyz"}'
```

**Expected:** Fallback directions with error handling

### **STEP 5: Metrics & Budget Tracking**

#### 5.1 Check Metrics
```bash
curl http://localhost:8000/metrics
```

**Expected Response:**
```json
{
  "total_requests": 5,
  "successful_requests": 4,
  "success_rate": "80.0%",
  "average_time": "3.20s",
  "total_errors": 1
}
```

#### 5.2 Check Budget Status
**Look in logs/metrics.json:**
```bash
cat logs/metrics.json
```

**Should show:**
- Token usage per request
- Estimated costs
- API call counts

### **STEP 6: Docker Testing**

#### 6.1 Test Docker Build
```bash
docker build -t transport-agents .
```

**Expected:** Build completes successfully

#### 6.2 Test Docker Run
```bash
docker run -p 8000:8000 --env-file .env transport-agents
```

#### 6.3 Test Docker Compose
```bash
docker-compose up --build
```

---

## 📱 MOBILE TESTING

### Use Your Phone to Test!

#### Option 1: Using Browser
1. Find your computer's IP: `ifconfig | grep inet`
2. On phone, go to: `http://YOUR_IP:8000/docs`
3. Test the `/directions` endpoint

#### Option 2: Using curl on phone (Termux app)
```bash
curl -X POST http://YOUR_COMPUTER_IP:8000/directions \
  -H "Content-Type: application/json" \
  -d '{"query": "bus to mall"}'
```

---

## 🔍 VERIFICATION CHECKLIST

Before competition, verify ALL these work:

### ✅ Core Functionality
- [ ] System starts without errors
- [ ] All 5 agents execute in sequence
- [ ] Real API calls to Google Maps (transit mode)
- [ ] Real weather data retrieved
- [ ] OpenAI generates coherent directions
- [ ] Public transport routes (not car routes!)

### ✅ Logging & Metrics
- [ ] All agent activities logged to `logs/system.log`
- [ ] Metrics saved to `logs/metrics.json`
- [ ] Token usage tracked
- [ ] Budget tracking under $20

### ✅ Error Handling
- [ ] Invalid queries handled gracefully
- [ ] API failures don't crash system
- [ ] Fallback responses provided

### ✅ Mobile-Friendly
- [ ] Responses are concise and clear
- [ ] Important info (time, cost) highlighted
- [ ] Weather alerts when relevant
- [ ] Easy to read on small screens

### ✅ Docker Deployment
- [ ] Docker builds successfully
- [ ] Container runs and accepts requests
- [ ] Docker Compose orchestrates properly

---

## 🚨 COMMON ISSUES & FIXES

### Issue: "No route found"
**Fix:** Google Maps needs valid addresses. Try:
- "Union Square to Times Square"
- "Central Park to JFK Airport"
- Use real NYC locations

### Issue: High API costs
**Check:** `logs/metrics.json` for token usage
**Fix:** Reduce `LLM_MAX_TOKENS` in your prompt

### Issue: Slow responses
**Expected:** 3-5 seconds is normal (5 API calls)
**Fix:** Add timeout handling if needed

### Issue: Weather not affecting directions
**Expected:** Only alerts for rain/snow/storms
**Test:** Try during actual bad weather

---

## 🎯 COMPETITION DEMO PREP

### Demo Script (30 seconds):
1. **Show health endpoint:** "All 5 agents active"
2. **Make live request:** "public transport to [local landmark]"
3. **Show real-time logs:** Point out each agent executing
4. **Show result:** Mobile-friendly transit directions
5. **Show metrics:** "Under budget, tracking all usage"

### Backup Demo Data:
If APIs fail during demo, have screenshots of:
- Successful health check
- Sample directions output
- Metrics dashboard
- Docker deployment

### Competition Questions Ready:
- **"Is this real MAS?"** → Yes, 5 specialized agents with LangGraph coordination
- **"How do agents communicate?"** → Shared state via LangGraph workflow
- **"What APIs do you use?"** → Google Maps Transit, OpenWeather, OpenAI
- **"How do you track costs?"** → Token counting + budget metrics
- **"Can it run on mobile?"** → Yes, responsive design + Docker deployment

---

## 📞 FINAL TEST BEFORE DEMO

**30 minutes before competition:**
1. Run full test suite above
2. Check all logs are clean
3. Verify Docker still works
4. Test on mobile device
5. Practice 30-second demo

**You're ready! 🚀**