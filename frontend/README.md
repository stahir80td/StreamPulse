# StreamPulse Frontend

React dashboard for real-time content analytics visualization. Built with **mobile-first responsive design**.

## Features

### 📊 Real-Time Dashboard
- Auto-refreshes every 2 seconds
- Live metrics cards with trend indicators
- Responsive charts (Recharts library)
- Mobile-friendly touch interactions

### 📱 Mobile-First Design
- **Mobile (<768px)**: Single column layout, optimized charts
- **Tablet (768-1023px)**: 2-column grid, larger typography
- **Desktop (1024px+)**: 3-column grid, full-width charts
- **Touch-friendly**: Larger tap targets, swipe-friendly charts

### 🎨 Components
- **StatsCards**: Real-time metrics with color-coded status
- **TrendingChart**: Bar chart for top content
- **RegionChart**: Regional performance with health indicators
- **TimeSeriesChart**: Line chart for downloads over time
- **AlertsList**: Priority-sorted alerts with severity badges

## Setup

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your backend API URL
```

### Configuration

Edit `.env` file:

```bash
# Backend API URL
REACT_APP_API_URL=http://localhost:8000

# Refresh interval (milliseconds)
REACT_APP_REFRESH_INTERVAL=2000
```

## Running Locally

```powershell
# Development mode (hot reload)
npm start

# Opens browser at http://localhost:3000
```

## Building for Production

```powershell
# Create optimized production build
npm run build

# Output in build/ directory
```

## Deployment

### Deploy to Vercel (Recommended)

```powershell
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod

# Set environment variable
vercel env add REACT_APP_API_URL production
# Enter your Railway backend URL when prompted
```

### Manual Deployment

```powershell
# Build
npm run build

# Serve static files from build/
# Upload to any static hosting (Netlify, GitHub Pages, etc.)
```

## Project Structure

```
frontend/
├── public/
│   └── index.html              # HTML template
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx       # Main container
│   │   ├── StatsCards.jsx      # Metrics cards
│   │   ├── TrendingChart.jsx   # Bar chart
│   │   ├── RegionChart.jsx     # Regional chart
│   │   ├── TimeSeriesChart.jsx # Line chart
│   │   └── AlertsList.jsx      # Alerts widget
│   ├── services/
│   │   └── api.js              # API client
│   ├── styles/
│   │   ├── App.css             # Global styles
│   │   └── Dashboard.css       # Dashboard styles
│   ├── App.jsx                 # Root component
│   └── index.jsx               # Entry point
├── package.json
├── vercel.json                 # Vercel config
└── README.md
```

## API Integration

The dashboard fetches data from 6 API endpoints:

```javascript
// Realtime stats (last 5 minutes)
GET /api/stats/realtime?minutes=5

// Top trending content
GET /api/stats/trending?minutes=5&limit=5

// Regional health
GET /api/stats/regions?minutes=5

// Alerts
GET /api/stats/alerts?limit=10

// Time series (last hour)
GET /api/stats/timeseries?minutes=60

// Device stats
GET /api/stats/devices?minutes=5&limit=10
```

All requests are parallelized for optimal performance.

## Responsive Breakpoints

```css
/* Mobile-first (default) */
< 768px: Single column, stacked layout

/* Tablet */
768px - 1023px: 2-column grid, medium charts

/* Desktop */
1024px+: 3-column grid, full-width charts

/* Large Desktop */
1440px+: Optimized for large screens
```

## Performance Optimizations

### 1. **Code Splitting**
- React lazy loading (future enhancement)
- Chunked bundles for faster initial load

### 2. **API Caching**
- Backend caches responses (2-second TTL)
- Parallel requests reduce latency

### 3. **Chart Optimization**
- Recharts uses SVG (lightweight)
- Responsive containers adjust to screen size
- Reduced data points on mobile

### 4. **Image Optimization**
- No images used (pure CSS/SVG)
- Emoji for icons (native rendering)

## Browser Support

- **Modern Browsers**: Chrome, Firefox, Safari, Edge (last 2 versions)
- **Mobile**: iOS Safari 12+, Chrome Android 90+
- **IE**: Not supported (uses modern ES6+ features)

## Accessibility

- **ARIA Labels**: All interactive elements labeled
- **Keyboard Navigation**: Full keyboard support
- **Focus Indicators**: Visible focus outlines
- **Color Contrast**: WCAG AA compliant
- **Screen Readers**: Semantic HTML structure
- **Reduced Motion**: Respects prefers-reduced-motion

## Testing

```powershell
# Run tests
npm test

# Coverage report
npm test -- --coverage

# E2E tests (future)
npm run e2e
```

## Troubleshooting

### Issue: "CORS error when calling API"
```
Solution:
1. Ensure REACT_APP_API_URL is correct in .env
2. Verify backend ALLOWED_ORIGINS includes frontend URL
3. Check browser console for exact error
```

### Issue: "Dashboard shows no data"
```
Solution:
1. Check if backend API is running
2. Open browser DevTools → Network tab
3. Verify API calls return 200 status
4. Check if database has data (run Flink processor)
```

### Issue: "Charts not rendering on mobile"
```
Solution:
1. Charts use ResponsiveContainer - should work
2. Check browser console for errors
3. Try hard refresh (Ctrl+Shift+R)
4. Ensure device viewport is detected correctly
```

### Issue: "App not refreshing data"
```
Solution:
1. Check REACT_APP_REFRESH_INTERVAL in .env
2. Verify no JavaScript errors in console
3. Check if backend is responding (Network tab)
4. Try hard refresh
```

## Development Tips

### Hot Reload
```powershell
# Changes auto-reload browser
npm start
```

### Debug API Calls
```javascript
// In api.js, uncomment console.log
console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
```

### Test Responsive Design
```
1. Open Chrome DevTools (F12)
2. Click device toolbar icon (Ctrl+Shift+M)
3. Select device (iPhone, iPad, etc.)
4. Test interactions
```

### Performance Profiling
```
1. Open React DevTools
2. Go to Profiler tab
3. Click Record
4. Interact with dashboard
5. Stop recording
6. Analyze render times
```

## Future Enhancements

- [ ] Dark mode support
- [ ] User authentication
- [ ] Customizable dashboard widgets
- [ ] Export data to CSV/PDF
- [ ] Real-time WebSocket updates (replace polling)
- [ ] Offline mode with service workers
- [ ] Multi-language support (i18n)
- [ ] Advanced filtering and date ranges
- [ ] Drag-and-drop widget reordering

## Contributing

This is a portfolio project, but suggestions welcome!

## License

MIT License

---

