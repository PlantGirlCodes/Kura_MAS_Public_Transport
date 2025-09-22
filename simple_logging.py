"""
Simple Logging for Multi-Agent Transport System
Keep it simple for beginners!
"""
import json
import time
from datetime import datetime
from pathlib import Path

# Create logs folder
Path("logs").mkdir(exist_ok=True)

def log_message(message: str, level="INFO"):
    """Simple logging function"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {level}: {message}"

    # Print to console
    print(log_entry)

    # Save to file
    with open("logs/system.log", "a") as f:
        f.write(log_entry + "\n")

def log_error(message: str):
    """Log errors"""
    log_message(f"❌ {message}", "ERROR")

def log_success(message: str):
    """Log successes"""
    log_message(f"✅ {message}", "SUCCESS")

def log_agent_start(agent_name: str):
    """Log when agent starts"""
    log_message(f"🤖 Starting {agent_name}")

def log_agent_complete(agent_name: str):
    """Log when agent completes"""
    log_message(f"✅ Completed {agent_name}")

def log_api_call(api_name: str):
    """Log API calls"""
    log_message(f"🌐 API call to {api_name}")

class SimpleMetrics:
    """Track basic metrics"""

    def __init__(self):
        self.start_time = None
        self.agents_used = []
        self.errors = 0
        self.api_calls = 0
        self.tokens_used = 0
        self.estimated_cost = 0.0

    def start_request(self, query: str):
        """Start tracking a request"""
        self.start_time = time.time()
        self.agents_used = []
        self.errors = 0
        self.api_calls = 0
        log_message(f"📊 Processing: {query}")

    def add_agent(self, agent_name: str):
        """Track agent usage"""
        self.agents_used.append(agent_name)

    def add_error(self):
        """Track errors"""
        self.errors += 1

    def add_api_call(self, api_name: str = "unknown", tokens: int = 0):
        """Track API calls with token usage"""
        self.api_calls += 1
        self.tokens_used += tokens

        # Estimate cost based on API
        if "openai" in api_name.lower():
            # GPT-3.5-turbo: $0.002/1K tokens
            self.estimated_cost += (tokens / 1000) * 0.002
        elif "google" in api_name.lower():
            # Google Maps: ~$0.005 per request (after free tier)
            self.estimated_cost += 0.005

        log_message(f"💰 Tokens used: {tokens}, Est. cost: ${self.estimated_cost:.4f}")

    def finish_request(self, success: bool = True):
        """Finish and save metrics"""
        if not self.start_time:
            return

        processing_time = time.time() - self.start_time

        # Simple metrics summary
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "processing_time": round(processing_time, 2),
            "agents_used": len(self.agents_used),
            "api_calls": self.api_calls,
            "errors": self.errors,
            "success": success
        }

        # Save to simple JSON file
        try:
            # Load existing metrics
            try:
                with open("logs/metrics.json", "r") as f:
                    all_metrics = json.load(f)
            except FileNotFoundError:
                all_metrics = []

            # Add new metrics
            all_metrics.append(metrics)

            # Save back
            with open("logs/metrics.json", "w") as f:
                json.dump(all_metrics, f, indent=2)

        except Exception as e:
            log_error(f"Could not save metrics: {e}")

        # Log summary
        log_message(f"📈 Request completed in {processing_time:.2f}s | Agents: {len(self.agents_used)} | API calls: {self.api_calls} | Errors: {self.errors}")

def get_simple_stats():
    """Get basic statistics"""
    try:
        with open("logs/metrics.json", "r") as f:
            metrics = json.load(f)

        if not metrics:
            return "No requests processed yet"

        total = len(metrics)
        successful = sum(1 for m in metrics if m.get("success", False))
        avg_time = sum(m.get("processing_time", 0) for m in metrics) / total
        total_errors = sum(m.get("errors", 0) for m in metrics)

        return {
            "total_requests": total,
            "successful_requests": successful,
            "success_rate": f"{(successful/total)*100:.1f}%",
            "average_time": f"{avg_time:.2f}s",
            "total_errors": total_errors
        }

    except FileNotFoundError:
        return "No metrics file found"
    except Exception as e:
        return f"Error reading metrics: {e}"