# main.py - Complete Multi-Agent Direction System with LangGraph
import os
import json
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# FastAPI and Pydantic
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# LangChain and LangGraph
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor

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
# STATE MANAGEMENT
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
    
def add_message(state: Dict[str, Any], msg_type: MessageType, content: str, agent: str) -> None:
    """Helper to add messages to state dictionary"""
    if "messages" not in state:
        state["messages"] = []
    state["messages"].append({
        "type": msg_type.value,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "agent": agent
    })

# =============================================================================
# TOOL FUNCTIONS (for agents to use)
# =============================================================================

@tool
def get_user_location(ip_address: str = "8.8.8.8") -> Dict[str, Any]:
    """Get location from IP address - FREE SERVICE"""
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

@tool
def get_weather_conditions(lat: float, lon: float) -> Dict[str, Any]:
    """Get weather data - FREE TIER: 1000 calls/day"""
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

@tool
def get_traffic_conditions(origin: str, destination: str) -> Dict[str, Any]:
    """Get traffic conditions - FREE TIER: $200 monthly credit"""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    try:
        print(f"🚗 Getting traffic from {origin} to {destination}")
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "mode": "transit",  # PUBLIC TRANSPORT MODE!
            "departure_time": "now",
            "transit_mode": "bus|subway|train",
            "key": api_key
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data["status"] == "OK":
            route = data["routes"][0]
            leg = route["legs"][0]
            
            duration_normal = leg.get("duration", {}).get("value", 0)
            duration_traffic = leg.get("duration_in_traffic", {}).get("value", duration_normal)
            
            return {
                "duration_normal": leg.get("duration", {}).get("text", "Unknown"),
                "duration_in_traffic": leg.get("duration_in_traffic", {}).get("text", "Unknown"),
                "distance": leg.get("distance", {}).get("text", "Unknown"),
                "traffic_delay": max(0, duration_traffic - duration_normal),
                "route_summary": route.get("summary", "Route found"),
                "source": "google_maps"
            }
        else:
            raise Exception(f"Google Maps error: {data.get('status', 'Unknown')}")
            
    except Exception as e:
        print(f"Traffic error: {e}")
        return {
            "error": str(e),
            "source": "error"
        }

@tool
def calculate_route_options(origin: str, destination: str) -> List[Dict[str, Any]]:
    """Calculate multiple route options - FREE TIER: $200 monthly credit"""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    try:
        print(f"🛣️ Calculating route options from {origin} to {destination}")
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "mode": "transit",  # PUBLIC TRANSPORT MODE!
            "alternatives": "true",
            "departure_time": "now",
            "transit_mode": "bus|subway|train",
            "key": api_key
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        routes = []
        if data["status"] == "OK":
            for i, route in enumerate(data["routes"][:3]):  # Max 3 routes
                leg = route["legs"][0]
                routes.append({
                    "route_id": i + 1,
                    "summary": route.get("summary", f"Route {i + 1}"),
                    "duration": leg.get("duration_in_traffic", leg.get("duration", {})).get("text", "Unknown"),
                    "distance": leg.get("distance", {}).get("text", "Unknown"),
                    "steps_count": len(leg.get("steps", [])),
                    "source": "google_maps"
                })
        
        return routes if routes else [{"error": "No routes found"}]
        
    except Exception as e:
        print(f"Route calculation error: {e}")
        return [{"error": str(e)}]

# =============================================================================
# AGENT CLASSES
# =============================================================================

class SupervisorAgent:
    """Supervisor Agent - Orchestrates the workflow"""
    
    def __init__(self):
        self.name = "supervisor"
    
    def should_continue(self, state: Dict[str, Any]) -> str:
        """Determine which agent to run next"""
        print(f"🎯 Supervisor: Evaluating state (errors: {state.get('error_count', 0)})")
        
        # Too many errors - stop
        if state.get('error_count', 0) >= 3:
            print("❌ Supervisor: Too many errors, ending workflow")
            return "end"
        
        # Check what data we have and what we need
        if not state.get('location_data'):
            print("📍 Supervisor: Need location data")
            return "location_agent"

        if not state.get('weather_data'):
            print("🌤️ Supervisor: Need weather data")
            return "weather_agent"

        if not state.get('traffic_data'):
            print("🚗 Supervisor: Need traffic data")
            return "traffic_agent"

        if not state.get('route_options'):
            print("🛣️ Supervisor: Need route options")
            return "route_agent"

        if not state.get('final_directions'):
            print("🤖 Supervisor: Need final directions")
            return "direction_agent"
        
        print("✅ Supervisor: All done!")
        return "end"

