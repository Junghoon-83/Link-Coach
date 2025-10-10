# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Link-Coach is an AI-powered leadership coaching platform consisting of:
- **Widget** (React + Netlify): Embeddable chat widget using Google Gemini API
- **Server** (FastAPI - planned but not in use): Backend infrastructure for PostgreSQL/ChromaDB integration

**Current Architecture**: The widget uses Netlify Serverless Functions directly, bypassing the FastAPI backend described in README.md.

## Repository Structure

```
Link-Coach/
├── widget/                  # React widget (ACTIVE - deployed to Netlify)
│   ├── src/                # React components
│   ├── netlify/functions/  # Serverless functions (.cjs files)
│   └── .claude/CLAUDE.md   # Widget-specific development guide
│
├── server/                  # FastAPI backend (PLANNED - not currently used)
│   ├── app/                # FastAPI application
│   │   ├── main.py        # App entrypoint
│   │   ├── api/v1/        # API endpoints
│   │   └── services/      # AI services, ML models
│   └── requirements.txt
│
└── docker-compose.yml      # Development environment (PostgreSQL, ChromaDB)
```

## Development Commands

### Widget Development (Current Implementation)
```bash
cd widget

# Local development
npm run dev              # Vite dev server (localhost:5173)
netlify dev              # Netlify dev server with functions (localhost:8888)

# Production deployment
npm run build            # Build for production
netlify deploy --prod    # Deploy to https://link-coach.netlify.app
```

### Server Development (Planned - Not Active)
```bash
cd server

# Setup Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run FastAPI server
uvicorn app.main:app --reload --port 8000

# Initialize database
python scripts/init_database.py
python scripts/init_chroma_data.py
```

### Full Stack with Docker (As Designed in README)
```bash
# Start all services (PostgreSQL, ChromaDB, FastAPI, React)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Architecture Notes

### Current vs Planned Implementation

**What's Actually Running:**
- Widget frontend: React 18 + Vite
- Backend: Netlify Serverless Functions (`widget/netlify/functions/`)
- AI: Google Gemini API via `@google/generative-ai` SDK
- State: Client-side only (Zustand)

**What's Planned (in README but not implemented):**
- FastAPI backend with JWT authentication
- PostgreSQL for report caching and logs
- ChromaDB for RAG-based conversation context
- ML model (`leadership_classifier.pkl`)

### Netlify Functions Details

Functions are located in `widget/netlify/functions/`:

**chat.cjs** - Real-time AI coaching chat
- Model: `gemini-2.5-flash`
- System prompt configured for "개별비전형" leadership style
- CommonJS syntax required (`.cjs` extension)

**generate.cjs** - Leadership report generation (unused - widget shows dummy data)
- Model: `gemini-2.0-flash-exp`

**Important**: All functions must:
- Use `.cjs` extension (package.json has `"type": "module"`)
- Use CommonJS: `exports.handler = async (event) => {}`
- Access `GEMINI_API_KEY` from Netlify environment variables

## Environment Variables

### Widget (Netlify Dashboard)
```
GEMINI_API_KEY=<your-google-gemini-api-key>
```

**DO NOT set** `VITE_API_BASE_URL` in production (causes CORS issues).

### Server (Not Currently Used)
```
GEMINI_API_KEY=<api-key>
JWT_SECRET_KEY=<random-string>
DATABASE_URL=postgresql://user:pass@localhost:5432/linkcoach
CORS_ORIGINS=http://localhost:5173,https://your-site.com
```

## Communication Flow

### Widget Embedding (postMessage API)

```javascript
// Parent site sends initialization message
window.postMessage({
  type: 'INIT_WIDGET',
  payload: {
    token: '<JWT_TOKEN>',
    userId: 'user_123',
    leadershipType: '개별비전형'
  }
}, '*');
```

**Demo Mode**: Widget auto-initializes after 500ms when running standalone for testing.

## Key Design Patterns

### Widget Component Hierarchy
```
App.jsx (postMessage handler)
  └── Widget.jsx (main container)
      ├── ReportViewer.jsx (static dummy report)
      └── ChatInterface.jsx (Gemini API chat)
```

### API Base URL Resolution
```javascript
// services/api.js
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/.netlify/functions'
```

## Testing

### Widget
```bash
cd widget
npm run lint         # ESLint
npm run format       # Prettier
```

### Server (if implementing)
```bash
cd server
pytest               # Run tests
pytest --cov=app     # With coverage
```

## Common Issues

### "Network Error" or CORS
- Remove `VITE_API_BASE_URL` from `.env`
- Verify `GEMINI_API_KEY` in Netlify: `netlify env:list`

### "API key not valid"
```bash
netlify env:set GEMINI_API_KEY "your-new-key"
netlify deploy --prod
```

### CommonJS/ESM Errors
- Netlify Functions require `.cjs` extension
- Use `require()` and `exports.handler`, not `import`/`export`

## Deployment

### Widget (Current Production)
- Platform: Netlify
- URL: https://link-coach.netlify.app
- Branch: Auto-deploys from `main`

### Server (Future - Google Cloud Run)
```bash
# Build images
docker build -t linkcoach-server ./server
docker build -t linkcoach-widget ./widget

# Deploy to Cloud Run
gcloud run deploy linkcoach-api \
  --image gcr.io/your-project/linkcoach-server \
  --platform managed \
  --region asia-northeast1
```

## Development Workflow

1. **Widget changes**: Work in `widget/` directory
   - See `widget/.claude/CLAUDE.md` for detailed widget development guide
   - Test locally with `netlify dev`
   - Deploy with `netlify deploy --prod`

2. **Backend changes**: Work in `server/` directory
   - Currently not integrated with production widget
   - Test with Docker: `docker-compose up`
   - API docs at http://localhost:8000/docs

## Future Integration Tasks

To connect the FastAPI backend with the widget:

1. Deploy FastAPI to Cloud Run
2. Update widget's `VITE_API_BASE_URL` to Cloud Run URL
3. Implement JWT token generation in parent site
4. Migrate Netlify Functions logic to FastAPI endpoints
5. Set up PostgreSQL and ChromaDB in production
6. Implement ML model loading and inference

## GitHub Repository
https://github.com/Junghoon-83/Link-Coach
