# Web UI Quick Start Guide 🚀

## Prerequisites

- Node.js 20+ and npm
- Backend API running at http://localhost:8000

## Option 1: Local Development (Recommended)

```bash
# Navigate to web-ui directory
cd web-ui

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Start development server with hot reload
npm run dev
```

Open browser at **http://localhost:3000**

## Option 2: Docker Development

```bash
# From project root
docker-compose -f docker-compose.dev.yml up web-ui-dev

# Or build and run
cd web-ui
docker build -f Dockerfile.dev -t sutra-web-ui:dev .
docker run -p 3000:3000 sutra-web-ui:dev
```

## Option 3: Production Build

```bash
cd web-ui

# Build
npm run build

# Preview
npm run preview

# Or with Docker
docker build -t sutra-web-ui:latest .
docker run -p 80:80 sutra-web-ui:latest
```

## Full Stack Setup

Run both backend and frontend together:

```bash
# Development mode with hot reload
docker-compose -f docker-compose.dev.yml up

# Production mode
docker-compose up
```

Access:
- **Web UI**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Features

✨ **Drag & Drop** - Upload files with beautiful animations
🎨 **Material Design 3** - Modern, minimal interface
🌓 **Dark Mode** - Automatic theme switching
⚡ **Real-time** - Live conversion progress (WebSocket)
📱 **Responsive** - Works on all devices
🔒 **Type-Safe** - Full TypeScript implementation

## Project Structure

```
web-ui/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Route pages
│   ├── services/       # API communication layer
│   ├── types/          # TypeScript definitions
│   ├── theme/          # Material Design 3 theme
│   └── App.tsx         # Root component
├── public/             # Static assets
├── Dockerfile          # Production build
├── Dockerfile.dev      # Development build
└── package.json
```

## Development Tips

- **Hot Reload**: Changes auto-refresh in dev mode
- **Type Checking**: Run `npm run type-check`
- **Linting**: Run `npm run lint`
- **API Proxy**: Vite proxies `/api` and `/ws` to backend

## Troubleshooting

**Port 3000 in use:**
```bash
# Change port in vite.config.ts or use:
npm run dev -- --port 3001
```

**API connection failed:**
- Ensure backend is running on port 8000
- Check `VITE_API_BASE_URL` in `.env`
- Verify CORS is enabled on backend

**Build errors:**
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
```

Enjoy building with Sutra! 🎉