class LocationAgent:
    """Location Agent - Finds user's location"""

    def __init__(self):
        self.name = "location_agent"
        self.tools = [get_user_location]

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        log_agent_start(self.name)

        try:
            log_api_call("IP Geolocation")
            tool = self.tools[0]  # get_user_location tool
            location_result = tool.invoke("8.8.8.8")  # Call tool with .invoke()
            state['location_data'] = location_result
            create_agent_message(
                state,
                MessageType.LOCATION_UPDATE,
                f"Location found: {location_result.get('city', 'Unknown')}, {location_result.get('region', 'Unknown')}",
                self.name
            )
            log_agent_complete(self.name)

        except Exception as e:
            state['error_count'] = state.get('error_count', 0) + 1
            create_agent_message(state, MessageType.LOCATION_UPDATE, f"Error: {str(e)}", self.name)
            log_error(f"Location Agent failed: {e}")

        return state

class WeatherAgent:
    """Weather Agent - Gets weather conditions"""
    
    def __init__(self):
        self.name = "weather_agent"
        self.tools = [get_weather_conditions]
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print("🌤️ Weather Agent: Checking weather conditions...")
        
        if not state.get("location_data"):
            state['error_count'] = state.get('error_count', 0) + 1
            create_agent_message(state, MessageType.WEATHER_UPDATE, "No location data available", self.name)
            print("❌ Weather Agent: No location data")
            return state
        
        try:
            lat = state['location_data']["latitude"]
            lon = state['location_data']["longitude"]
            weather_result = self.tools[0].invoke({"lat": float(lat), "lon": float(lon)})
            state['weather_data'] = weather_result
            create_agent_message(
                state,
                MessageType.WEATHER_UPDATE,
                f"Weather: {weather_result.get('condition', 'Unknown')}, {weather_result.get('temperature', 'Unknown')}°C",
                self.name
            )
            print(f"✅ Weather Agent: {weather_result.get('condition')}")
            
        except Exception as e:
            state['error_count'] = state.get('error_count', 0) + 1
            create_agent_message(state, MessageType.WEATHER_UPDATE, f"Error: {str(e)}", self.name)
            print(f"❌ Weather Agent failed: {e}")
        
        return state

