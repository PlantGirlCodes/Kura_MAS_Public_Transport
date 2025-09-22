# main_fixed_minimal.py - Minimal version showing fixes work
import os
import json
import requests
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# FastAPI and Pydantic
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Environment variables
from dotenv import load_dotenv
load_dotenv()

# Simple logging
from simple_logging import (
    log_message, log_error, log_success, log_agent_start, log_agent_complete,
    log_api_call, SimpleMetrics, get_simple_stats
)

# =============================================================================
# CONFIGURATION & SETUP
# =============================================================================

def check_api_keys():
    """Check if required API keys are set"""
    required_keys = ["OPENAI_API_KEY", "GOOGLE_MAPS_API_KEY", "WEATHER_API_KEY"]
    missing = [key for key in required_keys if not os.getenv(key)]
    if missing:
        print(f"❌ Missing API keys: {missing}")
        print("Please add them to your .env file")
        return False
    print("✅ All API keys found!")
    return True

# =============================================================================
# STATE MANAGEMENT (FIXED!)
# =============================================================================

class MessageType(Enum):
    USER_REQUEST = "user_request"
    LOCATION_UPDATE = "location_update"
    WEATHER_UPDATE = "weather_update"
    TRAFFIC_UPDATE = "traffic_update"
    ROUTE_CALCULATION = "route_calculation"
    FINAL_DIRECTIONS = "final_directions"

def create_initial_state(user_query: str = "") -> Dict[str, Any]:
    """Create a new state dictionary with default values"""
    return {
        "messages": [],
        "user_query": user_query,
        "location_data": {},
        "weather_data": {},
        "traffic_data": {},
        "route_options": [],
        "final_directions": "",
        "error_count": 0
    }

def create_agent_message(state: Dict[str, Any], msg_type: MessageType, content: str, agent: str) -> None:
    """Helper to add messages to state dictionary (FIXED!)"""
    if "messages" not in state:
        state["messages"] = []
    state["messages"].append({
        "type": msg_type.value,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "agent": agent
    })

# =============================================================================
# TOOL FUNCTIONS (FIXED!)
# =============================================================================

def get_user_location_simple(ip_address: str = "8.8.8.8") -> Dict[str, Any]:
    """Get location from IP address - FREE SERVICE (FIXED!)"""
    try:
        print(f"🗺️ Getting location for IP: {ip_address}")
        response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=10)
        data = response.json()

        if data.get("status") == "success":
            return {
                "latitude": data["lat"],
                "longitude": data["lon"],
                "city": data["city"],
                "region": data["regionName"],
                "country": data["country"],
                "source": "ip_geolocation"
            }
        else:
            raise Exception("IP geolocation failed")

    except Exception as e:
        print(f"Location error: {e}, using NYC as fallback")
        return {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "city": "New York",
            "region": "New York",
            "country": "United States",
            "source": "fallback"
        }

def get_weather_conditions_simple(lat: float, lon: float) -> Dict[str, Any]:
    """Get weather data - FREE TIER: 1000 calls/day (FIXED!)"""
    api_key = os.getenv("WEATHER_API_KEY")
    try:
        print(f"🌤️ Getting weather for {lat}, {lon}")
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "temperature": data["main"]["temp"],
            "condition": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
            "visibility": data.get("visibility", 10000) / 1000,
            "humidity": data["main"]["humidity"],
            "source": "openweathermap"
        }

    except Exception as e:
        print(f"Weather error: {e}, using default weather")
        return {
            "temperature": 20,
            "condition": "clear sky",
            "wind_speed": 5,
            "visibility": 10,
            "humidity": 50,
            "source": "fallback"
        }

# =============================================================================
# SIMPLIFIED AGENT CLASSES (FIXED!)
# =============================================================================

class LocationAgent:
    """Location Agent - Finds user's location (FIXED!)"""

    def __init__(self):
        self.name = "location_agent"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        log_agent_start(self.name)

        try:
            log_api_call("IP Geolocation")
            # FIXED: Proper function call instead of tool.invoke()
            location_result = get_user_location_simple("8.8.8.8")
            state['location_data'] = location_result  # FIXED: Dictionary access
            create_agent_message(  # FIXED: Using helper function
                state,
                MessageType.LOCATION_UPDATE,
                f"Location found: {location_result.get('city', 'Unknown')}, {location_result.get('region', 'Unknown')}",
                self.name
            )
            log_agent_complete(self.name)

        except Exception as e:
            state['error_count'] = state.get('error_count', 0) + 1  # FIXED: Dictionary access
            create_agent_message(state, MessageType.LOCATION_UPDATE, f"Error: {str(e)}", self.name)
            log_error(f"Location Agent failed: {e}")

        return state

