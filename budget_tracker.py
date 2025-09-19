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
