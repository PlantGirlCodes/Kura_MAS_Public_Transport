#!/usr/bin/env python3
"""
🧪 BEGINNER-FRIENDLY TEST SCRIPT 🧪
Transport Multi-Agent System Testing Suite

This script will:
1. ✅ Check if your system is running
2. 🚌 Test public transport direction requests
3. 📱 Test mobile-style queries
4. 📊 Check system metrics
5. 🛡️ Test error handling
6. 📋 Generate a detailed report

Perfect for beginners to understand what's working!
"""
import requests
import time
import json
from datetime import datetime
import sys
import os

def test_system():
    """Run automated tests on the system with beginner explanations"""
    base_url = "http://localhost:8000"
    test_results = {"passed": 0, "failed": 0, "warnings": 0}

    print("\n" + "=" * 60)
    print("🎆 WELCOME TO THE BEGINNER-FRIENDLY TEST SUITE! 🎆")
    print("=" * 60)
    print("📚 What this script does:")
    print("   - Tests if your multi-agent system is working")
    print("   - Checks if public transport directions are accurate")
    print("   - Validates error handling for edge cases")
    print("   - Provides detailed feedback for debugging")
    print("\n🚀 Let's begin testing...\n")

    # Test 1: Health Check
    print("🩺 Test 1: Health Check")
    print("-" * 30)
    print("📝 Purpose: Verify that your FastAPI server is running and all agents are active")
    print("🛠️ What we're testing: GET /health endpoint")

    try:
        print("🔍 Sending request to health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=10)

        if response.status_code == 200:
            print("✅ SUCCESS: Health check PASSED!")
            data = response.json()
            agents_count = len(data.get('agents', {}))
            print(f"   🤖 Active agents detected: {agents_count}")
            print(f"   🕰️ System timestamp: {data.get('timestamp', 'Unknown')}")
            print(f"   ⚙️ Workflow engine: {data.get('workflow', 'Unknown')}")
            test_results["passed"] += 1

            if agents_count < 6:
                print(f"   ⚠️ WARNING: Expected 6 agents, found {agents_count}")
                test_results["warnings"] += 1
        else:
            print(f"❌ FAILED: Health check returned status {response.status_code}")
            print(f"   💬 Response: {response.text[:100]}")
            test_results["failed"] += 1
            return False

    except requests.ConnectionError:
        print("❌ FAILED: Cannot connect to server")
        print("   🛠️ SOLUTION: Make sure to run 'python main.py' first")
        print("   📍 Check that port 8000 is available")
        test_results["failed"] += 1
        return False
    except Exception as e:
        print(f"❌ ERROR: Unexpected error - {e}")
        test_results["failed"] += 1
        return False

    # Test 2: Basic Direction Request
    print("\n\n🚨 Test 2: Basic Public Transport Request")
    print("-" * 45)
    print("📝 Purpose: Test the core functionality - getting public transport directions")
    print("🛠️ What we're testing: POST /directions with a typical user query")

    test_query = "public transport to Times Square"
    print(f"💬 Test query: '{test_query}'")

    try:
        print("🔍 Sending direction request...")
        start_time = time.time()
        response = requests.post(
            f"{base_url}/directions",
            json={"query": test_query},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response_time = time.time() - start_time

        print(f"⏱️ Response received in {response_time:.2f} seconds")

        if response.status_code == 200:
            print("✅ SUCCESS: Direction request PASSED!")
            data = response.json()

            # Detailed analysis
            print("\n📋 RESPONSE ANALYSIS:")
            print(f"   🕰️ Processing time: {data.get('processing_time', 0):.2f}s")
            print(f"   💬 Messages exchanged: {data.get('messages_exchanged', 0)}")
            print(f"   ❌ Errors encountered: {data.get('errors_encountered', 0)}")

            # Check directions quality
            directions = data.get('directions', '')
            if len(directions) > 100:
                print(f"   ✅ Got detailed directions ({len(directions)} characters)")
                print(f"   📝 Preview: {directions[:150]}...")
                test_results["passed"] += 1
            elif len(directions) > 20:
                print(f"   ⚠️ Got basic directions ({len(directions)} characters)")
                print(f"   📝 Content: {directions}")
                test_results["warnings"] += 1
            else:
                print(f"   ❌ Directions too short ({len(directions)} characters)")
                print("   🛠️ This might indicate API key issues")
                test_results["failed"] += 1

            # Check individual components
            print("\n🧪 COMPONENT CHECK:")
            location = data.get('location', {})
            weather = data.get('weather', {})
            traffic = data.get('traffic', {})
            routes = data.get('route_options', [])

            print(f"   📍 Location data: {'✅ Present' if location else '❌ Missing'}")
            print(f"   🌤️ Weather data: {'✅ Present' if weather else '❌ Missing'}")
            print(f"   🚗 Traffic data: {'✅ Present' if traffic else '❌ Missing'}")
            print(f"   🛣️ Route options: {'✅ Present' if routes else '❌ Missing'}")

        else:
            print(f"❌ FAILED: Direction request returned status {response.status_code}")
            print(f"   💬 Error response: {response.text[:200]}")
            test_results["failed"] += 1
            return False

    except requests.Timeout:
        print("❌ FAILED: Request timed out (>30 seconds)")
        print("   🛠️ This might indicate slow API responses or infinite loops")
        test_results["failed"] += 1
        return False
    except Exception as e:
        print(f"❌ ERROR: Unexpected error - {e}")
        test_results["failed"] += 1
        return False

    # Test 3: Mobile-Style Queries
    print("\n\n📱 Test 3: Mobile-Style Queries")
    print("-" * 35)
    print("📝 Purpose: Test how the system handles short, mobile-style queries")
    print("🛠️ What we're testing: Various quick direction requests")

    mobile_queries = [
        "bus to airport",
        "subway downtown",
        "transit to Central Park",
        "where am I?"
    ]

    mobile_results = {"success": 0, "failed": 0}

    for i, query in enumerate(mobile_queries, 1):
        print(f"\n   📱 Query {i}: '{query}'")
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/directions",
                json={"query": query},
                timeout=20
            )
            response_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                directions_length = len(data.get('directions', ''))
                print(f"      ✅ SUCCESS ({response_time:.1f}s, {directions_length} chars)")
                mobile_results["success"] += 1
            else:
                print(f"      ❌ FAILED (Status: {response.status_code})")
                mobile_results["failed"] += 1

        except requests.Timeout:
            print(f"      ❌ TIMEOUT (>20s)")
            mobile_results["failed"] += 1
        except Exception as e:
            print(f"      ❌ ERROR: {str(e)[:50]}")
            mobile_results["failed"] += 1

    print(f"\n📋 Mobile Query Results: {mobile_results['success']}/{len(mobile_queries)} successful")
    if mobile_results["success"] == len(mobile_queries):
        test_results["passed"] += 1
    elif mobile_results["success"] > 0:
        test_results["warnings"] += 1
    else:
        test_results["failed"] += 1

    # Test 4: Metrics & Monitoring
    print("\n\n📊 Test 4: Metrics & Monitoring")
    print("-" * 35)
    print("📝 Purpose: Verify system monitoring and metrics collection")
    print("🛠️ What we're testing: GET /metrics endpoint and log files")

    try:
        print("🔍 Checking metrics endpoint...")
        response = requests.get(f"{base_url}/metrics", timeout=10)

        if response.status_code == 200:
            print("✅ SUCCESS: Metrics endpoint responding!")
            data = response.json()

            if isinstance(data, dict) and "total_requests" in data:
                print("\n📋 METRICS SUMMARY:")
                print(f"   📊 Total requests: {data.get('total_requests', 0)}")
                print(f"   ✅ Success rate: {data.get('success_rate', 'N/A')}")
                print(f"   ⏱️ Average time: {data.get('average_time', 'N/A')}")
                print(f"   ❌ Total errors: {data.get('total_errors', 0)}")
                test_results["passed"] += 1
            else:
                print("   ⚠️ No metrics data yet (normal for first run)")
                test_results["warnings"] += 1
        else:
            print(f"❌ FAILED: Metrics endpoint returned {response.status_code}")
            test_results["failed"] += 1

    except Exception as e:
        print(f"❌ ERROR: Metrics check failed - {e}")
        test_results["failed"] += 1

    # Check log files
    print("\n📋 Checking log files...")
    log_files = ["logs/system.log", "logs/metrics.json"]

    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"   ✅ {log_file}: {size} bytes")
        else:
            print(f"   ❌ {log_file}: Missing")

    # Test 5: Error Handling & Edge Cases
    print("\n\n🛡️ Test 5: Error Handling & Edge Cases")
    print("-" * 45)
    print("📝 Purpose: Test system robustness with invalid inputs")
    print("🛠️ What we're testing: Empty queries, invalid data, malformed requests")

    error_tests = [
        {"name": "Empty query", "data": {"query": ""}, "expected_status": 400},
        {"name": "Nonsense query", "data": {"query": "asdfghjkl123456"}, "expected_status": 200},
        {"name": "Very long query", "data": {"query": "a" * 1000}, "expected_status": 200},
        {"name": "Special characters", "data": {"query": "@#$%^&*()"}, "expected_status": 200},
    ]

    error_results = {"passed": 0, "failed": 0}

    for test in error_tests:
        print(f"\n   🧪 {test['name']}:")
        try:
            response = requests.post(
                f"{base_url}/directions",
                json=test["data"],
                timeout=15
            )

            if response.status_code == test["expected_status"]:
                print(f"      ✅ Handled correctly (Status: {response.status_code})")
                error_results["passed"] += 1
            else:
                print(f"      ⚠️ Unexpected status: {response.status_code} (expected {test['expected_status']})")
                error_results["failed"] += 1

        except requests.Timeout:
            print(f"      ❌ TIMEOUT (system might be hanging)")
            error_results["failed"] += 1
        except Exception as e:
            print(f"      ❌ ERROR: {str(e)[:50]}")
            error_results["failed"] += 1

    print(f"\n📋 Error Handling Results: {error_results['passed']}/{len(error_tests)} tests passed")

    if error_results["passed"] == len(error_tests):
        test_results["passed"] += 1
    elif error_results["passed"] > len(error_tests) // 2:
        test_results["warnings"] += 1
    else:
        test_results["failed"] += 1

    # Generate Final Report
    print("\n\n" + "=" * 70)
    print("🏁 TESTING COMPLETE - FINAL REPORT")
    print("=" * 70)

    total_tests = test_results["passed"] + test_results["failed"] + test_results["warnings"]
    success_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0

    print(f"📋 SUMMARY:")
    print(f"   ✅ Tests Passed: {test_results['passed']}")
    print(f"   ⚠️ Warnings: {test_results['warnings']}")
    print(f"   ❌ Tests Failed: {test_results['failed']}")
    print(f"   📊 Success Rate: {success_rate:.1f}%")

    if test_results["failed"] == 0:
        print("\n🎆 EXCELLENT! Your system is working perfectly!")
        print("🚀 You're ready for production testing.")
    elif test_results["failed"] <= 2:
        print("\n🟡 GOOD! Minor issues detected but core functionality works.")
        print("🛠️ Fix the failed tests and you'll be ready to go!")
    else:
        print("\n🔴 NEEDS WORK! Several issues detected.")
        print("📝 Please review the failed tests and fix the underlying issues.")

    print("\n📝 NEXT STEPS FOR BEGINNERS:")
    print("   1️⃣ 📜 Check logs/system.log for detailed agent activity")
    print("   2️⃣ 📊 Review logs/metrics.json for performance tracking")
    print("   3️⃣ 🐳 Test with Docker: docker-compose up --build")
    print("   4️⃣ 📱 Test on a mobile device for real-world usage")
    print("   5️⃣ 🎤 Practice your 30-second demo presentation!")

    if test_results["failed"] > 0:
        print("\n🛠️ DEBUGGING TIPS:")
        print("   - Check if all API keys are set in .env file")
        print("   - Verify internet connection for external APIs")
        print("   - Look for error messages in the console output")
        print("   - Try restarting the server: Ctrl+C then 'python main.py'")

    print("\n👨‍💻 DEVELOPER RESOURCES:")
    print("   - API Documentation: http://localhost:8000/docs")
    print("   - Interactive Testing: http://localhost:8000")
    print("   - Health Check: http://localhost:8000/health")
    print("   - Metrics: http://localhost:8000/metrics")

    return test_results["failed"] == 0

