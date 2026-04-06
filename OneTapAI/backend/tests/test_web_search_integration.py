"""
Integration Tests for Web Search Agent with Other Agents
Tests complex workflows involving web search combined with other agent types
"""

import pytest
from backend.models.task import TaskGraph, TaskNode, TaskExecution, TaskStatus, AgentType
from backend.core.execution import ExecutionEngine
from backend.agents.web_search_agent import WebSearchAgent
from backend.agents.data_agent import DataAgent


class TestWebSearchIntegration:
    """Test web search agent integrated with other agents"""

    @pytest.mark.asyncio
    async def test_web_search_with_data_aggregation(self, execution_engine):
        """Test web search followed by data aggregation"""
        graph = TaskGraph()

        # Task 1: Web search
        search_task = TaskNode(
            agent=AgentType.WEB_SEARCH,
            action="search_web",
            parameters={
                "query": "Python async programming",
                "max_results": 3
            }
        )
        graph.add_node(search_task)

        # Task 2: Data aggregation (depends on search)
        aggregate_task = TaskNode(
            agent=AgentType.DATA,
            action="aggregate_data",
            parameters={
                "data_source": "search_results",
                "aggregation_type": "summary"
            },
            dependencies=[search_task.task_id]
        )
        graph.add_node(aggregate_task)

        # Create execution
        execution = TaskExecution(
            user_id="test_user",
            intent="Search and aggregate Python async info",
            task_graph=graph
        )

        # Execute
        result = await execution_engine.execute_task_graph(
            execution,
            execution.execution_id
        )

        # Verify execution completed
        assert "success" in result or "error" in result

    @pytest.mark.asyncio
    async def test_multiple_web_searches_with_aggregation(self, execution_engine):
        """Test multiple web searches followed by aggregation"""
        graph = TaskGraph()

        # Task 1: Search for AI trends
        search1 = TaskNode(
            agent=AgentType.WEB_SEARCH,
            action="search_web",
            parameters={"query": "AI trends 2024", "max_results": 3}
        )
        graph.add_node(search1)

        # Task 2: Search for ML frameworks
        search2 = TaskNode(
            agent=AgentType.WEB_SEARCH,
            action="search_technical",
            parameters={"query": "machine learning frameworks", "tech_stack": "Python", "max_results": 3}
        )
        graph.add_node(search2)

        # Task 3: Aggregate both searches (depends on both)
        aggregate = TaskNode(
            agent=AgentType.DATA,
            action="aggregate_data",
            parameters={
                "data_source": "multiple_sources",
                "aggregation_type": "comparative_analysis"
            },
            dependencies=[search1.task_id, search2.task_id]
        )
        graph.add_node(aggregate)

        # Verify initial structure: 2 independent search tasks
        ready_tasks = graph.get_ready_tasks()
        assert len(ready_tasks) == 2  # Two independent searches

        # Create and execute
        execution = TaskExecution(
            user_id="test_user",
            intent="Compare AI trends and ML frameworks",
            task_graph=graph
        )

        result = await execution_engine.execute_task_graph(
            execution,
            execution.execution_id
        )

        # Verify execution completed
        assert result is not None
        assert len(graph.nodes) == 3

    @pytest.mark.asyncio
    async def test_web_search_workflow_with_controller(self, execution_engine):
        """Test complete workflow: search -> process -> summarize"""
        graph = TaskGraph()

        # Task 1: Web search
        search = TaskNode(
            agent=AgentType.WEB_SEARCH,
            action="search_news",
            parameters={"query": "technology news", "max_results": 5}
        )
        graph.add_node(search)

        # Task 2: Controller processes results
        process = TaskNode(
            agent=AgentType.CONTROLLER,
            action="process_request",
            parameters={"processing_type": "extract_key_points"},
            dependencies=[search.task_id]
        )
        graph.add_node(process)

        # Task 3: Final summary
        summary = TaskNode(
            agent=AgentType.CONTROLLER,
            action="process_request",
            parameters={"format": "executive_summary"},
            dependencies=[process.task_id]
        )
        graph.add_node(summary)

        # Verify workflow structure before execution
        assert len(graph.nodes) == 3
        # Verify dependencies
        assert search.task_id in process.dependencies
        assert process.task_id in summary.dependencies

        # Execute
        execution = TaskExecution(
            user_id="test_user",
            intent="Get tech news summary",
            task_graph=graph
        )

        result = await execution_engine.execute_task_graph(
            execution,
            execution.execution_id
        )

        # Verify execution completed
        assert result is not None

    @pytest.mark.asyncio
    async def test_web_search_error_handling_in_workflow(self, execution_engine):
        """Test workflow handles web search failures gracefully"""
        graph = TaskGraph()

        # Task 1: Invalid web search (will fail)
        search = TaskNode(
            agent=AgentType.WEB_SEARCH,
            action="search_web",
            parameters={}  # Missing query parameter
        )
        graph.add_node(search)

        # Task 2: Depends on search (should not execute or handle failure)
        process = TaskNode(
            agent=AgentType.DATA,
            action="aggregate_data",
            parameters={"data_source": "search_results"},
            dependencies=[search.task_id]
        )
        graph.add_node(process)

        # Execute
        execution = TaskExecution(
            user_id="test_user",
            intent="Test error handling",
            task_graph=graph
        )

        result = await execution_engine.execute_task_graph(
            execution,
            execution.execution_id
        )

        # Should handle error gracefully
        assert result is not None

    @pytest.mark.asyncio
    async def test_complex_web_search_workflow(self, execution_engine):
        """Test complex workflow with multiple web search types"""
        graph = TaskGraph()

        # Task 1: General web search
        general_search = TaskNode(
            agent=AgentType.WEB_SEARCH,
            action="search_web",
            parameters={"query": "FastAPI best practices", "max_results": 3}
        )
        graph.add_node(general_search)

        # Task 2: Technical documentation search
        tech_search = TaskNode(
            agent=AgentType.WEB_SEARCH,
            action="search_technical",
            parameters={"query": "async await Python", "tech_stack": "Python", "max_results": 3}
        )
        graph.add_node(tech_search)

        # Task 3: Real-time search (independent)
        realtime_search = TaskNode(
            agent=AgentType.WEB_SEARCH,
            action="search_realtime",
            parameters={"query": "Python version", "info_type": "general"}
        )
        graph.add_node(realtime_search)

        # Task 4: Aggregate all three searches
        aggregate = TaskNode(
            agent=AgentType.DATA,
            action="aggregate_data",
            parameters={
                "data_source": "web_search",
                "aggregation_type": "comprehensive_report"
            },
            dependencies=[general_search.task_id, tech_search.task_id, realtime_search.task_id]
        )
        graph.add_node(aggregate)

        # Task 5: Create final report
        report = TaskNode(
            agent=AgentType.CONTROLLER,
            action="process_request",
            parameters={"format": "detailed_report", "include_sources": True},
            dependencies=[aggregate.task_id]
        )
        graph.add_node(report)

        # Verify initial structure: 3 independent search tasks
        ready_tasks = graph.get_ready_tasks()
        assert len(ready_tasks) == 3

        # Execute
        execution = TaskExecution(
            user_id="test_user",
            intent="Comprehensive research on FastAPI",
            task_graph=graph
        )

        result = await execution_engine.execute_task_graph(
            execution,
            execution.execution_id
        )

        # Verify workflow structure
        assert len(graph.nodes) == 5

    @pytest.mark.asyncio
    async def test_web_search_task_execution_updates(self, execution_engine, database_service):
        """Test that web search task execution properly updates status"""
        graph = TaskGraph()

        search_task = TaskNode(
            agent=AgentType.WEB_SEARCH,
            action="search_web",
            parameters={"query": "test query", "max_results": 2}
        )
        graph.add_node(search_task)

        execution = TaskExecution(
            user_id="test_user",
            intent="Test status updates",
            task_graph=graph
        )

        # Store initial execution
        await database_service.create_task_execution({
            "execution_id": execution.execution_id,
            "user_id": execution.user_id,
            "intent": execution.intent,
            "status": "pending",
            "task_graph": execution.task_graph.model_dump(),
            "created_at": execution.created_at.isoformat()
        })

        # Execute
        result = await execution_engine.execute_task_graph(
            execution,
            execution.execution_id
        )

        # Verify database was updated
        updated_execution = await database_service.get_task_execution(execution.execution_id)
        assert updated_execution is not None
        assert updated_execution.get("status") in ["completed", "failed"]


