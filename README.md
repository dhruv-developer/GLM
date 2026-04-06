# OneTapAI: Zero-Interaction Execution Links with Multi-Agent System

## Overview
OneTapAI converts natural language intent into executable, secure links that autonomously execute complex tasks through distributed multi-agent architecture.

## Tech Stack
- **Backend**: FastAPI (Python)
- **Frontend**: Next.js (React)
- **Databases**: MongoDB (persistent), Redis (cache/state)
- **LLM**: GLM 5.1
- **Automation**: Playwright
- **Security**: JWT, AES encryption

## Architecture
```
User Intent → Controller Agent → Task DAG → Secure Link → Multi-Agent Execution → Result
```

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints
- `POST /api/v1/create-task` - Create task from intent
- `GET /api/v1/execute/{token}` - Execute task via secure link
- `GET /api/v1/status/{task_id}` - Get execution status

## Components

### Controller Agent
- Parses natural language intent
- Generates task DAGs
- Orchestrates multi-agent execution

### Worker Agents
- **API Agent**: Executes API calls
- **Web Automation Agent**: Browser automation
- **Communication Agent**: Email/WhatsApp messaging
- **Data Agent**: Data fetching and processing
- **Scheduler Agent**: Delayed/recurring tasks
- **Validation Agent**: Output verification

## Security
- Encrypted tokens (AES/JWT)
- Permission scoping
- API whitelisting
- Full audit logging

## License
MIT
