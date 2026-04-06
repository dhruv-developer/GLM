# ZIEL-MAS Architecture

## System Overview

ZIEL-MAS is a distributed multi-agent system that converts natural language intent into executable, secure links. The system uses a controller-worker architecture optimized for long-horizon reasoning and real-world task completion.

## Core Concepts

### Executable Intent Artifacts
Each generated link represents:
- A compiled task graph (DAG)
- Agent assignments
- Execution constraints
- Security-scoped permissions

### Zero-Interface Computing
- Traditional: User → UI → API → Result
- ZIEL-MAS: User Intent → Controller → DAG → Link → Autonomous Execution → Result

## Architecture Diagram

```
┌─────────────┐
│   User      │
│  (Intent)   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│     Intent Processing Layer     │
│  - Natural Language Parsing     │
│  - Entity Extraction            │
│  - Task Type Detection          │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│      Controller Agent           │
│  (GLM 5.1 Powered Brain)        │
│  - Task Decomposition           │
│  - DAG Generation               │
│  - Agent Assignment             │
│  - Re-planning Logic            │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│       Task Graph (DAG)          │
│  - Nodes: Individual Tasks      │
│  - Edges: Dependencies          │
│  - Parallel Execution Paths     │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│    Link Generator (Secure)      │
│  - JWT Token Creation           │
│  - Permission Scoping           │
│  - Encryption                   │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│    Execution Link               │
│  /execute/{encrypted_token}     │
└──────┬──────────────────────────┘
       │
       ▼ (User activates link)
┌─────────────────────────────────┐
│     Execution Engine            │
│  - DAG Traversal                │
│  - Dependency Resolution        │
│  - Parallel Execution           │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│     Task Dispatcher             │
│  - Agent Selection              │
│  - Queue Management             │
│  - Load Balancing               │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│    Worker Agents Pool           │
│  ┌────────────┬────────────┐   │
│  │ API Agent  │   Web Auto │   │
│  ├────────────┼────────────┤   │
│  │ Comm Agent │  Data Agent│   │
│  ├────────────┼────────────┤   │
│  │Scheduler   │Validation  │   │
│  └────────────┴────────────┘   │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│    Result Aggregator            │
│  - Collect Outputs              │
│  - Error Handling               │
│  - Final Response               │
└─────────────────────────────────┘
```

## Component Details

### 1. Controller Agent
**Purpose**: Central orchestrator and planner

**Responsibilities**:
- Parse natural language intent
- Decompose tasks into sub-tasks
- Generate task DAGs
- Assign agents to tasks
- Monitor execution
- Handle failures and re-planning

**Technology**: GLM 5.1 LLM

### 2. Worker Agents

#### API Agent
- Executes HTTP requests
- Handles rate limiting
- API whitelisting
- Retry logic

#### Web Automation Agent
- Browser automation (Playwright)
- Form filling
- Navigation
- Screenshot capture

#### Communication Agent
- Email sending (SMTP)
- WhatsApp messages (Twilio)
- SMS sending
- Template management

#### Data Agent
- Data fetching (APIs, databases)
- Filtering and transformation
- Ranking and scoring
- Aggregation

#### Scheduler Agent
- One-time scheduling
- Recurring tasks (cron)
- Delayed execution
- Queue management

#### Validation Agent
- Output verification
- Schema validation
- Sanity checks
- Delivery confirmation

### 3. Execution Engine

**Core Algorithm**:
```python
while tasks_remaining:
    ready_tasks = get_tasks_with_satisfied_deps()
    for task in ready_tasks:
        dispatch_to_agent(task)
    wait_for_completion()
    update_state()
```

**Features**:
- Parallel execution
- Dependency resolution
- State management
- Progress tracking

### 4. Security Layer

**Components**:
- JWT Token Generation
- AES Encryption
- Permission Scoping
- API Whitelisting
- Audit Logging

**Token Structure**:
```json
{
  "execution_id": "uuid",
  "user_id": "uuid",
  "type": "execution",
  "iat": timestamp,
  "exp": timestamp,
  "allowed_actions": ["execute"],
  "jti": "unique_token_id"
}
```