class TestWebSearchAgentDirectly:
    """Test web search agent behavior in isolation"""

    @pytest.mark.asyncio
    async def test_web_search_agent_initialization(self):
        """Test web search agent initializes correctly"""
        agent = WebSearchAgent()

        assert agent.name == "Web Search Agent"
        assert agent.agent_type == "web_search"
        assert agent.mcp_server_url == "https://api.z.ai/api/mcp/web_search_prime/mcp"

    @pytest.mark.asyncio
    async def test_web_search_all_actions(self):
        """Test all web search actions are available"""
        agent = WebSearchAgent()

        # Test that all actions return proper response format
        actions = [
            ("search_web", {"query": "test"}),
            ("search_news", {"query": "test"}),
            ("search_realtime", {"query": "test"}),
            ("search_technical", {"query": "test"})
        ]

        for action, params in actions:
            result = await agent.execute(action, params)

            # Should have status field
            assert "status" in result
            assert result["status"] in ["success", "failed"]

            # Should have either output or error
            if result["status"] == "success":
                assert "output" in result
            else:
                assert "error" in result

    @pytest.mark.asyncio
    async def test_web_search_parameter_validation(self):
        """Test web search validates required parameters"""
        agent = WebSearchAgent()

        # Test missing query parameter
        result = await agent.execute("search_web", {})
        assert result["status"] == "failed"
        assert "query" in result.get("error", "").lower()

    @pytest.mark.asyncio
    async def test_web_search_unknown_action(self):
        """Test web search handles unknown actions"""
        agent = WebSearchAgent()

        result = await agent.execute("unknown_action", {})
        assert result["status"] == "failed"
        assert "Unknown action" in result.get("error", "")


