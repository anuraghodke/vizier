# Getting Started - Frontend-Backend Integration

This branch (`connect-frontend-backend`) implements the full integration between the React frontend and FastAPI backend.

## What's New

This branch adds:
- **Backend API**: FastAPI server with endpoints for animation generation
- **Job Management**: Celery-based async task processing with Redis
- **Frontend Integration**: React components connected to backend API
- **File Handling**: Upload keyframes, process with AI, download results

## Quick Start

### 1. Prerequisites

- Docker Desktop installed and running
- Anthropic API key ([Get one here](https://console.anthropic.com/settings/keys))

### 2. Environment Setup

```bash
# Create .env file with your API key
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

### 3. Start All Services

```bash
# Start backend, frontend, Redis, and Celery worker
docker-compose up -d

# View logs (optional)
docker-compose logs -f
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 5. Test the Integration

1. Open http://localhost:3000 in your browser
2. Upload two PNG keyframes with transparency
3. Enter animation instructions (e.g., "create 8 smooth frames")
4. Click "Generate" and watch the AI create inbetween frames
5. Download the resulting frames as a ZIP file

## Architecture Overview

```
Frontend (Vite + React)  <-->  Backend (FastAPI)
     :3000                         :8000
                                     |
                                     v
                              Celery Worker
                                     |
                                     v
                                  Redis
                                     |
                                     v
                            AI Services (Claude + AnimateDiff)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/generate` | POST | Upload keyframes and start generation |
| `/api/jobs/{job_id}` | GET | Check job status |
| `/api/frames/{job_id}/{frame}` | GET | Get individual frame |
| `/api/download/{job_id}` | GET | Download all frames as ZIP |
| `/health` | GET | Health check |

## Development Mode

If you want to run services individually (not using Docker):

**Terminal 1 - Backend:**
```bash
cd backend
source ../.venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Celery Worker:**
```bash
cd backend
source ../.venv/bin/activate
celery -A app.workers.celery_worker worker --loglevel=info
```

**Terminal 3 - Redis:**
```bash
redis-server
```

**Terminal 4 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Troubleshooting

### Frontend can't connect to backend
- Check that both services are running: `docker-compose ps`
- Verify CORS settings in `backend/app/main.py`
- Check browser console for errors

### Jobs stuck in "processing"
- Check Celery worker logs: `docker-compose logs celery`
- Verify Redis is running: `docker-compose ps redis`
- Check backend logs: `docker-compose logs backend`

### Generation fails
- Verify ANTHROPIC_API_KEY is set correctly in `.env`
- Check Celery worker logs for error details
- Ensure uploads/outputs directories exist and are writable

## Next Steps

- Review the [main README](README.md) for project overview
- Check [ANIMATION_STYLE.md](docs/ANIMATION_STYLE.md) to understand the animation philosophy
- Explore the API documentation at http://localhost:8000/docs
