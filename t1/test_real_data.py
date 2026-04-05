#!/usr/bin/env python3
"""
Test script to verify real data vs mock data functionality
"""

import os
import asyncio
import httpx
from backend.core.controller import ControllerAgent
from backend.agents.code_writer_agent import CodeWriterAgent
from backend.agents.web_search_agent import WebSearchAgent

async def test_controller_with_real_api():
    """Test controller agent with real GLM API"""
    print("🧠 Testing Controller Agent with GLM API")
    print("=" * 50)
    
    # Get API key from environment
    glm_api_key = os.getenv("GLM_API_KEY", "")
    
    if not glm_api_key or glm_api_key == "your-glm-api-key-here":
        print("❌ GLM API key not configured")
        print("   Run: python setup_api_keys.py")
        return False
    
    print(f"✅ GLM API key configured (length: {len(glm_api_key)})")
    
    try:
        # Initialize controller
        controller = ControllerAgent(glm_api_key=glm_api_key)
        
        # Test intent parsing
        test_intent = "Create a Python web scraper to extract product prices from Amazon"
        print(f"\n📝 Testing intent parsing: '{test_intent}'")
        
        parsed = await controller.parse_intent(test_intent)
        
        print(f"🔍 Parsed intent:")
        print(f"   Task Type: {parsed.get('task_type')}")
        print(f"   Priority: {parsed.get('priority')}")
        print(f"   Confidence: {parsed.get('confidence')}")
        print(f"   Reasoning: {parsed.get('reasoning')}")
        
        # Test task graph generation
        print(f"\n🏗️  Testing task graph generation...")
        task_graph = await controller.generate_task_graph(parsed)
        
        print(f"✅ Generated task graph with {len(task_graph.nodes)} nodes")
        for node_id, node in task_graph.nodes.items():
            print(f"   {node_id}: {node.agent} - {node.action}")
        
        return True
        
    except Exception as e:
        print(f"❌ Controller test failed: {e}")
        return False

async def test_code_writer_with_real_api():
    """Test code writer agent with real GLM API"""
    print("\n💻 Testing Code Writer Agent with GLM API")
    print("=" * 50)
    
    glm_api_key = os.getenv("GLM_API_KEY", "")
    
    if not glm_api_key or glm_api_key == "your-glm-api-key-here":
        print("❌ GLM API key not configured")
        return False
    
    try:
        # Initialize code writer
        agent = CodeWriterAgent()
        
        # Test code generation
        print(f"\n📝 Testing code generation...")
        result = await agent.execute("write_file", {
            "description": "Create a simple Python function to calculate factorial",
            "language": "python",
            "filename": "factorial.py"
        })
        
        if result.get("status") == "completed":
            print("✅ Code generation successful")
            print(f"   Lines: {result.get('output', {}).get('lines', 0)}")
            print(f"   Size: {result.get('output', {}).get('size_bytes', 0)} bytes")
            
            # Show first few lines of generated code
            code = result.get('output', {}).get('code', '')
            if code:
                lines = code.split('\n')[:5]
                print("   Code preview:")
                for line in lines:
                    print(f"      {line}")
                if len(code.split('\n')) > 5:
                    print("      ...")
            
            return True
        else:
            print(f"❌ Code generation failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Code writer test failed: {e}")
        return False

async def test_web_search_with_real_api():
    """Test web search agent"""
    print("\n🔍 Testing Web Search Agent")
    print("=" * 50)
    
    try:
        # Initialize web search agent
        agent = WebSearchAgent()
        
        # Test web search
        print(f"\n🔍 Testing web search...")
        result = await agent.execute("search_web", {
            "query": "Python async programming best practices",
            "max_results": 5
        })
        
        if result.get("status") == "completed":
            results = result.get('output', {}).get('results', [])
            print(f"✅ Web search successful - Found {len(results)} results")
            
            # Show first result
            if results:
                first = results[0]
                print(f"   First result: {first.get('title', 'No title')}")
                print(f"   URL: {first.get('url', 'No URL')}")
                print(f"   Source: {first.get('source', 'Unknown')}")
            
            return True
        else:
            print(f"❌ Web search failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Web search test failed: {e}")
        return False

async def test_glm_api_directly():
    """Test GLM API connection directly"""
    print("\n🔌 Testing GLM API Connection")
    print("=" * 50)
    
    glm_api_key = os.getenv("GLM_API_KEY", "")
    
    if not glm_api_key or glm_api_key == "your-glm-api-key-here":
        print("❌ GLM API key not configured")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {glm_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "glm-4",
            "messages": [
                {
                    "role": "user",
                    "content": "Say 'Hello from GLM API!' in exactly those words."
                }
            ],
            "temperature": 0.1,
            "max_tokens": 50
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.glm.ai/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                print(f"✅ GLM API connection successful")
                print(f"   Response: {content}")
                return True
            else:
                print(f"❌ GLM API error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ GLM API test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 ZIEL-MAS Real Data Test Suite")
    print("=" * 50)
    print("This test verifies that you're getting real AI responses")
    print("instead of mock/sample data.\n")
    
    # Check environment
    glm_key = os.getenv("GLM_API_KEY", "")
    if not glm_key or glm_key == "your-glm-api-key-here":
        print("❌ GLM API key not configured!")
        print("\n🔧 To fix this:")
        print("   1. Run: python setup_api_keys.py")
        print("   2. Or edit .env file and add your GLM API key")
        print("   3. Get API key from: https://open.bigmodel.cn/")
        return
    
    print(f"✅ GLM API key found (length: {len(glm_key)})")
    
    # Run tests
    tests = [
        ("GLM API Connection", test_glm_api_directly),
        ("Controller Agent", test_controller_with_real_api),
        ("Code Writer Agent", test_code_writer_with_real_api),
        ("Web Search Agent", test_web_search_with_real_api),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! You're getting real AI data!")
        print("   Your ZIEL-MAS system is properly configured.")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed.")
        print("   Check the errors above and fix your configuration.")
    
    print("\n💡 Next steps:")
    print("   1. If all tests passed: Enjoy real AI-powered responses!")
    print("   2. If tests failed: Check your API key configuration")
    print("   3. Restart the server after making changes")

if __name__ == "__main__":
    asyncio.run(main())
