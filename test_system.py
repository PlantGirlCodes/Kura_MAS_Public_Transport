#!/usr/bin/env python3
"""
Simple Test Script for Transport Multi-Agent System
Run this to quickly test your system before competition!
"""
import requests
import time
import json
from datetime import datetime

def test_system():
    """Run automated tests on the system"""
    base_url = "http://localhost:8000"

    print("🧪 AUTOMATED TESTING STARTING...")
    print("=" * 50)

    # Test 1: Health Check
    print("\n1️⃣ Testing Health Endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check PASSED")
            data = response.json()
            print(f"   Agents active: {len(data.get('agents', {}))}")
        else:
            print(f"❌ Health check FAILED: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check ERROR: {e}")
        print("   Make sure to run: python main.py")
        return False

    # Test 2: Basic Direction Request
    print("\n2️⃣ Testing Basic Public Transport Request...")
    test_query = "public transport to Times Square"
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/directions",
            json={"query": test_query},
            timeout=30
        )
        response_time = time.time() - start_time

        if response.status_code == 200:
            print("✅ Direction request PASSED")
            data = response.json()
            print(f"   Response time: {response_time:.2f} seconds")
            print(f"   Agents used: {data.get('messages_exchanged', 0)}")
            print(f"   Errors: {data.get('errors_encountered', 0)}")

            # Check if we got real directions
            directions = data.get('directions', '')
            if len(directions) > 50:
                print("✅ Got detailed directions")
                print(f"   Preview: {directions[:100]}...")
            else:
                print("⚠️ Directions seem short, check APIs")

        else:
            print(f"❌ Direction request FAILED: Status {response.status_code}")
            print(f"   Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Direction request ERROR: {e}")
        return False

    # Test 3: Mobile-Style Query
    print("\n3️⃣ Testing Mobile-Style Query...")
    mobile_queries = [
        "bus to airport",
        "subway downtown",
        "transit to Central Park"
    ]

    for query in mobile_queries:
        try:
            response = requests.post(
                f"{base_url}/directions",
                json={"query": query},
                timeout=20
            )
            if response.status_code == 200:
                print(f"✅ '{query}' - SUCCESS")
            else:
                print(f"❌ '{query}' - FAILED ({response.status_code})")
        except Exception as e:
            print(f"❌ '{query}' - ERROR: {e}")

    # Test 4: Metrics Check
    print("\n4️⃣ Testing Metrics Endpoint...")
    try:
        response = requests.get(f"{base_url}/metrics", timeout=10)
        if response.status_code == 200:
            print("✅ Metrics endpoint PASSED")
            data = response.json()
            if isinstance(data, dict) and "total_requests" in data:
                print(f"   Total requests: {data.get('total_requests', 0)}")
                print(f"   Success rate: {data.get('success_rate', 'N/A')}")
            else:
                print("   No metrics data yet (expected for first run)")
        else:
            print(f"❌ Metrics endpoint FAILED: {response.status_code}")
    except Exception as e:
        print(f"❌ Metrics check ERROR: {e}")

    # Test 5: Error Handling
    print("\n5️⃣ Testing Error Handling...")
    try:
        # Test empty query
        response = requests.post(
            f"{base_url}/directions",
            json={"query": ""},
            timeout=10
        )
        if response.status_code == 400:
            print("✅ Empty query handling PASSED")
        else:
            print(f"⚠️ Empty query returned: {response.status_code}")

        # Test invalid query
        response = requests.post(
            f"{base_url}/directions",
            json={"query": "asdfghjkl123456"},
            timeout=20
        )
        if response.status_code == 200:
            print("✅ Invalid query handled gracefully")
        else:
            print(f"⚠️ Invalid query failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Error handling test ERROR: {e}")

    print("\n" + "=" * 50)
    print("🎯 TESTING COMPLETE!")
    print("\nNext Steps:")
    print("1. Check logs/system.log for detailed agent activity")
    print("2. Check logs/metrics.json for usage tracking")
    print("3. Test Docker: docker-compose up --build")
    print("4. Test on mobile device")
    print("5. Practice your 30-second demo!")

    return True

def check_logs():
    """Check if logs are being created"""
    print("\n📁 Checking Log Files...")
    try:
        with open("logs/system.log", "r") as f:
            lines = f.readlines()
            print(f"✅ System log: {len(lines)} entries")
            if lines:
                print(f"   Latest: {lines[-1].strip()}")
    except FileNotFoundError:
        print("⚠️ No system.log found - run a test first")

    try:
        with open("logs/metrics.json", "r") as f:
            data = json.load(f)
            print(f"✅ Metrics file: {len(data)} requests recorded")
    except FileNotFoundError:
        print("⚠️ No metrics.json found - run a test first")

if __name__ == "__main__":
    print("🚀 TRANSPORT MULTI-AGENT SYSTEM TESTER")
    print("Make sure your system is running first:")
    print("   python main.py")
    print("\nPress Enter to start testing...")
    input()

    success = test_system()
    check_logs()

    if success:
        print("\n🎉 System ready for competition!")
    else:
        print("\n🚨 Issues found - check the errors above")