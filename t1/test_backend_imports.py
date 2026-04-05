#!/usr/bin/env python3
"""
Test script to verify backend imports work correctly
"""

def test_imports():
    """Test that all backend imports work"""
    try:
        print("🧪 Testing Backend Imports")
        print("=" * 40)
        
        # Test core imports
        print("📦 Testing core imports...")
        from backend.core.controller import ControllerAgent
        print("   ✅ ControllerAgent")
        
        from backend.core.execution import ExecutionEngine, TaskDispatcher
        print("   ✅ ExecutionEngine, TaskDispatcher")
        
        from backend.core.reasoning_engine import ReasoningEngine
        print("   ✅ ReasoningEngine")
        
        # Test services imports
        print("🔧 Testing service imports...")
        from backend.services.cache import RedisService
        print("   ✅ RedisService")
        
        from backend.services.database import DatabaseService
        print("   ✅ DatabaseService")
        
        from backend.services.task_completion_formatter import TaskCompletionFormatter
        print("   ✅ TaskCompletionFormatter")
        
        # Test API imports
        print("🌐 Testing API imports...")
        from backend.models.task import TaskCreateRequest, TaskStatusResponse
        print("   ✅ Task models")
        
        # Test the main app import
        print("🎯 Testing main app import...")
        from backend.api.main import app
        print("   ✅ FastAPI app")
        
        print("\n" + "=" * 40)
        print("🎉 All imports successful!")
        print("=" * 40)
        print("\n💡 The backend should start without import errors now.")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("\n🔧 Possible fixes:")
        print("   1. Make sure you're in the virtual environment")
        print("   2. Install missing packages: pip install fastapi uvicorn")
        print("   3. Check PYTHONPATH includes the project root")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n🚀 Ready to start backend: python -m backend.main")
    else:
        print("\n⚠️  Fix import issues before starting backend")
