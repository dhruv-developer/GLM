# ZIEL-MAS Quick Start Guide

## Overview
ZIEL-MAS (Zero-Interaction Execution Links with Multi-Agent System) converts natural language intent into autonomous, executable workflows.

## Prerequisites

- Python 3.9+
- Node.js 18+
- MongoDB
- Redis
- GLM API Key

## Installation

### 1. Clone and Setup

```bash
# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 2. Configure Environment

```bash
# Copy example .env
cp .env.example .env

# Edit .env with your configuration
nano .env
```

**Required Environment Variables:**
- `GLM_API_KEY` - Your GLM API key
- `JWT_SECRET` - Secret for JWT tokens
- `ENCRYPTION_KEY` - 32-byte encryption key
- `MONGODB_URI` - MongoDB connection string
- `REDIS_URI` - Redis connection string

### 3. Start Services

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start MongoDB
mongod

# Terminal 3: Start Backend
python backend/main.py

# Terminal 4: Start Frontend
cd frontend
npm run dev
```

## Usage

### Web Interface

1. Open http://localhost:3000
2. Enter your task in natural language
3. Click "Create Task"
4. Copy the execution link
5. Share the link or click to execute

### API Usage

```bash
# Create a task
curl -X POST http://localhost:8000/api/v1/create-task \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "Send birthday message to mom at 12 AM",
    "priority": "medium"
  }'

# Execute task (use the token from response)
curl http://localhost:8000/api/v1/execute/{token}

# Check status
curl http://localhost:8000/api/v1/status/{execution_id}
```

## Example Intents

- "Send birthday message to my mother at 12 AM"
- "Book an Uber to the airport at 3 PM"
- "Find top 5 Italian restaurants nearby"
- "Apply for Software Engineer position at Google"

## Demo Workflows

```bash
# Run demo workflows
python tests/demo_workflows.py
```

## Architecture

```
User Intent → Controller Agent → Task Graph → Secure Link → Multi-Agent Execution → Result
```

### Components

- **Controller Agent**: Parses intent and generates task DAGs
- **Worker Agents**: Execute specific tasks (API, Web, Communication, Data, Scheduler, Validation)
- **Execution Engine**: Orchestrates multi-agent execution
- **Security Layer**: Token-based authentication and permission scoping

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_controller.py

# Run with coverage
pytest --cov=backend tests/
```

## Troubleshooting

### Backend won't start
- Check MongoDB and Redis are running
- Verify .env configuration
- Check logs in `logs/ziel_mas.log`

### Tasks failing
- Verify API keys in .env
- Check agent permissions
- Review execution logs via API

### Frontend connection issues
- Ensure backend is running on port 8000
- Check CORS settings in .env
- Verify API_URL in frontend/.env.local

## Development

### Backend Development
```bash
# Run with auto-reload
uvicorn backend.api.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
```

## Production Deployment

1. Update .env with production values
2. Set `DEBUG=False`
3. Use production-grade MongoDB and Redis
4. Enable HTTPS
5. Set up monitoring and logging
6. Configure rate limiting
7. Set up backups

## License
MIT

## Support
For issues and questions, please open an issue on GitHub.
