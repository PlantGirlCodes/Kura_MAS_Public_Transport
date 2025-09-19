# test_system.py - Simple test script
import requests
import json
from datetime import datetime

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Multi-Agent Direction System")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Agents: {response.json()['agents']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 3: Built-in test endpoint
    print("\n3. Testing system with built-in test...")
    try:
        response = requests.get(f"{base_url}/test")
        if response.status_code == 200:
            print("✅ System test passed")
            result = response.json()
            print(f"   Query: {result['test_query']}")
            directions = result['result']['directions'][:100] + "..." if len(result['result']['directions']) > 100 else result['result']['directions']
            print(f"   Directions: {directions}")
        else:
            print(f"❌ System test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ System test error: {e}")
    
    # Test 4: Custom direction request
    print("\n4. Testing custom direction request...")
    test_queries = [
        "directions to Central Park",
        "how do I get to JFK airport",
        "route to Brooklyn Bridge"
    ]
    
    for query in test_queries:
        try:
            print(f"\n   Testing: '{query}'")
            response = requests.post(
                f"{base_url}/directions",
                json={"query": query},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("   ✅ Success!")
                print(f"   📍 Location: {result['location']['city']}")
                print(f"   🌤️ Weather: {result['weather']['condition']}")
                
                # Show first part of directions
                directions = result['directions'][:150] + "..." if len(result['directions']) > 150 else result['directions']
                print(f"   🗺️ Directions: {directions}")
                
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Testing complete!")
    print("\nIf you see ✅ marks above, your system is working!")
    print("If you see ❌ marks, check your API keys in the .env file")

if __name__ == "__main__":
    test_api_endpoints()

# ---

# simple_sms.py - Optional SMS integration (for students who want to try it)
from fastapi import FastAPI, Form
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

# This would be added to your main.py if you want SMS features
class SimpleSMSHandler:
    """Simple SMS handler for Twilio integration"""
    
    def __init__(self, direction_system):
        self.direction_system = direction_system
        self.twilio_client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
    
    def handle_sms(self, from_number: str, message_body: str) -> str:
        """Process SMS message and return response"""
        try:
            # Check if it's a direction request
            direction_keywords = ["directions", "route", "how to get", "navigate"]
            
            if any(keyword in message_body.lower() for keyword in direction_keywords):
                # Process through our multi-agent system
                result = self.direction_system.get_directions(message_body)
                
                # Format response for SMS (160 character limit considerations)
                directions = result["directions"]
                if len(directions) > 1500:  # SMS has limits
                    directions = directions[:1500] + "... (Reply 'more' for full directions)"
                
                return directions
            else:
                return ("Hi! I can help you with directions. Try asking: "
                       "'directions to Times Square' or 'how do I get to Central Park?'")
                
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)[:100]}. Please try again."
    
    def send_sms(self, to_number: str, message: str):
        """Send SMS message"""
        try:
            message = self.twilio_client.messages.create(
                body=message,
                from_=os.getenv("TWILIO_PHONE_NUMBER"),
                to=to_number
            )
            return message.sid
        except Exception as e:
            print(f"SMS send error: {e}")
            return None

# Add this to your main.py FastAPI app if you want SMS:
"""
# Initialize SMS handler (only if Twilio credentials are available)
sms_handler = None
if os.getenv("TWILIO_ACCOUNT_SID") and os.getenv("TWILIO_AUTH_TOKEN"):
    sms_handler = SimpleSMSHandler(direction_system)
    print("📱 SMS integration enabled")

@app.post("/sms/webhook")
async def sms_webhook(From: str = Form(...), Body: str = Form(...)):
    '''Twilio SMS webhook endpoint'''
    if not sms_handler:
        return {"error": "SMS not configured"}
    
    # Process the SMS
    response_text = sms_handler.handle_sms(From, Body)
    
    # Create TwiML response
    resp = MessagingResponse()
    resp.message(response_text)
    
    return str(resp)

@app.get("/sms/test")
async def test_sms(phone: str, message: str = "Test from direction system"):
    '''Test SMS sending'''
    if not sms_handler:
        return {"error": "SMS not configured"}
    
    message_sid = sms_handler.send_sms(phone, message)
    if message_sid:
        return {"status": "sent", "message_sid": message_sid}
    else:
        return {"error": "Failed to send SMS"}
"""

# ---

# budget_tracker.py - Help students track API costs
import requests
import json
from datetime import datetime, timedelta

