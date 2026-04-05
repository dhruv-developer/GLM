# 🎨 ZIEL-MAS Frontend - Beautiful Multi-Page UI

A stunning, modern multi-page frontend for the ZIEL-MAS system built with Next.js 14, shadcn/ui, and Framer Motion.

## ✨ Features

### 🎯 **Multi-Page Architecture**
- **Dashboard** - Beautiful home with stats, activity feed, and task creation
- **Tasks** - Advanced task management with filtering, sorting, and search
- **Analytics** - Comprehensive charts and performance insights
- **Settings** - Full configuration with tabs and form controls

### 🎨 **Beautiful UI Components**
- **shadcn/ui** - Modern, accessible component library
- **Dark Mode** - Perfect dark mode with CSS variables
- **Glass Morphism** - Stunning glass effects and gradients
- **Responsive Design** - Mobile-first, fully responsive

### 🚀 **Advanced Features**
- **Real-time Updates** - Live task status monitoring
- **Data Visualization** - Charts with Recharts
- **Animations** - Smooth transitions with Framer Motion
- **Mobile Navigation** - Touch-friendly mobile menu
- **Form Controls** - Advanced forms with validation

## 🛠️ Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui + Radix UI
- **Charts**: Recharts
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Language**: TypeScript

## 📦 Installation

```bash
cd frontend
npm install
```

## 🎬 Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see the beautiful UI.

## 🏗️ Build

```bash
npm run build
npm start
```

## 📱 Pages Overview

### 1. **Dashboard** (`/`)
- 📊 Key metrics cards with animated counters
- ✨ Quick task creation with examples
- 🕒 Recent activity feed
- 🎯 Feature highlights

### 2. **Tasks** (`/tasks`)
- 📋 Complete task list with expandable details
- 🔍 Advanced search and filtering
- 📶 Sort by status, date, progress
- 📊 Visual progress indicators
- 🎨 Status badges with icons

### 3. **Analytics** (`/analytics`)
- 📈 Task completion trends (Area chart)
- 🥧 Task type distribution (Pie chart)
- 📊 Agent performance (Bar chart)
- ⏰ Hourly activity patterns (Line chart)
- 🏆 Performance insights

### 4. **Settings** (`/settings`)
- 👤 Profile management
- 🔔 Notification preferences
- 🔒 Security settings
- 🔑 API configuration
- 🎨 Appearance options
- ⚡ Advanced system settings

## 🎨 UI Components

### Custom Components
- `SidebarNav` - Beautiful sidebar navigation
- `Header` - Top navigation bar
- `MainLayout` - Responsive layout wrapper
- `StatsCard` - Animated stat cards
- `HoverCard` - Interactive hover effects
- `LoadingDots` - Elegant loading animation
- `PulseRing` - Pulse animation effects
- `ShimmerBadge` - Shimmer effect badges
- `PageTransition` - Smooth page transitions
- `StaggerChildren` - Staggered animations

### shadcn/ui Components
- Button, Card, Input, Textarea
- Badge, Tabs, Select, Switch
- Progress, Dialog, Dropdown
- And many more...

## 🎭 Animations

### Page Transitions
- Smooth fade-in and slide-up effects
- Staggered children animations
- Hover lift effects

### Micro-interactions
- Button hover states
- Card scale effects
- Loading animations
- Progress animations

### Mobile Optimizations
- Touch-friendly tap targets
- Swipe gestures
- Mobile navigation
- Responsive breakpoints

## 🌙 Dark Mode

The UI features a perfect dark mode implementation:
- CSS variables for theming
- Smooth transitions
- High contrast ratios
- Accessible color schemes

## 📱 Responsive Design

- **Mobile** (< 768px): Stacked layout, mobile menu
- **Tablet** (768px - 1024px): 2-column grid
- **Desktop** (> 1024px): 3-4 column grids

## 🎯 Key Features

### Dashboard
- ✅ Animated stat counters
- ✅ Gradient backgrounds
- ✅ Glass morphism effects
- ✅ Real-time activity feed

### Tasks Page
- ✅ Advanced filtering
- ✅ Sortable columns
- ✅ Expandable task details
- ✅ Status badges
- ✅ Progress bars

### Analytics
- ✅ Interactive charts
- ✅ Performance metrics
- ✅ Agent statistics
- ✅ Activity patterns

### Settings
- ✅ Tabbed interface
- ✅ Form controls
- ✅ Toggle switches
- ✅ API key management

## 🚀 Performance

- ⚡ Optimized builds
- 📦 Code splitting
- 🎯 Lazy loading
- 📈 Fast page loads

## 🎨 Customization

### Colors
Edit `tailwind.config.ts` to customize the color scheme:
```typescript
primary: {
  DEFAULT: "hsl(262 83% 58%)",
  // ... more colors
}
```

### Animations
Edit `globals.css` to customize animations:
```css
@keyframes your-animation {
  /* your keyframes */
}
```

## 📄 File Structure

```
frontend/
├── app/
│   ├── page.tsx           # Dashboard
│   ├── tasks/
│   │   └── page.tsx       # Tasks page
│   ├── analytics/
│   │   └── page.tsx       # Analytics page
│   ├── settings/
│   │   └── page.tsx       # Settings page
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── components/
│   ├── ui/                # shadcn/ui components
│   ├── sidebar-nav.tsx
│   ├── header.tsx
│   ├── main-layout.tsx
│   └── ...custom components
└── lib/
    ├── api.ts
    └── utils.ts
```

## 🎉 Getting Started

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Run development server**
   ```bash
   npm run dev
   ```

3. **Open browser**
   Navigate to `http://localhost:3000`

4. **Explore the beautiful UI!**
   - Dashboard for overview
   - Tasks for management
   - Analytics for insights
   - Settings for configuration

## 🔧 Configuration

### API Endpoints
Configure in `lib/api.ts`:
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
```

### Environment Variables
Create `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📝 Notes

- Built with Next.js 14 App Router
- TypeScript for type safety
- Responsive by default
- Accessible (WCAG AA)
- SEO optimized
- Performance optimized

## 🎨 Design Philosophy

- **Minimal**: Clean, uncluttered interface
- **Functional**: Every element serves a purpose
- **Beautiful**: Gradient accents and glass effects
- **Responsive**: Works on all devices
- **Accessible**: High contrast, keyboard navigation

## 🚀 Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] More chart types
- [ ] Export functionality
- [ ] Advanced filtering
- [ ] User preferences
- [ ] Themes customization

## 📞 Support

For issues or questions, please refer to the main project documentation.

---

**Built with ❤️ using Next.js, shadcn/ui, and Framer Motion**
