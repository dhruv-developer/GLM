"""
Test script for Web Search Agent functionality
Demonstrates web search capabilities using Z.AI MCP Server
"""

import asyncio
import sys
import os

# Add path to imports
sys.path.insert(0, '/Users/dhruvdawar11/Desktop/Projects/GLM-Hack/t1')

from backend.agents.web_search_agent import WebSearchAgent


async def test_web_search():
    """Test web search functionality"""
    print("🔍 Testing Web Search Agent")
    print("=" * 50)

    # Check if API key is configured
    api_key = os.getenv("ZAI_API_KEY")
    if not api_key or api_key == "your-zai-api-key-here":
        print("⚠️  ZAI_API_KEY not configured!")
        print("To use the Web Search Agent:")
        print("1. Get your API key from: https://z.ai/manage-apikey/apikey-list")
        print("2. Add to backend/.env: ZAI_API_KEY=your_actual_api_key")
        print("3. Restart the server")
        print("\nFor now, testing error handling...")

        # Test without API key
        agent = WebSearchAgent()
        result = await agent.execute("search_web", {"query": "Python programming"})

        print(f"\n❌ Web Search Result (without API key):")
        print(f"   Status: {result.get('status')}")
        print(f"   Error: {result.get('error')}")

        # Test error handling
        result2 = await agent.execute("search_web", {})
        print(f"\n❌ Missing Query Test:")
        print(f"   Status: {result2.get('status')}")
        print(f"   Error: {result2.get('error')}")

        return

    print("✅ ZAI_API_KEY configured!")
    print("Testing web search functionality...")

    agent = WebSearchAgent()

    # Test 1: General web search
    print("\n1️⃣  Testing General Web Search...")
    result = await agent.execute("search_web", {
        "query": "latest AI developments 2024",
        "max_results": 3
    })

    print(f"   Status: {result.get('status')}")
    if result.get('status') == 'success':
        print(f"   Found {result['output']['total_results']} results")
        for i, item in enumerate(result['output']['results'][:2]):
            print(f"   {i+1}. {item.get('title', 'N/A')}")
            print(f"      URL: {item.get('url', 'N/A')}")

    # Test 2: News search
    print("\n2️⃣  Testing News Search...")
    result = await agent.execute("search_news", {
        "query": "technology",
        "max_results": 2
    })

    print(f"   Status: {result.get('status')}")
    if result.get('status') == 'success':
        print(f"   Found {result['output']['total_results']} news articles")

    # Test 3: Technical search
    print("\n3️⃣  Testing Technical Documentation Search...")
    result = await agent.execute("search_technical", {
        "query": "REST API design",
        "tech_stack": "Python",
        "max_results": 2
    })

    print(f"   Status: {result.get('status')}")
    if result.get('status') == 'success':
        print(f"   Found {result['output']['total_results']} technical docs")

    print("\n✅ Web Search Agent tests completed!")


if __name__ == "__main__":
    asyncio.run(test_web_search())