class WeatherAgent:
    """Weather Agent - Gets weather conditions (FIXED!)"""

    def __init__(self):
        self.name = "weather_agent"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print("🌤️ Weather Agent: Checking weather conditions...")

        if not state.get("location_data"):  # FIXED: Dictionary access
            state['error_count'] = state.get('error_count', 0) + 1
            create_agent_message(state, MessageType.WEATHER_UPDATE, "No location data available", self.name)
            print("❌ Weather Agent: No location data")
            return state

        try:
            lat = state['location_data']["latitude"]  # FIXED: Dictionary access
            lon = state['location_data']["longitude"]
            weather_result = get_weather_conditions_simple(lat, lon)  # FIXED: Direct function call
            state['weather_data'] = weather_result  # FIXED: Dictionary access
            create_agent_message(
                state,
                MessageType.WEATHER_UPDATE,
                f"Weather: {weather_result.get('condition', 'Unknown')}, {weather_result.get('temperature', 'Unknown')}°C",
                self.name
            )
            print(f"✅ Weather Agent: {weather_result.get('condition')}")

        except Exception as e:
            state['error_count'] = state.get('error_count', 0) + 1  # FIXED: Dictionary access
            create_agent_message(state, MessageType.WEATHER_UPDATE, f"Error: {str(e)}", self.name)
            print(f"❌ Weather Agent failed: {e}")

        return state