def check_logs():
    """Detailed log analysis for beginners"""
    print("\n" + "=" * 50)
    print("📁 DETAILED LOG ANALYSIS")
    print("=" * 50)

    # Check system log
    print("📜 System Log Analysis:")
    try:
        with open("logs/system.log", "r") as f:
            lines = f.readlines()
            print(f"   ✅ Found system.log with {len(lines)} entries")

            if lines:
                recent_lines = lines[-5:]  # Last 5 entries
                print("   🕰️ Recent activity:")
                for line in recent_lines:
                    line = line.strip()
                    if "ERROR" in line:
                        print(f"      ❌ {line}")
                    elif "SUCCESS" in line:
                        print(f"      ✅ {line}")
                    else:
                        print(f"      📝 {line}")

                # Count error vs success
                errors = sum(1 for line in lines if "ERROR" in line)
                successes = sum(1 for line in lines if "SUCCESS" in line)
                print(f"   📊 Statistics: {successes} successes, {errors} errors")

    except FileNotFoundError:
        print("   ⚠️ No system.log found - this is normal for the first run")
        print("   📝 Logs will be created when you make requests")

    # Check metrics
    print("\n📊 Metrics Analysis:")
    try:
        with open("logs/metrics.json", "r") as f:
            data = json.load(f)
            print(f"   ✅ Found metrics.json with {len(data)} requests recorded")

            if data:
                successful = sum(1 for entry in data if entry.get('success', False))
                failed = len(data) - successful
                avg_time = sum(entry.get('processing_time', 0) for entry in data) / len(data)

                print(f"   📊 Performance Summary:")
                print(f"      Success rate: {successful}/{len(data)} ({successful/len(data)*100:.1f}%)")
                print(f"      Average response time: {avg_time:.2f} seconds")
                print(f"      Failed requests: {failed}")

    except FileNotFoundError:
        print("   ⚠️ No metrics.json found - normal for first run")
    except json.JSONDecodeError:
        print("   ❌ metrics.json is corrupted - may need to delete and recreate")

    # File size check
    print("\n📂 File System Check:")
    if os.path.exists("logs"):
        print("   ✅ logs/ directory exists")
        for file in ["system.log", "metrics.json"]:
            path = f"logs/{file}"
            if os.path.exists(path):
                size = os.path.getsize(path)
                print(f"   📄 {file}: {size} bytes")
    else:
        print("   📌 logs/ directory will be created automatically")