class TrafficAgent:
    """Traffic Agent - Gets traffic conditions"""
    
    def __init__(self):
        self.name = "traffic_agent"
        self.tools = [get_traffic_conditions]
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print("🚗 Traffic Agent: Analyzing traffic conditions...")
        
        try:
            # Parse origin and destination from query
            # Handle location queries
            if state['user_query'].lower().strip() in ["where am i?", "where am i", "my location"]:
                state['traffic_data'] = {"status": "location_query"}
                create_agent_message(
                    state,
                    MessageType.TRAFFIC_UPDATE,
                    "Location query - no traffic data needed",
                    self.name
                )
                return state

            origin, destination = self.parse_locations(state['user_query'], state['location_data'])
            print(f"🚗 Traffic Agent: From {origin} to {destination}")
            
            traffic_result = self.tools[0].invoke({"origin": origin, "destination": destination})
            state['traffic_data'] = traffic_result
            
            if "error" not in traffic_result:
                delay = traffic_result.get("traffic_delay", 0)
                delay_text = f" (+{delay//60} min delay)" if delay > 0 else ""
                create_agent_message(
                    state,
                    MessageType.TRAFFIC_UPDATE,
                    f"Route: {traffic_result.get('distance', 'Unknown')}, {traffic_result.get('duration_in_traffic', 'Unknown')}{delay_text}",
                    self.name
                )
                print(f"✅ Traffic Agent: {traffic_result.get('duration_in_traffic')}")
            else:
                create_agent_message(state, MessageType.TRAFFIC_UPDATE, f"Error: {traffic_result['error']}", self.name)
                print(f"❌ Traffic Agent: {traffic_result['error']}")
                
        except Exception as e:
            state['error_count'] = state.get('error_count', 0) + 1
            create_agent_message(state, MessageType.TRAFFIC_UPDATE, f"Error: {str(e)}", self.name)
            print(f"❌ Traffic Agent failed: {e}")
        
        return state
    
    def parse_locations(self, query: str, location_data: Dict) -> tuple:
        """Simple location parsing from user query"""
        query_lower = query.lower()
        
        if " to " in query_lower:
            parts = query_lower.split(" to ")
            origin = parts[0].replace("directions from", "").replace("from", "").strip()
            destination = parts[1].strip()
        elif " from " in query_lower and " to " in query_lower:
            # Handle "directions from X to Y"
            parts = query_lower.replace("directions from ", "").split(" to ")
            origin = parts[0].strip()
            destination = parts[1].strip()
        else:
            # Assume current location as origin
            origin = f"{location_data.get('city', 'Unknown')}, {location_data.get('region', 'Unknown')}"
            destination = query_lower.replace("directions to", "").replace("to", "").replace("directions", "").strip()
        
        return origin, destination

class RouteAgent:
    """Route Agent - Calculates route options"""
    
    def __init__(self):
        self.name = "route_agent"
        self.tools = [calculate_route_options]
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print("🛣️ Route Agent: Calculating route options...")
        
        try:
            # Use same parsing as TrafficAgent
            traffic_agent = TrafficAgent()
            # Handle location queries
            if state['user_query'].lower().strip() in ["where am i?", "where am i", "my location"]:
                state['route_options'] = [{"status": "location_query"}]
                create_agent_message(
                    state,
                    MessageType.ROUTE_CALCULATION,
                    "Location query - no route options needed",
                    self.name
                )
                return state

            origin, destination = traffic_agent.parse_locations(state['user_query'], state['location_data'])
            
            route_options = self.tools[0].invoke({"origin": origin, "destination": destination})
            state['route_options'] = route_options
            
            if route_options and "error" not in route_options[0]:
                create_agent_message(
                    state,
                    MessageType.ROUTE_CALCULATION,
                    f"Found {len(route_options)} route options",
                    self.name
                )
                print(f"✅ Route Agent: Found {len(route_options)} routes")
            else:
                error_msg = route_options[0].get("error", "Unknown error") if route_options else "No routes found"
                create_agent_message(state, MessageType.ROUTE_CALCULATION, f"Error: {error_msg}", self.name)
                print(f"❌ Route Agent: {error_msg}")
                
        except Exception as e:
            state['error_count'] = state.get('error_count', 0) + 1
            create_agent_message(state, MessageType.ROUTE_CALCULATION, f"Error: {str(e)}", self.name)
            print(f"❌ Route Agent failed: {e}")
        
        return state

