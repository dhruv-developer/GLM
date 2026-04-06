# OneTapAI Frontend

Modern Next.js frontend for the OneTapAI (Zero-Interaction Execution Links with Multi-Agent System) application.

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI primitives
- **Animations**: Framer Motion
- **State Management**: React Hooks (with potential for Zustand)
- **HTTP Client**: Native fetch API with custom wrapper

## Features

- 🎨 **Modern UI**: Beautiful gradient design with smooth animations
- 🚀 **Real-time Updates**: Live task monitoring with auto-refresh
- 🔒 **Secure Execution**: Token-based task execution system
- 📊 **Analytics Dashboard**: Real-time statistics and task history
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile
- ⚡ **Type-Safe**: Full TypeScript implementation

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout with providers
│   ├── page.tsx            # Main dashboard page
│   ├── monitor/
│   │   └── [executionId]/  # Task execution monitor page
│   ├── analytics/          # Analytics page (future)
│   ├── tasks/              # Tasks list page (future)
│   └── settings/           # Settings page (future)
├── components/
│   ├── ui/                 # Radix UI components
│   ├── IntentInput.tsx     # Task creation form
│   ├── ExecutionMonitor.tsx # Real-time task monitoring
│   ├── MainLayout.tsx      # Main app layout
│   └── ...                 # Other components
├── lib/
│   └── api.ts              # API client functions
├── types/
│   └── index.ts            # TypeScript type definitions
└── .env.local              # Environment variables
```

## Setup & Installation

### Prerequisites

- Node.js 18+ installed
- Backend server running on port 8000

### Quick Start

1. **Install dependencies**:
```bash
npm install
```

2. **Configure environment** (`.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DEFAULT_USER_ID=default_user_001
```

3. **Start development server**:
```bash
npm run dev
```

4. **Open browser**: Navigate to `http://localhost:3000`

### Using the Startup Script

From the root directory:
```bash
./start.sh
```

This will:
- Check and start MongoDB & Redis
- Install dependencies
- Start both backend and frontend servers

## API Integration

The frontend connects to the backend through the API client in `lib/api.ts`:

### Available API Functions

```typescript
// Task Management
createTask(request: CreateTaskRequest): Promise<CreateTaskResponse>
executeTask(token: string): Promise<ExecutionResponse>
getTaskStatus(executionId: string): Promise<TaskStatus>
cancelTask(executionId: string): Promise<CancelResponse>

// Data Retrieval
getUserTasks(userId?: string, status?: string, limit?: number): Promise<TasksResponse>
getTaskLogs(executionId: string, level?: string, limit?: number): Promise<LogsResponse>
getStatistics(): Promise<StatisticsResponse>

// Health
healthCheck(): Promise<HealthResponse>
```

### Type Definitions

All types are defined in `types/index.ts`:

```typescript
interface TaskStatus {
  execution_id: string;
  status: "pending" | "planning" | "ready" | "running" | "completed" | "failed" | "cancelled";
  progress: number;
  completed_tasks: number;
  total_tasks: number;
  result?: any;
  error?: string;
  logs: LogEntry[];
}

interface CreateTaskRequest {
  intent: string;
  priority?: "low" | "medium" | "high";
  user_id?: string;
}

interface CreateTaskResponse {
  execution_id: string;
  execution_link: string;
  estimated_duration?: number;
  task_count: number;
}
```

## Key Features

### 1. Task Creation Dashboard

- **IntentInput Component**: Natural language task creation
- **Example Suggestions**: Clickable example intents
- **Real-time Validation**: Input validation with error handling
- **Auto-navigation**: Redirects to monitor page after creation

### 2. Execution Monitoring

- **Real-time Updates**: Auto-refresh every 3 seconds
- **Progress Tracking**: Visual progress bar with task counts
- **Live Logs**: Scrolling log viewer with color-coded levels
- **Status Indicators**: Animated status badges
- **Execution Links**: Copy-able secure execution links