### 5. Data Management

**Redis** (Fast State):
- Task status tracking
- Progress monitoring
- Agent state
- Queue management
- Token lookup

**MongoDB** (Persistent):
- Task executions
- Execution logs
- Agent history
- Audit trails
- User data

## Task Graph Structure

### Example DAG
```json
{
  "graph_id": "uuid",
  "nodes": {
    "t1": {
      "task_id": "t1",
      "agent": "controller",
      "action": "prepare_message",
      "dependencies": [],
      "status": "completed"
    },
    "t2": {
      "task_id": "t2",
      "agent": "scheduler",
      "action": "schedule_task",
      "dependencies": ["t1"],
      "status": "pending"
    },
    "t3": {
      "task_id": "t3",
      "agent": "communication",
      "action": "send_message",
      "dependencies": ["t2"],
      "status": "pending"
    }
  },
  "edges": [
    {"from": "t1", "to": "t2"},
    {"from": "t2", "to": "t3"}
  ],
  "parallel_execution": false
}
```

## Execution Flow

### Phase 1: Intent Processing
1. User submits natural language
2. Controller parses and structures intent
3. Extracts entities, time, priority

### Phase 2: Planning
1. DAG created from parsed intent
2. Agents assigned to tasks
3. Execution strategy defined
4. Dependencies established

### Phase 3: Link Generation
1. Plan serialized
2. Token generated (JWT)
3. Encrypted payload
4. Stored securely

### Phase 4: Execution Trigger
1. User clicks link
2. Token validated
3. Execution engine starts
4. Task dispatcher activated

### Phase 5: Distributed Execution
1. Ready tasks identified
2. Dispatched to agents
3. Agents execute independently
4. Controller monitors progress

### Phase 6: Completion
1. Results aggregated
2. Response returned
3. Audit log updated
4. User notified

## Failure Handling

### Strategies
1. **Exponential Backoff**: 2^retry_count seconds
2. **Alternative Agents**: Switch to different agent type
3. **Partial Re-execution**: Re-run only failed branches
4. **Circuit Breaker**: Prevent cascading failures

### Retry Logic
```python
if retry_count < max_retries:
    if error_type == "timeout":
        strategy = "exponential_backoff"
    elif error_type == "auth":
        strategy = "alternative_agent"
    else:
        strategy = "exponential_backoff"
```

## Scalability

### Horizontal Scaling
- Multiple execution nodes
- Shared Redis/MongoDB
- Load balancer distribution

### Queue-Based
- Redis queues for tasks
- Worker pools per agent type
- Priority queue support

### Stateless Execution
- Execution nodes are stateless
- State in Redis/MongoDB
- Easy horizontal scaling

## Security Model

### Token Security
- AES-256 encryption
- JWT with expiration
- Single-use tokens
- Scope-limited permissions

### API Whitelisting
- Pre-approved domains
- URL validation
- Request signing

### Audit Trail
- Full execution log
- Agent actions
- User activities
- Security events

## Performance Optimizations

1. **Parallel Execution**: Independent tasks run concurrently
2. **Caching**: Redis for frequently accessed data
3. **Connection Pooling**: Reuse database connections
4. **Async I/O**: Non-blocking operations
5. **Lazy Loading**: Load data on demand

## Monitoring & Observability

### Metrics
- Task execution time
- Agent performance
- Error rates
- Queue depths

### Logging
- Structured JSON logs
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Contextual information
- Centralized logging

### Health Checks
- Service availability
- Database connectivity
- Redis connectivity
- Agent status

## Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Next.js (React)
- **Databases**: MongoDB, Redis
- **LLM**: GLM 5.1
- **Automation**: Playwright
- **Security**: JWT, AES

## Future Enhancements

1. **Persistent Links**: Reusable workflows
2. **Learning Layer**: Preference adaptation
3. **Multi-Agent Hierarchy**: Sub-controllers
4. **Federated Execution**: Cross-server
5. **Visual Builder**: Drag-and-drop workflow editor