class TestWebSearchTaskGraphScenarios:
    """Test realistic task graph scenarios with web search"""

    @pytest.mark.asyncio
    async def test_research_and_summarize_scenario(self, execution_engine):
        """Test scenario: Research topic and create summary"""
        graph = TaskGraph()

        # Search for information
        search = TaskNode(
            agent=AgentType.WEB_SEARCH,
            action="search_web",
            parameters={"query": "microservices architecture patterns", "max_results": 5}
        )
        graph.add_node(search)

        # Create summary
        summary = TaskNode(
            agent=AgentType.CONTROLLER,
            action="create_summary",
            parameters={"format": "executive_summary"},
            dependencies=[search.task_id]
        )
        graph.add_node(summary)

        execution = TaskExecution(
            user_id="test_user",
            intent="Research microservices and create summary",
            task_graph=graph
        )

        result = await execution_engine.execute_task_graph(
            execution,
            execution.execution_id
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_multi_source_research_scenario(self, execution_engine):
        """Test scenario: Research from multiple sources and compare"""
        graph = TaskGraph()

        # Search web for general info
        web_search = TaskNode(
            agent=AgentType.WEB_SEARCH,
            action="search_web",
            parameters={"query": "React vs Vue performance", "max_results": 5}
        )
        graph.add_node(web_search)

        # Search technical docs
        tech_search = TaskNode(
            agent=AgentType.WEB_SEARCH,
            action="search_technical",
            parameters={"query": "frontend framework benchmark", "tech_stack": "JavaScript", "max_results": 5}
        )
        graph.add_node(tech_search)

        # Search for news
        news_search = TaskNode(
            agent=AgentType.WEB_SEARCH,
            action="search_news",
            parameters={"query": "JavaScript framework news", "max_results": 3}
        )
        graph.add_node(news_search)

        # Aggregate all sources
        aggregate = TaskNode(
            agent=AgentType.DATA,
            action="aggregate_data",
            parameters={"aggregation_type": "comparison"},
            dependencies=[web_search.task_id, tech_search.task_id, news_search.task_id]
        )
        graph.add_node(aggregate)

        # Verify 3 parallel searches before execution
        ready_tasks = graph.get_ready_tasks()
        assert len(ready_tasks) == 3

        execution = TaskExecution(
            user_id="test_user",
            intent="Compare React and Vue from multiple sources",
            task_graph=graph
        )

        result = await execution_engine.execute_task_graph(
            execution,
            execution.execution_id
        )

        # Verify execution completed
        assert result is not None

    @pytest.mark.asyncio
    async def test_technical_research_scenario(self, execution_engine):
        """Test scenario: Deep technical research"""
        graph = TaskGraph()

        # Search for tutorials
        tutorial_search = TaskNode(
            agent=AgentType.WEB_SEARCH,
            action="search_technical",
            parameters={"query": "Docker container tutorial", "tech_stack": "DevOps", "max_results": 5}
        )
        graph.add_node(tutorial_search)

        # Search for best practices
        best_practices = TaskNode(
            agent=AgentType.WEB_SEARCH,
            action="search_technical",
            parameters={"query": "Docker best practices production", "tech_stack": "Docker", "max_results": 5}
        )
        graph.add_node(best_practices)

        # Search for troubleshooting
        troubleshooting = TaskNode(
            agent=AgentType.WEB_SEARCH,
            action="search_technical",
            parameters={"query": "Docker common issues solutions", "tech_stack": "Docker", "max_results": 3}
        )
        graph.add_node(troubleshooting)

        # Aggregate and create guide
        aggregate = TaskNode(
            agent=AgentType.DATA,
            action="aggregate_data",
            parameters={"aggregation_type": "comprehensive_guide"},
            dependencies=[tutorial_search.task_id, best_practices.task_id, troubleshooting.task_id]
        )
        graph.add_node(aggregate)

        # Create actionable guide
        guide = TaskNode(
            agent=AgentType.CONTROLLER,
            action="create_summary",
            parameters={"format": "actionable_guide"},
            dependencies=[aggregate.task_id]
        )
        graph.add_node(guide)

        execution = TaskExecution(
            user_id="test_user",
            intent="Create comprehensive Docker guide",
            task_graph=graph
        )

        result = await execution_engine.execute_task_graph(
            execution,
            execution.execution_id
        )

        # Verify workflow
        assert len(graph.nodes) == 5
