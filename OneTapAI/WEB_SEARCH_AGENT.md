# Web Search Agent Documentation

## Overview

The **Web Search Agent** is a new addition to the ZIEL-MAS system that provides powerful web search capabilities using the Z.AI Web Search MCP Server. It enables the system to retrieve real-time information from the web, making it possible to answer questions about current events, news, technical documentation, and more.

## Features

### 🔍 **Search Capabilities**

1. **General Web Search** (`search_web`)
   - Search the web for any topic
   - Retrieve page titles, URLs, summaries, and metadata
   - Configurable result limits

2. **News Search** (`search_news`)
   - Find recent news articles
   - Real-time news retrieval
   - Focus on current events and trends

3. **Real-time Information** (`search_realtime`)
   - Stock prices, weather, and other live data
   - Time-sensitive information retrieval
   - Current date/time specific searches

4. **Technical Documentation** (`search_technical`)
   - Programming tutorials and guides
   - Technical documentation search
   - Stack Overflow, GitHub, and developer resources

## Configuration

### Prerequisites

1. **Get Z.AI API Key**
   ```
   Visit: https://z.ai/manage-apikey/apikey-list
   Sign up for GLM Coding Plan
   Generate your API key
   ```

2. **Configure Environment Variables**
   ```bash
   # Add to backend/.env
   ZAI_API_KEY=your_actual_zai_api_key_here
   ```

3. **Restart the Backend Server**
   ```bash
   pkill -f uvicorn
   nohup ./venv312/bin/python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 > /tmp/backend_server.log 2>&1 &
   ```

## Usage

### Via Task Execution

The web search agent can be used through the task execution system:

```python
# Example 1: General web search
task = TaskNode(
    agent=AgentType.WEB_SEARCH,
    action="search_web",
    parameters={
        "query": "latest AI developments 2024",
        "max_results": 10
    }
)

# Example 2: News search
task = TaskNode(
    agent=AgentType.WEB_SEARCH,
    action="search_news",
    parameters={
        "query": "technology news",
        "max_results": 5
    }
)

# Example 3: Technical documentation search
task = TaskNode(
    agent=AgentType.WEB_SEARCH,
    action="search_technical",
    parameters={
        "query": "FastAPI async tutorial",
        "tech_stack": "Python",
        "max_results": 8
    }
)
```

### Via API

```bash
curl -X POST http://localhost:8000/api/v1/create-task \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "Search for the latest AI news",
    "priority": "medium",
    "user_id": "user_123"
  }'
```

### Direct Testing

```bash
# Test the web search agent directly
python test_web_search.py
```

## Agent Actions

### `search_web`
**Description:** Perform general web search

**Parameters:**
- `query` (required): Search query string
- `max_results` (optional): Maximum number of results (default: 10)

**Returns:**
```json
{
  "status": "success",
  "output": {
    "query": "Python programming",
    "results": [
      {
        "title": "Python Programming Official Website",
        "url": "https://www.python.org",
        "snippet": "Official Python documentation...",
        "site_name": "python.org",
        "published_date": "2024-01-15"
      }
    ],
    "total_results": 10
  }
}
```

### `search_news`
**Description:** Search for recent news articles

**Parameters:**
- `query` (required): News topic
- `max_results` (optional): Maximum results (default: 10)

**Returns:** News articles with publication dates and sources

### `search_realtime`
**Description:** Search for real-time information

**Parameters:**
- `query` (required): Search query
- `info_type` (optional): Information type (default: "general")

**Returns:** Current data including timestamps and sources

### `search_technical`
**Description:** Search for technical documentation

**Parameters:**
- `query` (required): Technical topic
- `tech_stack` (optional): Technology stack (e.g., "Python", "JavaScript")
- `max_results` (optional): Maximum results (default: 10)

**Returns:** Technical docs, tutorials, and guides

## Integration with Task Graphs

The web search agent can be part of complex task graphs:

```python
# Task 1: Search for information
search_task = TaskNode(
    agent=AgentType.WEB_SEARCH,
    action="search_web",
    parameters={"query": "Python async best practices"}
)

# Task 2: Process the search results
process_task = TaskNode(
    agent=AgentType.DATA,
    action="aggregate_data",
    parameters={"data": search_task.output}
)

# Task 3: Create summary
summary_task = TaskNode(
    agent=AgentType.CONTROLLER,
    action="create_summary",
    parameters={"search_results": process_task.output}
)
```

## Error Handling

The web search agent handles various error conditions:

### Missing API Key
```json
{
  "status": "failed",
  "error": "ZAI_API_KEY not configured. Please set ZAI_API_KEY environment variable."
}
```

### Invalid Query
```json
{
  "status": "failed",
  "error": "Search query is required"
}
```

### MCP Server Connection Issues
```json
{
  "status": "failed",
  "error": "Failed to connect to MCP server: Connection timeout"
}
```

## Testing

### Unit Tests
```bash
# Run web search agent tests
./venv312/bin/python -m pytest backend/tests/test_web_search_agent.py -v
```

### Integration Test
```bash
# Test with actual API key
ZAI_API_KEY=your_key ./venv312/bin/python test_web_search.py
```

## Quotas and Limits

According to your GLM Coding Plan:

- **Lite Plan**: 100 web searches total
- **Pro Plan**: 1,000 web searches total
- **Max Plan**: 4,000 web searches total

## Troubleshooting

### Common Issues

1. **"ZAI_API_KEY not configured"**
   - Ensure you've added the API key to `backend/.env`
   - Restart the backend server after adding the key
   - Verify the key format: `ZAI_API_KEY=your_key_here`

2. **"Failed to connect to MCP server"**
   - Check your internet connection
   - Verify the API key is valid and activated
   - Ensure you have sufficient quota
   - Check firewall settings

3. **Empty search results**
   - Try different search terms
   - Check if search query is too specific
   - Verify network connectivity

## Architecture

```
User Intent
    ↓
Controller Agent (plans task)
    ↓
Task Graph (DAG)
    ↓
Web Search Agent (executes search)
    ↓
Z.AI MCP Server (webSearchPrime)
    ↓
Search Results (formatted)
    ↓
Data Agent (processes results)
    ↓
Final Output
```

## Future Enhancements

Potential improvements to the web search agent:

1. **Search result caching** - Store frequently searched queries
2. **Advanced filtering** - Filter by date, source, language
3. **Search history** - Track search queries for analytics
4. **Batch searches** - Multiple concurrent searches
5. **Custom result ranking** - Relevance scoring and ranking

## Support

For issues with:
- **API Key**: https://z.ai/manage-apikey/apikey-list
- **MCP Protocol**: https://modelcontextprotocol.io/
- **Z.AI Support**: Contact through Z.AI console

---

**Created:** 2026-04-05
**Version:** 1.0.0
**Agent Type:** WEB_SEARCH
**MCP Server:** Z.AI Web Search Prime
