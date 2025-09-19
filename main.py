#A simple multi-agent AI system for intelligent directions.

## Setup

# 1. Install requirements: `pip install -r requirements.txt`
# 2. Copy `.env.example` to `.env` and add your API keys
# 3. Run: `python main.py`
# 4. Test: http://localhost:8000/test

## API Keys Needed

# - OpenAI API Key
# - Google Maps API Key  
# - Weather API Key

# All have free tiers!

## Usage

# ```bash
# # Test the system
# python test_system.py

# # Check budget
# python -c "from budget_tracker import BudgetTracker; BudgetTracker().print_budget_report()"
# ```

# Built for CS students! 🎓
# """

import os
import subprocess

def setup_github_repo():
    readme_content = """#A simple multi-agent AI system for intelligent directions.

## Setup

# 1. Install requirements: `pip install -r requirements.txt`
# 2. Copy `.env.example` to `.env` and add your API keys
# 3. Run: `python main.py`
# 4. Test: http://localhost:8000/test

## API Keys Needed

# - OpenAI API Key
# - Google Maps API Key  
# - Weather API Key

# All have free tiers!

## Usage

# ```bash
# # Test the system
# python test_system.py

# # Check budget
# python -c "from budget_tracker import BudgetTracker; BudgetTracker().print_budget_report()"
# ```

# Built for CS students! 🎓
# """
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