class BudgetTracker:
    """Simple budget tracking for API usage"""
    
    def __init__(self):
        self.usage_file = "api_usage.json"
        self.load_usage()
    
    def load_usage(self):
        """Load usage from file"""
        try:
            with open(self.usage_file, 'r') as f:
                self.usage = json.load(f)
        except FileNotFoundError:
            self.usage = {
                "openai_requests": 0,
                "google_maps_requests": 0, 
                "weather_requests": 0,
                "start_date": datetime.now().isoformat(),
                "estimated_cost": 0.0
            }
            self.save_usage()
    
    def save_usage(self):
        """Save usage to file"""
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage, f, indent=2)
    
    def track_request(self, service: str):
        """Track a request to a service"""
        if service == "openai":
            self.usage["openai_requests"] += 1
            # GPT-3.5-turbo: ~$0.002 per 1K tokens, estimate 500 tokens per request
            self.usage["estimated_cost"] += 0.001  # $0.001 per request
        
        elif service == "google_maps":
            self.usage["google_maps_requests"] += 1
            # Free tier: $200 credit, ~$0.005 per request after free tier
            # For students, this will likely stay free
            
        elif service == "weather":
            self.usage["weather_requests"] += 1
            # Free tier: 1000 requests/day, then ~$0.0015 per request
            if self.usage["weather_requests"] > 1000:
                self.usage["estimated_cost"] += 0.0015
        
        self.save_usage()
    
    def get_budget_status(self) -> dict:
        """Get current budget status"""
        days_running = (datetime.now() - datetime.fromisoformat(self.usage["start_date"])).days + 1
        
        return {
            "days_running": days_running,
            "total_requests": (
                self.usage["openai_requests"] + 
                self.usage["google_maps_requests"] + 
                self.usage["weather_requests"]
            ),
            "openai_requests": self.usage["openai_requests"],
            "google_maps_requests": self.usage["google_maps_requests"],
            "weather_requests": self.usage["weather_requests"],
            "estimated_cost": round(self.usage["estimated_cost"], 2),
            "budget_remaining": max(0, 20 - self.usage["estimated_cost"]),
            "daily_average_cost": round(self.usage["estimated_cost"] / days_running, 3)
        }
    
    def print_budget_report(self):
        """Print a budget report"""
        status = self.get_budget_status()
        
        print("\n💰 Budget Report")
        print("=" * 30)
        print(f"Days running: {status['days_running']}")
        print(f"Total requests: {status['total_requests']}")
        print(f"  • OpenAI: {status['openai_requests']}")
        print(f"  • Google Maps: {status['google_maps_requests']}")
        print(f"  • Weather: {status['weather_requests']}")
        print(f"Estimated cost: ${status['estimated_cost']}")
        print(f"Budget remaining: ${status['budget_remaining']}")
        print(f"Daily average: ${status['daily_average_cost']}")
        
        if status['estimated_cost'] > 15:
            print("⚠️ Warning: Approaching $20 budget limit!")
        elif status['estimated_cost'] < 5:
            print("✅ Well within budget - great job!")
        else:
            print("👍 Budget looking good")

# Usage in main.py:
"""
# Add budget tracking to your main system
budget_tracker = BudgetTracker()

# In your DirectionAgent.__init__:
def get_directions(self, user_query: str) -> Dict[str, Any]:
    # Track the request
    budget_tracker.track_request("openai")
    # ... rest of the method

# Add budget endpoint to FastAPI:
@app.get("/budget")
async def get_budget_status():
    return budget_tracker.get_budget_status()
"""

# ---

# github_setup.py - Help set up GitHub repository
import os
import subprocess

def setup_github_repo():
    """Help students set up their GitHub repository"""
    
    print("🐙 GitHub Repository Setup")
    print("=" * 30)
    
    # Check if git is installed
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        print(f"✅ Git found: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Git not found. Please install Git first.")
        return
    
    # Check if already a git repo
    if os.path.exists('.git'):
        print("✅ Already a Git repository")
    else:
        print("🔧 Initializing Git repository...")
        subprocess.run(['git', 'init'])
        
    # Create basic .gitignore if it doesn't exist
    if not os.path.exists('.gitignore'):
        gitignore_content = """# Python
__pycache__/
*.pyc
.Python

# Environment
.env
.venv/
env/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
api_usage.json
"""
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        print("✅ Created .gitignore")
    
    # Create README if it doesn't exist
    if not os.path.exists('README.md'):
        readme_content = """# Multi-Agent Direction System

A simple multi-agent AI system for intelligent directions.

## Setup

1. Install requirements: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your API keys
3. Run: `python main.py`
4. Test: http://localhost:8000/test

## API Keys Needed

- OpenAI API Key
- Google Maps API Key  
- Weather API Key

All have free tiers!

## Usage

```bash
# Test the system
python test_system.py

# Check budget
python -c "from budget_tracker import BudgetTracker; BudgetTracker().print_budget_report()"
```

Built for CS students! 🎓
"""
        with open('README.md', 'w') as f:
            f.write(readme_content)
        print("✅ Created README.md")
    
    # Stage files
    print("📦 Staging files for commit...")
    files_to_add = [
        'main.py', 'requirements.txt', 'README.md', '.gitignore',
        'Dockerfile', 'docker-compose.yml'
    ]
    
    for file in files_to_add:
        if os.path.exists(file):
            subprocess.run(['git', 'add', file])
            print(f"   Added {file}")
    
    print("\n🚀 Next steps:")
    print("1. Create repository on GitHub.com")
    print("2. Run: git commit -m 'Initial commit - Multi-agent direction system'")
    print("3. Run: git branch -M main")
    print("4. Run: git remote add origin YOUR_REPO_URL")  
    print("5. Run: git push -u origin main")
    print("\n⚠️ Remember: NEVER commit your .env file with API keys!")

if __name__ == "__main__":
    setup_github_repo()
