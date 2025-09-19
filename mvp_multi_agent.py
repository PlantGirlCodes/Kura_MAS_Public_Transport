# mvp_direction_system.py - Simplified Multi-Agent Direction System MVP
import os
import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import requests

# Simple environment setup - just put your keys here for now
API_KEYS = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "your-openai-key-here"),
    "GOOGLE_MAPS_API_KEY": os.getenv("GOOGLE_MAPS_API_KEY", "your-google-maps-key-here"),
    "WEATHER_API_KEY": os.getenv("WEATHER_API_KEY", "your-weather-api-key-here"),
    "TWILIO_ACCOUNT_SID": os.getenv("TWILIO_ACCOUNT_SID", "your-twilio-sid-here"),
    "TWILIO_AUTH_TOKEN": os.getenv("TWILIO_AUTH_TOKEN", "your-twilio-token-here"),
    "TWILIO_PHONE_NUMBER": os.getenv("TWILIO_PHONE_NUMBER", "+1234567890")
}

# Simple state management for agents
@dataclass
class SimpleState:
    user_query: str = ""
    location_data: Dict[str, Any] = field(default_factory=dict)
    weather_data: Dict[str, Any] = field(default_factory=dict)
    traffic_data: Dict[str, Any] = field(default_factory=dict)
    route_options: List[Dict[str, Any]] = field(default_factory=list)
    final_directions: str = ""
    messages: List[str] = field(default_factory=list)
    current_step: str = "start"

# Simple logging
def log(message: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

# =============================================================================
# TOOLS - Simple functions that agents use
# =============================================================================

def get_user_location(ip_address: str = None) -> Dict[str, Any]:
    """Get user location from IP address - FREE API"""
    if not ip_address:
        ip_address = "8.8.8.8"  # Google DNS for testing
    
    try:
        # Using free IP-API service (1000 requests/month free)
        url = f"http://ip-api.com/json/{ip_address}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data["status"] == "success":
            return {
                "latitude": data["lat"],
                "longitude": data["lon"],
                "city": data["city"],
                "region": data["regionName"],
                "country": data["country"],
                "address": f"{data['city']}, {data['regionName']}"
            }
        else:
            return {"error": "Could not determine location"}
    except Exception as e:
        log(f"Location error: {e}")
        return {"error": str(e)}

def get_weather_info(lat: float, lon: float) -> Dict[str, Any]:
    """Get weather from OpenWeatherMap - 1000 calls/day free"""
    api_key = API_KEYS["WEATHER_API_KEY"]
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        return {
            "temperature": data["main"]["temp"],
            "condition": data["weather"][0]["description"],
            "visibility_km": data.get("visibility", 10000) / 1000,
            "wind_speed": data["wind"]["speed"],
            "humidity": data["main"]["humidity"]
        }
    except Exception as e:
        log(f"Weather error: {e}")
        return {"error": str(e)}

def get_directions_data(origin: str, destination: str) -> Dict[str, Any]:
    """Get directions from Google Maps - $200 credit covers ~4000 requests"""
    api_key = API_KEYS["GOOGLE_MAPS_API_KEY"]
    
    try:
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "departure_time": "now",
            "traffic_model": "best_guess",
            "alternatives": "true",
            "key": api_key
        }
        
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        if data["status"] == "OK":
            route = data["routes"][0]
            leg = route["legs"][0]
            
            return {
                "duration_normal": leg.get("duration", {}).get("text", "Unknown"),
                "duration_traffic": leg.get("duration_in_traffic", {}).get("text", "Unknown"),
                "distance": leg.get("distance", {}).get("text", "Unknown"),
                "summary": route.get("summary", "Main route"),
                "steps": len(leg.get("steps", [])),
                "alternatives": len(data["routes"])
            }
        else:
            return {"error": f"Google Maps error: {data['status']}"}
    except Exception as e:
        log(f"Directions error: {e}")
        return {"error": str(e)}

