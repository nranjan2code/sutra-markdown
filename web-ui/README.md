# Sutra Markdown - Web UI 🎨

Beautiful, minimal Material Design 3 web interface for Sutra Markdown conversion service.

## ✨ Features

- **Material Design 3** - Modern, minimal aesthetics with M3 principles
- **Fully Responsive** - Works beautifully on desktop, tablet, and mobile
- **Dark Mode** - Automatic theme switching with smooth transitions
- **Real-time Progress** - WebSocket integration for live conversion updates
- **Type-Safe** - Full TypeScript implementation matching backend API
- **Performance Optimized** - Code splitting, lazy loading, and optimized bundles
- **API-First** - All communication through RESTful API
- **Docker Ready** - Production and development containers

## 🏗️ Architecture

```
web-ui/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── FileUpload/      # Drag-n-drop file upload
│   │   ├── ConversionResult/# Result display card
│   │   └── index.ts         # Barrel exports
│   ├── pages/               # Route pages
│   │   ├── Home/            # Main conversion page
│   │   └── index.ts
│   ├── services/            # API layer
│   │   └── api/
│   │       ├── client.ts    # Axios configuration
│   │       ├── conversion.ts# Conversion API
│   │       ├── health.ts    # Health & stats API
│   │       └── websocket.ts # WebSocket service
│   ├── types/               # TypeScript definitions
│   │   ├── api.ts           # API response types
│   │   └── ui.ts            # UI state types
│   ├── theme/               # Material Design 3 theme
│   │   └── theme.ts         # M3 color tokens & typography
│   ├── App.tsx              # Root component
│   └── main.tsx             # Entry point
├── public/                  # Static assets
├── Dockerfile               # Production build
├── Dockerfile.dev           # Development build
├── nginx.conf               # Nginx configuration
└── package.json
```

## 🚀 Quick Start

### Development

```bash
cd web-ui

# Install dependencies
npm install

# Start development server
npm run dev

# Open browser at http://localhost:3000
```

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Docker

```bash
# Development
docker build -f Dockerfile.dev -t sutra-web-ui:dev .
docker run -p 3000:3000 sutra-web-ui:dev

# Production
docker build -t sutra-web-ui:latest .
docker run -p 80:80 sutra-web-ui:latest
```

## 📋 Environment Variables

Create a `.env` file in the `web-ui` directory:

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000

# App Configuration
VITE_APP_NAME=Sutra Markdown
VITE_APP_VERSION=2.0.0

# Feature Flags
VITE_ENABLE_BATCH=true
VITE_ENABLE_REALTIME=true
VITE_MAX_FILE_SIZE=52428800  # 50MB
```

## 🎨 Design System

### Material Design 3 Tokens

The UI implements Google's Material Design 3 with:

- **Color System**: Primary, Secondary, Tertiary colors with light/dark variants
- **Typography Scale**: Display, Headline, Title, Body, Label sizes
- **Elevation**: Shadow tokens for depth and hierarchy
- **Shape**: Rounded corners (12px default)
- **Motion**: Smooth transitions and animations

### Custom Theme

Located in `src/theme/theme.ts`:

- Light and dark color palettes
- Inter font family with variable weights
- M3 component customizations
- Accessibility-first design

## 🧩 Component Architecture

### FileUpload Component

```tsx
import { FileUpload } from '@/components';

<FileUpload
  onFileSelect={(file) => handleFile(file)}
  onFileRemove={() => clearFile()}
  accept=".pdf,.docx,.pptx"
  maxSize={50 * 1024 * 1024}
  loading={isConverting}
  progress={conversionProgress}
/>
```

**Features:**
- Drag-and-drop support
- File validation (type & size)
- Progress indicator
- Beautiful animations

### ConversionResult Component

```tsx
import { ConversionResult } from '@/components';

<ConversionResult
  result={conversionResponse}
  filename="document.pdf"
