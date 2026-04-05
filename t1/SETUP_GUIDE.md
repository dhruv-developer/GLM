# ZIEL-MAS Setup Guide

This guide will help you set up and run the ZIEL-MAS application with proper frontend-backend connections.

## Prerequisites

- **Node.js** (v18+) and npm/yarn
- **Python** (v3.12+) and pip
- **MongoDB** (running on localhost:27017)
- **Redis** (running on localhost:6379)
- **GLM API Key** from [GLM.ai](https://glm.ai)

## 1. Backend Setup

### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your configuration
# Important: Update these values:
# - GLM_API_KEY=your-actual-api-key
# - JWT_SECRET=generate-a-secure-secret
# - ENCRYPTION_KEY=generate-a-secure-key
```

### Start MongoDB & Redis

Make sure MongoDB and Redis are running:

```bash
# MongoDB (default port 27017)
mongod

# Redis (default port 6379)
redis-server
```

### Start Backend Server

```bash
cd backend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

## 2. Frontend Setup

### Install Dependencies

```bash
cd frontend
npm install
```

### Configure Environment

The frontend uses `.env.local` for configuration (already created):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DEFAULT_USER_ID=default_user_001
```

### Start Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 3. Verify Connection

1. Open `http://localhost:3000` in your browser
2. Check the top-right badge - it should show "GLM 5.1 Multi-Agent System Active"
3. Statistics should load from the backend
4. Recent tasks should appear (if any exist)

## 4. Test the System

### Create a Task

1. Enter a task in the input field:
   ```
   Send birthday message to mom at 12 AM
   ```
2. Click "Create Task"
3. You'll be redirected to the execution monitor page

### Monitor Execution

1. The execution monitor will show real-time status
2. Progress bar updates every 3 seconds
3. Logs appear as tasks are processed
4. Results display when execution completes

## API Endpoints

### Task Management
- `POST /api/v1/create-task` - Create a new task
- `GET /api/v1/execute/{token}` - Execute a task via secure token
- `GET /api/v1/status/{execution_id}` - Get task status
- `POST /api/v1/cancel/{execution_id}` - Cancel a task

### Data Retrieval
- `GET /api/v1/user/{user_id}/tasks` - Get user's tasks
- `GET /api/v1/logs/{execution_id}` - Get execution logs
- `GET /api/v1/stats` - Get system statistics

### Health
- `GET /health` - Health check endpoint

## Troubleshooting

### Backend Won't Start

**Issue:** Port 8000 already in use
```bash
# Check what's using the port
lsof -i :8000
# Kill the process or use a different port
python -m uvicorn api.main:app --port 8001
```

**Issue:** MongoDB/Redis connection failed
```bash
# Check if MongoDB is running
pgrep mongod
# Check if Redis is running
pgrep redis-server
# Start them if needed
brew services start mongodb-community
brew services start redis
```

### Frontend Can't Connect to Backend

**Issue:** CORS errors
- Check backend CORS settings in `.env`
- Ensure `ALLOWED_ORIGINS` includes `http://localhost:3000`

**Issue:** Connection refused
- Verify backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in frontend `.env.local`

### Tasks Not Executing

**Issue:** Invalid GLM API key
- Verify your API key in backend `.env`
- Check API key is valid and has credits

**Issue:** Task stuck in "pending" status
- Check backend logs for errors
- Verify Redis is working properly
- Check MongoDB for task records

## Development Tips

### Hot Reload
- Frontend: Automatically reloads on file changes
- Backend: Use `--reload` flag for auto-restart

### Debugging
- Backend: Check console logs from `loguru`
- Frontend: Use browser DevTools Console
- API: Use `/api/v1/stats` to check system health

### Testing API Directly

```bash
# Health check
curl http://localhost:8000/health

# Create a task
curl -X POST http://localhost:8000/api/v1/create-task \
  -H "Content-Type: application/json" \
  -d '{"intent": "Test task", "priority": "medium"}'

# Get task status
curl http://localhost:8000/api/v1/status/{execution_id}
```

## Production Deployment

For production deployment, you'll need to:

1. **Use production-ready MongoDB and Redis instances**
2. **Set strong JWT_SECRET and ENCRYPTION_KEY**
3. **Configure proper CORS origins**
4. **Use a production WSGI server** (e.g., gunicorn)
5. **Enable HTTPS**
6. **Set up monitoring and logging**
7. **Configure environment variables** (don't use `.env` in production)

## Support

If you encounter issues:
1. Check the logs (both frontend and backend)
2. Verify all services are running (MongoDB, Redis)
3. Ensure environment variables are correctly set
4. Check network connectivity between frontend and backend