def generate_final_directions(state: SimpleState) -> str:
    """Generate final directions using OpenAI - about $0.30 per request with GPT-4"""
    api_key = API_KEYS["OPENAI_API_KEY"]
    
    # Create a simple prompt with all the data
    prompt = f"""
    You are a helpful navigation assistant. Based on the following information, provide clear, 
    friendly directions to help the user get to their destination.

    User Request: {state.user_query}
    Location: {json.dumps(state.location_data, indent=2)}
    Weather: {json.dumps(state.weather_data, indent=2)}
    Route Info: {json.dumps(state.traffic_data, indent=2)}

    Please provide:
    1. A summary of their journey
    2. Current conditions that might affect travel
    3. Estimated time and distance
    4. Any helpful tips

    Keep it friendly and conversational, like you're helping a friend.
    """

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",  # Cheaper than GPT-4: $0.002/1K tokens vs $0.03/1K
            "messages": [
                {"role": "system", "content": "You are a helpful navigation assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,  # Keep it concise to save money
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            log(f"OpenAI error: {response.status_code}")
            return create_fallback_directions(state)
            
    except Exception as e:
        log(f"OpenAI error: {e}")
        return create_fallback_directions(state)

def create_fallback_directions(state: SimpleState) -> str:
    """Create basic directions without AI if OpenAI fails"""
    location = state.location_data.get("address", "your location")
    weather = state.weather_data.get("condition", "unknown weather")
    duration = state.traffic_data.get("duration_traffic", "unknown time")
    distance = state.traffic_data.get("distance", "unknown distance")
    
    return f"""
    🗺️ Directions from {location}:

    📍 Distance: {distance}
    ⏱️ Estimated time: {duration}
    🌤️ Current weather: {weather}

    Route summary: {state.traffic_data.get('summary', 'Main route recommended')}

    Safe travels! Check your preferred navigation app for turn-by-turn directions.
    """

# =============================================================================
# AGENTS - Simple classes that do specific jobs
# =============================================================================

class LocationAgent:
    """Gets user's location"""
    
    def run(self, state: SimpleState) -> SimpleState:
        log("🌍 Location Agent: Finding your location...")
        
        # For MVP, we'll use IP geolocation
        # In a real app, you'd get GPS coordinates from the user
        location_data = get_user_location()
        
        if "error" not in location_data:
            state.location_data = location_data
            state.messages.append(f"📍 Found you in {location_data['city']}, {location_data['region']}")
            log(f"Location found: {location_data['city']}")
        else:
            state.messages.append("❌ Could not determine your location")
            log("Location detection failed")
        
        return state

class WeatherAgent:
    """Gets weather information"""
    
    def run(self, state: SimpleState) -> SimpleState:
        log("🌤️ Weather Agent: Checking weather conditions...")
        
        if not state.location_data or "error" in state.location_data:
            state.messages.append("⚠️ Need location first to check weather")
            return state
        
        lat = state.location_data["latitude"]
        lon = state.location_data["longitude"]
        weather_data = get_weather_info(lat, lon)
        
        if "error" not in weather_data:
            state.weather_data = weather_data
            temp = weather_data["temperature"]
            condition = weather_data["condition"]
            state.messages.append(f"🌡️ Weather: {condition}, {temp}°C")
            log(f"Weather: {condition}, {temp}°C")
        else:
            state.messages.append("❌ Could not get weather info")
            log("Weather check failed")
        
        return state

class TrafficAgent:
    """Gets directions and traffic info"""
    
    def run(self, state: SimpleState) -> SimpleState:
        log("🚗 Traffic Agent: Getting directions and traffic info...")
        
        # Parse the user query to extract origin and destination
        query = state.user_query.lower()
        
        # Simple parsing - in a real app, you'd use NLP
        if " to " in query:
            parts = query.split(" to ", 1)
            destination = parts[1].strip()
            origin = state.location_data.get("address", "current location")
        else:
            # Assume they want directions TO somewhere FROM current location
            destination = query.replace("directions to ", "").replace("how to get to ", "").strip()
            origin = state.location_data.get("address", "current location")
        
        log(f"Route: {origin} → {destination}")
        
        # Get directions data
        directions_data = get_directions_data(origin, destination)
        
        if "error" not in directions_data:
            state.traffic_data = directions_data
            duration = directions_data["duration_traffic"]
            distance = directions_data["distance"]
            state.messages.append(f"🛣️ Route found: {distance}, about {duration}")
            log(f"Route: {distance}, {duration}")
        else:
            state.messages.append("❌ Could not get directions")
            log("Directions failed")
        
        return state

class DirectionAgent:
    """Creates final user-friendly directions"""
    
    def run(self, state: SimpleState) -> SimpleState:
        log("🗺️ Direction Agent: Creating your personalized directions...")
        
        # Generate final directions using AI
        final_directions = generate_final_directions(state)
        state.final_directions = final_directions
        
        log("Directions generated successfully!")
        return state

class SupervisorAgent:
    """Coordinates all the other agents"""
    
    def __init__(self):
        self.location_agent = LocationAgent()
        self.weather_agent = WeatherAgent()
        self.traffic_agent = TrafficAgent()
        self.direction_agent = DirectionAgent()
    
    def process_request(self, user_query: str) -> Dict[str, Any]:
        log(f"🎯 Supervisor: Processing request - {user_query}")
        
        # Create initial state
        state = SimpleState(user_query=user_query, current_step="start")
        start_time = time.time()
        
        try:
            # Run agents in sequence
            log("Step 1: Getting location...")
            state = self.location_agent.run(state)
            
            log("Step 2: Checking weather...")
            state = self.weather_agent.run(state)
            
            log("Step 3: Finding route...")
            state = self.traffic_agent.run(state)
            
            log("Step 4: Generating directions...")
            state = self.direction_agent.run(state)
            
            processing_time = time.time() - start_time
            log(f"✅ Request completed in {processing_time:.2f} seconds")
            
            return {
                "success": True,
                "directions": state.final_directions,
                "processing_time": processing_time,
                "steps_completed": state.messages,
                "location": state.location_data.get("city", "Unknown"),
                "weather": state.weather_data.get("condition", "Unknown")
            }
            
        except Exception as e:
            log(f"❌ Error processing request: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time,
                "steps_completed": state.messages
            }

# =============================================================================
# SIMPLE WEB SERVER using Flask (lighter than FastAPI for MVP)
# =============================================================================

from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
supervisor = SupervisorAgent()

# Simple HTML page for testing
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Multi-Agent Directions MVP</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        input[type="text"] { width: 60%; padding: 10px; font-size: 16px; }
        button { padding: 10px 20px; font-size: 16px; background: #007bff; color: white; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result { margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 8px; }
        .steps { background: #e9ecef; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .loading { color: #007bff; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Multi-Agent Direction System</h1>
        <p>Ask for directions and watch our AI agents work together!</p>
        
        <div>
            <input type="text" id="query" placeholder="e.g., 'directions to Times Square'" />
            <button onclick="getDirections()">Get Directions</button>
        </div>
        
        <div id="result"></div>
    </div>

    <script>
        async function getDirections() {
            const query = document.getElementById('query').value;
            const resultDiv = document.getElementById('result');
            
            if (!query.trim()) {
                alert('Please enter a destination!');
                return;
            }
            
            resultDiv.innerHTML = '<div class="loading">🤖 Our agents are working on your request...</div>';
            
            try {
                const response = await fetch('/directions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.innerHTML = `
                        <div class="result">
                            <h3>🗺️ Your Directions:</h3>
                            <div style="white-space: pre-line; line-height: 1.6;">${data.directions}</div>
                            
                            <div class="steps">
                                <h4>🔍 What our agents found:</h4>
                                <ul>${data.steps_completed.map(step => '<li>' + step + '</li>').join('')}</ul>
                                <p><small>📍 Location: ${data.location} | 🌤️ Weather: ${data.weather} | ⏱️ Processed in ${data.processing_time.toFixed(2)}s</small></p>
                            </div>
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <div class="result" style="background: #f8d7da; color: #721c24;">
                            <h3>❌ Error</h3>
                            <p>${data.error}</p>
                        </div>
                    `;
                }
            } catch (error) {
                resultDiv.innerHTML = `
                    <div class="result" style="background: #f8d7da; color: #721c24;">
                        <h3>❌ Network Error</h3>
                        <p>Could not connect to the server. Please try again.</p>
                    </div>
                `;
            }
        }
        
        // Allow Enter key to submit
        document.getElementById('query').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                getDirections();
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    """Simple web interface for testing"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/directions', methods=['POST'])
def get_directions():
    """Main API endpoint"""
    try:
        data = request.get_json()
        user_query = data.get('query', '')
        
        if not user_query:
            return jsonify({"success": False, "error": "No query provided"}), 400
        
        # Process the request through our multi-agent system
        result = supervisor.process_request(user_query)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health')
def health():
    """Simple health check"""
    return jsonify({
        "status": "healthy",
        "agents": ["supervisor", "location", "weather", "traffic", "direction"],
        "timestamp": datetime.now().isoformat()
    })

# =============================================================================
# TWILIO SMS INTEGRATION - Simple version
# =============================================================================

try:
    from twilio.rest import Client
    from twilio.twiml.messaging_response import MessagingResponse
    
    # Store user sessions in memory (for MVP only - use database in production)
    user_sessions = {}
    
    @app.route('/sms', methods=['POST'])
    def handle_sms():
        """Handle incoming SMS messages"""
        try:
            from_number = request.form.get('From')
            body = request.form.get('Body', '').strip()
            
            log(f"📱 SMS from {from_number}: {body}")
            
            # Create Twilio response
            resp = MessagingResponse()
            
            # Check if this looks like a directions request
            direction_keywords = ['directions', 'how to get', 'navigate', 'route to']
            if any(keyword in body.lower() for keyword in direction_keywords):
                # Process through our multi-agent system
                result = supervisor.process_request(body)
                
                if result['success']:
                    # SMS has character limits, so we'll send a summary
                    directions = result['directions'][:1500]  # Keep it under SMS limit
                    resp.message(f"🗺️ {directions}")
                else:
                    resp.message("Sorry, I couldn't get directions right now. Please try again!")
            else:
                resp.message("Hi! I can help with directions. Try asking 'directions to [place]' or 'how to get to [place]'")
            
            return str(resp)
            
        except Exception as e:
            log(f"SMS error: {e}")
            resp = MessagingResponse()
            resp.message("Sorry, something went wrong. Please try again!")
            return str(resp)
    
    def send_test_sms(phone_number: str, message: str):
        """Send a test SMS"""
        try:
            client = Client(API_KEYS["TWILIO_ACCOUNT_SID"], API_KEYS["TWILIO_AUTH_TOKEN"])
            
            message = client.messages.create(
                body=message,
                from_=API_KEYS["TWILIO_PHONE_NUMBER"],
                to=phone_number
            )
            
            print(f"✅ SMS sent successfully! Message ID: {message.sid}")
            return True
        except Exception as e:
            print(f"❌ SMS failed: {e}")
            return False

except ImportError:
    print("⚠️ Twilio not installed. SMS features disabled.")
    print("To enable SMS: pip install twilio")

# =============================================================================
# MAIN FUNCTION - Run the system
# =============================================================================

def main():
    print("🚀 Starting Multi-Agent Direction System MVP")
    print("=" * 50)
    
    # Check API keys
    missing_keys = []
    for key, value in API_KEYS.items():
        if value == f"your-{key.lower().replace('_', '-')}-here":
            missing_keys.append(key)
    
    if missing_keys:
        print("⚠️ Warning: The following API keys are not set:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\nPlease update the API_KEYS dictionary in the code or set environment variables.")
        print("The system will still run but some features may not work.\n")
    
    # Test the system with a sample query
    print("🧪 Testing the system...")
    test_query = "directions to Central Park, New York"
    print(f"Test query: {test_query}")
    
    supervisor = SupervisorAgent()
    result = supervisor.process_request(test_query)
    
    if result['success']:
        print("✅ System test passed!")
        print(f"Processing time: {result['processing_time']:.2f} seconds")
    else:
        print("❌ System test failed:")
        print(result.get('error', 'Unknown error'))
    
    print("\n" + "=" * 50)
    print("🌐 Starting web server...")
    print("Open your browser to: http://localhost:5000")
    print("For SMS testing, your webhook URL will be: http://your-domain.com/sms")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
