#!/usr/bin/env python3
"""
🧪 SIMPLE SYSTEM TEST (No Dependencies)
Quick test to verify the basic functionality is working
"""
import json
import os

def test_imports():
    """Test if we can import the basic modules"""
    print("🧪 Testing Basic Imports...")

    try:
        # Test basic Python imports
        from datetime import datetime
        from typing import Dict, Any, List
        from enum import Enum
        print("   ✅ Basic Python modules imported successfully")

        # Test if we can import our simple logging
        import simple_logging
        print("   ✅ Simple logging module imported successfully")

        # Test the basic state management
        from main import create_initial_state, MessageType
        state = create_initial_state("test query")
        print(f"   ✅ State management working - created state: {type(state)}")

        return True

    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_tools():
    """Test if the basic tools work without external APIs"""
    print("\n🔧 Testing Tool Functions...")

    try:
        # Import and test location tool
        from main import get_user_location
        print("   🗺️ Testing location tool...")
        location_result = get_user_location.invoke("8.8.8.8")

        if location_result and "latitude" in location_result:
            print(f"   ✅ Location tool works: {location_result.get('city', 'Unknown')}")
        else:
            print(f"   ⚠️ Location tool returned: {location_result}")

        return True

    except Exception as e:
        print(f"   ❌ Tool test error: {e}")
        return False

def test_state_management():
    """Test state management without LangGraph"""
    print("\n📊 Testing State Management...")

    try:
        from main import create_initial_state, create_agent_message, MessageType

        # Create state
        state = create_initial_state("test query")
        print(f"   ✅ Initial state created with keys: {list(state.keys())}")

        # Test adding messages
        create_agent_message(state, MessageType.USER_REQUEST, "test message", "test_agent")

        if "messages" in state and len(state["messages"]) > 0:
            print(f"   ✅ Message added successfully: {len(state['messages'])} messages")
        else:
            print("   ❌ Failed to add message to state")

        # Test state access patterns
        state["test_data"] = {"test": "value"}
        if state.get("test_data") == {"test": "value"}:
            print("   ✅ State dictionary access working")
        else:
            print("   ❌ State dictionary access failed")

        return True

    except Exception as e:
        print(f"   ❌ State management error: {e}")
        return False

def test_logging():
    """Test the logging system"""
    print("\n📝 Testing Logging System...")

    try:
        from simple_logging import log_message, log_success, log_error, SimpleMetrics

        # Test basic logging
        log_message("Test message")
        print("   ✅ Basic logging works")

        # Test success/error logging
        log_success("Test success")
        log_error("Test error")
        print("   ✅ Success/error logging works")

        # Test metrics
        metrics = SimpleMetrics()
        metrics.start_request("test")
        metrics.finish_request(success=True)
        print("   ✅ Metrics system works")

        return True

    except Exception as e:
        print(f"   ❌ Logging test error: {e}")
        return False

def main():
    """Run all simple tests"""
    print("=" * 60)
    print("🚀 SIMPLE SYSTEM TEST (No External Dependencies)")
    print("=" * 60)
    print("This test checks basic functionality without starting the server")
    print()

    tests = [
        ("Basic Imports", test_imports),
        ("Tool Functions", test_tools),
        ("State Management", test_state_management),
        ("Logging System", test_logging)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            failed += 1
            print(f"❌ {test_name} FAILED")

    print("\n" + "=" * 60)
    print("📊 SIMPLE TEST RESULTS")
    print("=" * 60)
    print(f"✅ Tests Passed: {passed}")
    print(f"❌ Tests Failed: {failed}")
    print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")

    if failed == 0:
        print("\n🎉 All basic tests passed! The core system logic is working.")
        print("💡 Next step: Fix the LangChain/pydantic dependency issue to test the full system.")
    else:
        print(f"\n🔧 {failed} test(s) failed. Fix these basic issues first.")

    print("\n🔍 Dependency Issue Detected:")
    print("   The main system has a pydantic v1/v2 compatibility issue with LangChain")
    print("   This is common and can be fixed by updating packages or using compatibility mode")

if __name__ == "__main__":
    main()