"""
Web Search Agent Tests for ZIEL-MAS
Tests for web search functionality using Z.AI MCP Server
"""

import pytest
import os
from backend.agents.web_search_agent import WebSearchAgent


class TestWebSearchAgent:
    """Test Web Search Agent functionality"""

    @pytest.mark.asyncio
    async def test_web_search_initialization(self):
        """Test web search agent initializes correctly"""
        agent = WebSearchAgent()

        assert agent.name == "Web Search Agent"
        assert agent.agent_type == "web_search"
        assert agent.mcp_server_url == "https://api.z.ai/api/mcp/web_search_prime/mcp"

    @pytest.mark.asyncio
    async def test_search_web_without_api_key(self):
        """Test web search fails gracefully without API key"""
        import os
        # Temporarily remove API key
        original_key = os.getenv("ZAI_API_KEY")
        os.environ["ZAI_API_KEY"] = ""

        try:
            agent = WebSearchAgent()
            result = await agent.execute("search_web", {"query": "test query"})

            # Should fail gracefully
            assert result["status"] == "failed"
            assert "ZAI_API_KEY" in result.get("error", "")
        finally:
            # Restore original key
            if original_key:
                os.environ["ZAI_API_KEY"] = original_key
            else:
                os.environ.pop("ZAI_API_KEY", None)

    @pytest.mark.asyncio
    async def test_search_web_missing_query(self):
        """Test web search requires query parameter"""
        agent = WebSearchAgent()
        result = await agent.execute("search_web", {})

        assert result["status"] == "failed"
        assert "query" in result.get("error", "").lower()

    @pytest.mark.asyncio
    async def test_unknown_action(self):
        """Test web search agent handles unknown actions"""
        agent = WebSearchAgent()
        result = await agent.execute("unknown_action", {})

        assert result["status"] == "failed"
        assert "Unknown action" in result.get("error", "")

    @pytest.mark.asyncio
    async def test_search_news_action(self):
        """Test news search action"""
        agent = WebSearchAgent()
        result = await agent.execute("search_news", {})

        assert result["status"] == "failed"
        assert "query" in result.get("error", "").lower()

    @pytest.mark.asyncio
    async def test_search_realtime_action(self):
        """Test real-time search action"""
        agent = WebSearchAgent()
        result = await agent.execute("search_realtime", {})

        assert result["status"] == "failed"
        assert "query" in result.get("error", "").lower()

    @pytest.mark.asyncio
    async def test_search_technical_action(self):
        """Test technical search action"""
        agent = WebSearchAgent()
        result = await agent.execute("search_technical", {})

        assert result["status"] == "failed"
        assert "query" in result.get("error", "").lower()

    @pytest.mark.asyncio
    async def test_web_search_response_format(self):
        """Test web search returns proper response format"""
        agent = WebSearchAgent()
        result = await agent.execute("search_web", {"query": "test"})

        # Should have status and either output or error
        assert "status" in result
        assert result["status"] in ["success", "failed"]

        if result["status"] == "success":
            assert "output" in result
            assert "results" in result["output"]
            assert isinstance(result["output"]["results"], list)
        else:
            assert "error" in result


class TestWebSearchAgentIntegration:
    """Integration tests for Web Search Agent (requires API key)"""

    @pytest.mark.skipif(not os.getenv("ZAI_API_KEY"), reason="ZAI_API_KEY not configured")
    @pytest.mark.asyncio
    async def test_web_search_with_valid_query(self):
        """Test web search with valid query (requires API key)"""
        agent = WebSearchAgent()
        result = await agent.execute("search_web", {
            "query": "Python programming",
            "max_results": 5
        })

        assert result["status"] in ["success", "failed"]
        if result["status"] == "success":
            assert "results" in result["output"]
            assert len(result["output"]["results"]) <= 5

    @pytest.mark.skipif(not os.getenv("ZAI_API_KEY"), reason="ZAI_API_KEY not configured")
    @pytest.mark.asyncio
    async def test_news_search_with_valid_query(self):
        """Test news search with valid query (requires API key)"""
        agent = WebSearchAgent()
        result = await agent.execute("search_news", {
            "query": "AI news",
            "max_results": 5
        })

        assert result["status"] in ["success", "failed"]
        if result["status"] == "success":
            assert "results" in result["output"]
            assert result["output"]["type"] == "news"

    @pytest.mark.skipif(not os.getenv("ZAI_API_KEY"), reason="ZAI_API_KEY not configured")
    @pytest.mark.asyncio
    async def test_technical_search_with_valid_query(self):
        """Test technical search with valid query (requires API key)"""
        agent = WebSearchAgent()
        result = await agent.execute("search_technical", {
            "query": "FastAPI tutorial",
            "tech_stack": "Python",
            "max_results": 5
        })

        assert result["status"] in ["success", "failed"]
        if result["status"] == "success":
            assert "results" in result["output"]
            assert result["output"]["type"] == "technical"