/>
```

**Features:**
- Tier badge display
- Quality score visualization
- Copy to clipboard
- Download markdown
- Expandable preview
- Warning messages

## 🔌 API Integration

### Service Layer

All API communication is abstracted in the service layer:

```typescript
import { ConversionService } from '@/services';

// Convert document
const result = await ConversionService.convert(file, {
  tier: 'auto',
  use_cache: true,
});

// Convert async
const job = await ConversionService.convertAsync(file);

// Poll job status
const status = await ConversionService.pollJobStatus(
  job.job_id,
  1000,
  (progress) => console.log(progress)
);
```

### WebSocket Integration

```typescript
import { WebSocketService } from '@/services';

const ws = new WebSocketService();

ws.connect(
  jobId,
  (data) => {
    // Handle real-time updates
    console.log('Job status:', data.status);
    console.log('Progress:', data.progress);
  },
  (error) => console.error(error),
  () => console.log('Connection closed')
);
```

## 📦 Build & Deployment

### Build Optimization

The production build includes:

- **Code Splitting**: Vendor chunks for React, MUI
- **Tree Shaking**: Unused code elimination
- **Minification**: Terser for JavaScript, cssnano for CSS
- **Asset Optimization**: Image compression, font subsetting
- **Bundle Analysis**: Source maps for debugging

### Nginx Configuration

Production uses Nginx for:

- Static file serving with caching
- API reverse proxy
- WebSocket proxy
- Gzip compression
- Security headers
- SPA routing support

### Docker Multi-Stage Build

```dockerfile
# Stage 1: Build
FROM node:20-alpine as builder
# ... build steps

# Stage 2: Serve
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

**Benefits:**
- Small image size (~30MB)
- Fast deployment
- Production-ready nginx
- Health checks included

## 🧪 Development

### Type Safety

All API types match the FastAPI backend:

```typescript
// src/types/api.ts
export interface ConvertResponse {
  markdown: string;
  tier: string;
  quality_score: number;
  processing_time: number;
  word_count: number;
  line_count: number;
  cached: boolean;
  warnings: string[];
}
```

### Path Aliases

Clean imports with TypeScript path aliases:

```typescript
import { FileUpload } from '@/components';
import { ConversionService } from '@/services';
import { ConvertResponse } from '@/types';
```

### Code Quality

```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Format code
npm run format
```

## 🚢 Production Checklist

- [ ] Set `VITE_API_BASE_URL` to production API
- [ ] Enable HTTPS in nginx configuration
- [ ] Configure CORS on backend
- [ ] Set up CDN for static assets
- [ ] Enable error tracking (Sentry, etc.)
- [ ] Configure analytics (optional)
- [ ] Set up monitoring and health checks
- [ ] Review security headers
- [ ] Test with real production data
- [ ] Load testing and optimization

## 🎯 Roadmap

### Phase 1 (Current)
- [x] Single file conversion
- [x] Material Design 3 UI
- [x] Dark mode support
- [x] API integration
- [x] Docker setup

### Phase 2 (Planned)
- [ ] Batch conversion page
- [ ] Job tracking dashboard
- [ ] Settings page
- [ ] Conversion history
- [ ] Download all feature

### Phase 3 (Future)
- [ ] User authentication
- [ ] API key management
- [ ] Usage analytics
- [ ] Advanced settings
- [ ] Markdown editor

## 🤝 Contributing

1. Follow Material Design 3 principles
2. Maintain component separation of concerns
3. Write TypeScript types for all APIs
4. Test responsive design on multiple devices
5. Keep bundle size optimized

## 📄 License

MIT License - Part of Sutra Markdown project

## 🙏 Credits

- **Material Design 3** by Google
- **Material UI** for React components
- **Vite** for build tooling
- **TypeScript** for type safety

---

**Built with ❤️ using Material Design 3**

*Minimal. Beautiful. Fast.*