### 3. Statistics Dashboard

- **Live Stats**: Real-time task statistics from backend
- **Health Monitoring**: Backend connection status
- **Recent Activity**: Latest tasks with status indicators
- **Auto-refresh**: Manual refresh button available

### 4. Responsive Design

- **Mobile-first**: Optimized for all screen sizes
- **Touch-friendly**: Large touch targets for mobile
- **Adaptive Layout**: Components reflow based on screen size
- **Performance**: Optimized animations and lazy loading

## Component Usage

### IntentInput

```tsx
import IntentInput from "@/components/IntentInput"

<IntentInput onTaskCreated={(data) => {
  console.log("Task created:", data)
  // data.executionId
  // data.executionLink
  // data.intent
}} />
```

### ExecutionMonitor

```tsx
import ExecutionMonitor from "@/components/ExecutionMonitor"

<ExecutionMonitor
  executionId="exec_123abc"
  executionLink="/execute/token_abc123"
  intent="Send birthday message to mom"
/>
```

## Styling

### Tailwind CSS

The project uses Tailwind CSS with custom configurations:

```javascript
// tailwind.config.ts
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: "var(--primary)",
        secondary: "var(--secondary)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
    },
  },
}
```

### Custom Components

UI components are built with Radix UI primitives:

- **Button**: Accessible button with variants
- **Card**: Container component for sections
- **Badge**: Status indicators
- **Textarea**: Multi-line text input
- **Progress**: Progress bar component

## State Management

Currently using React hooks for local state. For more complex state:

```typescript
// Example: Using Zustand for global state
import create from 'zustand'

const useTaskStore = create((set) => ({
  tasks: [],
  addTask: (task) => set((state) => ({ tasks: [...state.tasks, task] })),
  updateTask: (id, updates) => set((state) => ({
    tasks: state.tasks.map((t) => (t.id === id ? { ...t, ...updates } : t))
  })),
}))
```

## Error Handling

### API Errors

All API functions handle errors consistently:

```typescript
try {
  const response = await createTask(request)
  // Handle success
} catch (error) {
  // Error is thrown with message from backend
  alert(error.message)
}
```

### Display Errors

Components show user-friendly error messages:

- Form validation errors
- API connection errors
- Backend validation errors
- Network timeout errors

## Performance Optimization

### Code Splitting

Pages are automatically code-split by Next.js:

```typescript
// app/monitor/[executionId]/page.tsx
// Only loaded when navigating to monitor page
```

### Lazy Loading

Components can be lazy-loaded:

```typescript
const ExecutionMonitor = dynamic(() => import('@/components/ExecutionMonitor'), {
  loading: () => <Loader />,
  ssr: false
})
```

### Image Optimization

Use Next.js Image component:

```typescript
import Image from 'next/image'

<Image
  src="/logo.png"
  alt="Logo"
  width={200}
  height={50}
  priority
/>
```

## Development

### Build Commands

```bash
# Development
npm run dev

# Production build
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

### Environment Variables

Create `.env.local` for local development:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Default User ID
NEXT_PUBLIC_DEFAULT_USER_ID=default_user_001
```

## Troubleshooting

### Common Issues

**Issue**: Frontend can't connect to backend
- Check backend is running on port 8000
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`
- Check CORS settings in backend

**Issue**: Components not rendering
- Clear Next.js cache: `rm -rf .next`
- Restart dev server
- Check browser console for errors

**Issue**: Styling not working
- Rebuild Tailwind: `npm run build`
- Check `tailwind.config.ts` configuration
- Verify CSS imports in `layout.tsx`

## Future Enhancements

- [ ] Add WebSocket support for real-time updates
- [ ] Implement dark mode toggle
- [ ] Add task scheduling interface
- [ ] Create analytics dashboard with charts
- [ ] Implement user authentication
- [ ] Add offline support with PWA
- [ ] Create mobile app with React Native

## License

This project is part of the OneTapAI system. See main LICENSE file for details.