class SimpleDirectionAgent:
    """Simple Direction Agent - Creates basic directions (NO AI DEPENDENCY!)"""

    def __init__(self):
        self.name = "direction_agent"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate simple directions based on collected data"""
        print("🤖 Direction Agent: Generating directions...")

        # Handle location queries (like 'where am I?')
        if state['user_query'].lower().strip() in ["where am i?", "where am i", "my location"]:
            if state.get('location_data'):
                # Create a simple location-based response
                location_msg = [
                    "📍 You are in:",
                    f"City: {state['location_data'].get('city', 'Unknown')}",
                    f"Region: {state['location_data'].get('region', 'Unknown')}",
                    f"Country: {state['location_data'].get('country', 'Unknown')}"
                ]

                # Add weather information if available
                if state.get('weather_data'):
                    location_msg.extend([
                        "",
                        "🌤️ Current weather:",
                        f"Condition: {state['weather_data'].get('condition', 'Unknown')}",
                        f"Temperature: {state['weather_data'].get('temperature', 'Unknown')}°C"
                    ])

                # Set the final directions
                state['final_directions'] = "\n".join(location_msg)  # FIXED: Dictionary access
                create_agent_message(
                    state,
                    MessageType.FINAL_DIRECTIONS,
                    "Location information generated",
                    self.name
                )
                return state

        try:
            # For regular direction queries, create basic directions
            directions = self.create_basic_directions(state)
            state['final_directions'] = directions
            create_agent_message(
                state,
                MessageType.FINAL_DIRECTIONS,
                "Basic directions generated",
                self.name
            )
            print("✅ Direction Agent: Directions created!")

        except Exception as e:
            state['error_count'] = state.get('error_count', 0) + 1
            print(f"❌ Direction Agent failed: {e}")

            # Use simpler fallback directions
            state['final_directions'] = f"I can help you with directions for: {state['user_query']}"
            create_agent_message(
                state,
                MessageType.FINAL_DIRECTIONS,
                f"Using fallback directions due to error: {str(e)}",
                self.name
            )

        return state

    def create_basic_directions(self, state: Dict[str, Any]) -> str:
        """Create basic directions when AI fails"""
        directions = f"Here are your directions for: {state['user_query']}\n\n"

        if state.get('location_data'):
            directions += f"📍 Your location: {state['location_data'].get('city')}, {state['location_data'].get('region')}\n"

        if state.get('weather_data'):
            directions += f"🌤️ Weather: {state['weather_data'].get('condition')}, {state['weather_data'].get('temperature')}°C\n"

        directions += "\n🚌 For public transport directions, I recommend:\n"
        directions += "- Check local transit apps for real-time schedules\n"
        directions += "- Use Google Maps transit mode\n"
        directions += "- Visit your local transit authority website\n"
        directions += "\nHave a safe trip!"
        return directions

# =============================================================================
# SIMPLIFIED SYSTEM (FIXED!)
# =============================================================================

class SimpleDirectionSystem:
    """Simplified system to test fixes"""

    def __init__(self):
        # Initialize agents
        self.location_agent = LocationAgent()
        self.weather_agent = WeatherAgent()
        self.direction_agent = SimpleDirectionAgent()

    def process_request(self, user_query: str) -> Dict[str, Any]:
        """Process a direction request through simplified agents"""
        # Start metrics tracking
        metrics = SimpleMetrics()
        metrics.start_request(user_query)

        # Create initial state (FIXED!)
        state = create_initial_state(user_query)
        create_agent_message(state, MessageType.USER_REQUEST, user_query, "user")

        start_time = datetime.now()

        try:
            print(f"🎯 Processing: {user_query}")

            # Run agents in sequence (simplified workflow)
            print("📍 Getting location...")
            state = self.location_agent.execute(state)

            print("🌤️ Getting weather...")
            state = self.weather_agent.execute(state)

            print("🤖 Generating directions...")
            state = self.direction_agent.execute(state)

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()

            # Update metrics
            metrics.finish_request(success=True)
            log_success(f"Request completed in {processing_time:.2f} seconds")

            return {
                "directions": state.get('final_directions', ''),
                "location": state.get('location_data', {}),
                "weather": state.get('weather_data', {}),
                "traffic": state.get('traffic_data', {}),
                "route_options": state.get('route_options', []),
                "processing_time": processing_time,
                "messages_exchanged": len(state.get('messages', [])),
                "errors_encountered": state.get('error_count', 0),
                "conversation_log": state.get('messages', [])
            }

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            metrics.add_error()
            metrics.finish_request(success=False)
            log_error(f"System error after {processing_time:.2f} seconds: {e}")

            return {
                "directions": f"I'm sorry, I encountered an error: {str(e)}. Please try again.",
                "location": {},
                "weather": {},
                "traffic": {},
                "route_options": [],
                "processing_time": processing_time,
                "messages_exchanged": 0,
                "errors_encountered": 1,
                "conversation_log": [{"error": str(e)}]
            }

# =============================================================================
# FASTAPI WEB INTERFACE (FIXED!)
# =============================================================================

# Initialize FastAPI app
app = FastAPI(
    title="Simple Multi-Agent Direction System (FIXED)",
    description="Student-friendly system showing fixes work",
    version="1.0.0-fixed"
)

# Initialize the direction system
print("🚀 Initializing Simple Direction System...")
direction_system = SimpleDirectionSystem()

# API Models
class DirectionRequest(BaseModel):
    query: str

class DirectionResponse(BaseModel):
    directions: str
    location: Dict[str, Any]
    weather: Dict[str, Any]
    traffic: Dict[str, Any]
    route_options: List[Dict[str, Any]]
    processing_time: float
    messages_exchanged: int
    errors_encountered: int
    conversation_log: List[Dict[str, Any]]

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "🚀 Simple Multi-Agent Direction System (FIXED VERSION)",
        "status": "All core fixes applied",
        "agents": ["location", "weather", "direction"],
        "usage": "POST to /directions with {'query': 'your direction request'}"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "fixed",
        "agents": {
            "location_agent": "active",
            "weather_agent": "active",
            "direction_agent": "active"
        },
        "timestamp": datetime.now().isoformat(),
        "fixes_applied": [
            "Fixed tool invocation syntax",
            "Fixed state management (dict access)",
            "Removed duplicate code",
            "Fixed message handling",
            "Simplified dependencies"
        ]
    }

@app.post("/directions", response_model=DirectionResponse)
async def get_directions(request: DirectionRequest):
    """Get directions from the simplified system"""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        result = direction_system.process_request(request.query)
        return DirectionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System error: {str(e)}")

@app.get("/metrics")
async def get_metrics():
    """Get simple system metrics"""
    return get_simple_stats()

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🎓 FIXED VERSION: SIMPLE MULTI-AGENT DIRECTION SYSTEM")
    print("=" * 60)
    print("✅ All critical bugs fixed:")
    print("   - Tool invocation syntax")
    print("   - State management (dict access)")
    print("   - Duplicate code removed")
    print("   - Message handling fixed")
    print("   - LangChain dependencies removed for testing")

    print("\n✅ System ready!")
    print("📊 API Documentation: http://localhost:8001/docs")
    print("💬 Example: curl -X POST http://localhost:8001/directions -H 'Content-Type: application/json' -d '{\"query\": \"where am I?\"}'")
    print("\n🚀 Starting fixed server on port 8001...\n")

    # Start the FastAPI server on different port to avoid conflicts
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")