class DirectionAgent:
    """Direction Agent - Generates final AI-powered directions"""
    
    def __init__(self):
        self.name = "direction_agent"
        # Using GPT-3.5 for better cost management
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Define how we want the AI to respond
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful directions assistant. Create clear, conversational 
            directions based on the user's request and available data. Consider weather conditions 
            and provide practical travel advice. Be friendly and concise."""),
            ("human", """
            User Query: {query}
            Location: {location}
            Weather: {weather}
            Traffic: {traffic}
            Route Options: {routes}
            
            Provide helpful directions and travel advice:
            """)
        ])
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the final directions based on all collected data"""
        print("🤖 Direction Agent: Generating personalized directions...")
        
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
                state['final_directions'] = "\n".join(location_msg)
                create_agent_message(
                    state,
                    MessageType.FINAL_DIRECTIONS,
                    "Location information generated",
                    self.name
                )
                return state

        try:
            # For regular direction queries, use the AI assistant
            context = {
                "query": state['user_query'],
                "location": json.dumps(state.get('location_data', {}), indent=2),
                "weather": json.dumps(state.get('weather_data', {}), indent=2),
                "traffic": json.dumps(state.get('traffic_data', {}), indent=2),
                "routes": json.dumps(state.get('route_options', []), indent=2)
            }
            
            # Generate AI response
            chain = self.prompt | self.llm
            response = chain.invoke(context)
            
            # Update state with AI generated directions
            state['final_directions'] = response.content
            create_agent_message(
                state,
                MessageType.FINAL_DIRECTIONS,
                "AI-powered directions generated",
                self.name
            )
            print("✅ Direction Agent: Directions created!")
            
        except Exception as e:
            # Handle any errors gracefully
            state['error_count'] = state.get('error_count', 0) + 1
            print(f"❌ Direction Agent failed: {e}")

            # Use simpler fallback directions
            state['final_directions'] = self.create_fallback_directions(state)
            create_agent_message(
                state,
                MessageType.FINAL_DIRECTIONS,
                f"Using fallback directions due to error: {str(e)}",
                self.name
            )
        
        return state
    
    def create_fallback_directions(self, state: Dict[str, Any]) -> str:
        """Create basic directions when AI fails"""
        directions = f"Here are your directions for: {state['user_query']}\n\n"

        if state.get('location_data'):
            directions += f"📍 Your location: {state['location_data'].get('city')}, {state['location_data'].get('region')}\n"

        if state.get('weather_data'):
            directions += f"🌤️ Weather: {state['weather_data'].get('condition')}, {state['weather_data'].get('temperature')}°C\n"

        if state.get('traffic_data') and "error" not in state['traffic_data']:
            directions += f"🚗 Route: {state['traffic_data'].get('distance')} in {state['traffic_data'].get('duration_in_traffic')}\n"
            if state['traffic_data'].get("traffic_delay", 0) > 0:
                directions += f"⚠️ Traffic delay: {state['traffic_data']['traffic_delay']//60} minutes\n"
        
        directions += "\nHave a safe trip!"
        return directions

# =============================================================================
# LANGGRAPH WORKFLOW SETUP
# =============================================================================

def create_agent_message(state: Dict[str, Any], msg_type: MessageType, content: str, agent: str) -> None:
    """Helper to add messages to state dictionary"""
    if "messages" not in state:
        state["messages"] = []
    state["messages"].append({
        "type": msg_type.value,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "agent": agent
    })

