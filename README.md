# Kura_MAS_Public_Transport
using langraph 

# README.md
# Multi-Agent Direction System MVP

A simple AI-powered direction system that uses multiple agents to provide intelligent navigation assistance.

## 🤖 How It Works

Our system uses 5 specialized agents:
1. **Supervisor Agent** - Coordinates everything
2. **Location Agent** - Finds your location  
3. **Weather Agent** - Checks weather conditions
4. **Traffic Agent** - Gets directions and traffic info
5. **Direction Agent** - Creates friendly, personalized directions

## 🚀 Quick Start

### 1. Get API Keys (All Free Tiers Available!)
- **OpenAI**: https://platform.openai.com/api-keys (GPT-3.5-turbo is cheap!)
- **Google Maps**: https://console.cloud.google.com/apis/credentials ($200 credit)
- **Weather**: https://openweathermap.org/api (1000 calls/day free)
- **Twilio** (optional): https://console.twilio.com/ (trial credit)

### 2. Setup
```bash
# Clone your repository
git clone your-repo-url
cd your-repo-name

# Install dependencies
pip install -r requirements.txt

# Add your API keys to the code
# Edit mvp_direction_system.py and replace the API_KEYS values
```

### 3. Run
```bash
python mvp_direction_system.py
```

Open http://localhost:5000 in your browser!

## 💰 Cost Breakdown (Under $20!)

- **OpenAI GPT-3.5**: ~$0.002 per request = ~10,000 requests for $20
- **Google Maps**: $200 free credit = ~4,000 requests  
- **Weather API**: 1000 requests/day FREE
- **Location API**: FREE forever
- **Twilio SMS**: Trial credit covers ~100 messages

**Total for 100 direction requests: ~$0.20** 🎉

## 📱 Features

### Web Interface
- Simple web page at http://localhost:5000
- Type any destination and get directions
- See all agent activities in real-time

### SMS Integration (Optional)
- Text your Twilio number: "directions to Times Square"
- Get directions via SMS
- Perfect for when you're on the go!

### Example Queries
- "directions to Times Square"
- "how to get to Central Park"  
- "navigate to JFK airport"
- "route to Brooklyn Bridge"

## 🔧 Architecture 

This is a **Hierarchical Multi-Agent System** where:
- Agents communicate through shared state
- Supervisor coordinates the workflow
- Each agent has a specific job
- All data flows through one central coordinator

## 📊 What Each Agent Does

### 🌍 Location Agent
- **Input**: Your IP address
- **Output**: City, coordinates, address
- **API**: IP-API.com (free)

### 🌤️ Weather Agent  
- **Input**: Your coordinates
- **Output**: Temperature, conditions, visibility
- **API**: OpenWeatherMap

### 🚗 Traffic Agent
- **Input**: Origin and destination
- **Output**: Route time, distance, traffic delays  
- **API**: Google Maps Directions

### 🗺️ Direction Agent
- **Input**: All the above data + your question
- **Output**: Friendly, personalized directions
- **API**: OpenAI GPT-3.5-turbo

## 🧪 Testing

### Quick Test
The system tests itself when you run it!

### Manual Testing
```bash
# Test the web interface
curl -X POST http://localhost:5000/directions \
  -H "Content-Type: application/json" \
  -d '{"query": "directions to Times Square"}'

# Test SMS (if configured)
# Send SMS to your Twilio number: "directions to Central Park"
```

## 🛠️ Customization

### Adding New Agent
1. Create a new class like `LocationAgent`
2. Add a `run(state)` method
3. Register it in `SupervisorAgent`

### Changing AI Model
In the `generate_final_directions` function:
```python
# Change this line:
"model": "gpt-3.5-turbo",  # Cheaper
# To this:
"model": "gpt-4",  # More expensive but better
```

## 🚨 Troubleshooting

### "API Key Invalid" 
- Check your API keys in the `API_KEYS` dictionary
- Make sure you've activated your APIs in the respective consoles

### "Location not found"
- The system uses IP geolocation (not GPS)
- For testing, it defaults to Google's DNS location

### "High costs"
- Use GPT-3.5-turbo instead of GPT-4
- Set max_tokens to 300-500 to limit response length
- Cache responses for common queries

### SMS not working
- Make sure you've configured your Twilio webhook URL
- Your webhook should point to: http://your-domain.com/sms

## 🎯 Next Steps

### Phase 2 Ideas
- [ ] Add GPS location sharing
- [ ] Save user preferences  
- [ ] Add transit directions
- [ ] Voice interface
- [ ] Group trip planning

### Making it Production Ready
- [ ] Add database for user sessions
- [ ] Implement proper error handling
- [ ] Add caching to reduce API calls
- [ ] Deploy to cloud (Heroku, Railway, etc.)

## 📞 Support

- Check the console output for detailed logs
- All agent activities are logged with timestamps
- SMS messages are logged for debugging

## 🏆 Project Requirements Met

✅ **Multi-Agent System**: 5 specialized agents with clear roles  
✅ **Communication**: Agents share data through structured state  
✅ **External Integration**: Google Maps, Weather, SMS via Twilio  
✅ **Agent Behaviors**: Reasoning, memory (state), tool use  
✅ **Logging**: All activities logged with timestamps  
✅ **Error Handling**: Try/catch blocks and fallback responses  
✅ **Deployment**: Simple Flask server, easy to deploy  
✅ **Documentation**: This README explains everything!  

---

**Built by student developers, for student developers! 🎓**

Have fun experimenting and learning about multi-agent systems!