def show_startup_help():
    """Show helpful information for beginners"""
    print("\n" + "=" * 70)
    print("🎓 BEGINNER'S GUIDE TO TESTING")
    print("=" * 70)
    print("📝 BEFORE RUNNING TESTS:")
    print("   1️⃣ Make sure your main system is running: 'python main.py'")
    print("   2️⃣ Check that you see 'Starting server...' message")
    print("   3️⃣ Verify your .env file has all required API keys")
    print("   4️⃣ Ensure you have internet connection for external APIs")
    print("\n🛠️ WHAT THIS TEST WILL DO:")
    print("   ✅ Check if your server is responding")
    print("   ✅ Test public transport direction requests")
    print("   ✅ Verify all 6 agents are working together")
    print("   ✅ Test error handling and edge cases")
    print("   ✅ Generate a comprehensive report")
    print("\n💡 TIP: If tests fail, don't panic! Read the error messages carefully.")

def main():
    """Main test execution with beginner-friendly interface"""
    show_startup_help()

    print("\n🚀 Ready to start testing?")
    print("Press Enter to begin, or Ctrl+C to exit...")

    try:
        input()
    except KeyboardInterrupt:
        print("\n👋 Goodbye! Run this script anytime to test your system.")
        sys.exit(0)

    success = test_system()
    check_logs()

    # Final message
    if success:
        print("\n\n🎆 CONGRATULATIONS! 🎆")
        print("🎉 Your multi-agent system is working perfectly!")
        print("🚀 You're ready for competition!")
    else:
        print("\n\n🛠️ Keep working on it!")
        print("💪 Every great system needs debugging - you've got this!")
        print("🔍 Check the error messages above for specific fixes needed.")

    print("\n👨‍💻 Happy coding! Run this test anytime to check your progress.")

if __name__ == "__main__":
    main()