class MultiAgentDirectionSystem:
    """Main system that orchestrates all agents using LangGraph"""
    
    def __init__(self):
        # Initialize all agents
        self.supervisor = SupervisorAgent()
        self.location_agent = LocationAgent()
        self.weather_agent = WeatherAgent()
        self.traffic_agent = TrafficAgent()
        self.route_agent = RouteAgent()
        self.direction_agent = DirectionAgent()
        
        # Build the LangGraph workflow
        self.workflow = self.build_workflow()
    
    def build_workflow(self) -> StateGraph:
        """Build the LangGraph state machine"""
        print("🔧 Building LangGraph workflow...")
        
        # Create the state graph using dict type
        workflow = StateGraph(Dict)
        
        # Add all agent nodes
        workflow.add_node("supervisor", self.supervisor_node)
        workflow.add_node("location_agent", self.location_agent.execute)
        workflow.add_node("weather_agent", self.weather_agent.execute)
        workflow.add_node("traffic_agent", self.traffic_agent.execute)
        workflow.add_node("route_agent", self.route_agent.execute)
        workflow.add_node("direction_agent", self.direction_agent.execute)
        
        # Set entry point
        workflow.set_entry_point("supervisor")
        
        # Add conditional edges from supervisor
        workflow.add_conditional_edges(
            "supervisor",
            self.supervisor.should_continue,
            {
                "location_agent": "location_agent",
                "weather_agent": "weather_agent",
                "traffic_agent": "traffic_agent",
                "route_agent": "route_agent",
                "direction_agent": "direction_agent",
                "end": END
            }
        )
        
        # All agents return to supervisor for next decision
        for agent_name in ["location_agent", "weather_agent", "traffic_agent", "route_agent", "direction_agent"]:
            workflow.add_edge(agent_name, "supervisor")
        
        # Compile the workflow
        compiled_workflow = workflow.compile()
        print("✅ LangGraph workflow built successfully")
        return compiled_workflow
    
    def supervisor_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Supervisor node - just passes through state for decision making"""
        return state
    
    def process_request(self, user_query: str) -> Dict[str, Any]:
        """Process a direction request through the multi-agent system"""
        # Start metrics tracking
        metrics = SimpleMetrics()
        metrics.start_request(user_query)

        # Create initial state with explicit initialization of all fields
        initial_state = create_initial_state(user_query)
        create_agent_message(initial_state, MessageType.USER_REQUEST, user_query, "user")

        start_time = datetime.now()

        try:
            # Run the workflow
            final_state = self.workflow.invoke(initial_state)

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()

            # Update metrics
            metrics.finish_request(success=True)

            log_success(f"Request completed in {processing_time:.2f} seconds")

            return {
                "directions": final_state.get('final_directions', ''),
                "location": final_state.get('location_data', {}),
                "weather": final_state.get('weather_data', {}),
                "traffic": final_state.get('traffic_data', {}),
                "route_options": final_state.get('route_options', []),
                "processing_time": processing_time,
                "messages_exchanged": len(final_state.get('messages', [])),
                "errors_encountered": final_state.get('error_count', 0),
                "conversation_log": final_state.get('messages', [])
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
# FASTAPI WEB INTERFACE
# =============================================================================

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Direction System",
    description="Student-friendly multi-agent AI system for intelligent directions",
    version="1.0.0"
)

# Initialize the direction system
print("🚀 Initializing Multi-Agent Direction System...")
direction_system = MultiAgentDirectionSystem()

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
        "message": "🚀 Multi-Agent Direction System is running!",
        "agents": ["supervisor", "location", "weather", "traffic", "route", "direction"],
        "usage": "POST to /directions with {'query': 'your direction request'}"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agents": {
            "supervisor": "active",
            "location_agent": "active",
            "weather_agent": "active", 
            "traffic_agent": "active",
            "route_agent": "active",
            "direction_agent": "active"
        },
        "timestamp": datetime.now().isoformat(),
        "workflow": "langgraph"
    }

@app.post("/directions", response_model=DirectionResponse)
async def get_directions(request: DirectionRequest):
    """Get directions from the multi-agent system"""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        result = direction_system.process_request(request.query)
        return DirectionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System error: {str(e)}")

@app.get("/test")
async def test_system():
    """Test the system with sample queries"""
    test_queries = [
        "directions to Times Square",
        "how do I get to Central Park",
        "route to JFK airport"
    ]

    results = {}
    for query in test_queries:
        try:
            result = direction_system.process_request(query)
            results[query] = {
                "success": True,
                "processing_time": result["processing_time"],
                "directions_preview": result["directions"][:100] + "..." if len(result["directions"]) > 100 else result["directions"]
            }
        except Exception as e:
            results[query] = {
                "success": False,
                "error": str(e)
            }

    return {
        "system_status": "operational",
        "test_results": results,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/metrics")
async def get_metrics():
    """Get simple system metrics"""
    return get_simple_stats()

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🎓 STUDENT MVP: MULTI-AGENT DIRECTION SYSTEM")
    print("=" * 60)
    
    # Check API keys
    if not check_api_keys():
        print("\n❌ Setup required:")
        print("1. Create a .env file")
        print("2. Add your API keys:")
        print("   OPENAI_API_KEY=your-key-here")
        print("   GOOGLE_MAPS_API_KEY=your-key-here")
        print("   WEATHER_API_KEY=your-key-here")
        exit(1)
    
    print("\n✅ System ready!")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🧪 Test endpoint: http://localhost:8000/test")
    print("💬 Example: curl -X POST http://localhost:8000/directions -H 'Content-Type: application/json' -d '{\"query\": \"directions to Times Square\"}'")
    print("\n🚀 Starting server...\n")
    
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
