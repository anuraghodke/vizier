# Claude Context File - Vizier Project
**AI-Assisted 2D Animation Inbetweening Tool**

> This file provides complete context for AI assistants when working on this project. Read this first to understand the project structure, current status, and development guidelines.

---

## Project Overview

**Name**: Vizier
**Purpose**: Help beginner artists create smooth 2D animations by auto-generating intermediate frames between keyframes
**Target User**: Artists using Procreate who struggle with manual inbetweening
**Current Status**: **Model Evaluation Phase** - Phase 1 complete, evaluating alternative models (RIFE/Ebsynth) before proceeding to Phase 2

### What It Does
1. User uploads 2 PNG keyframes with transparency (Procreate exports)
2. User describes motion in natural language (e.g., "create 8 bouncy frames")
3. Claude API parses instruction → structured parameters
4. Google FILM model generates intermediate frames
5. User downloads frames as ZIP → imports back to Procreate

### Animation Philosophy
Vizier supports **classic cel animation techniques** with physics-based interpolation. Objects should **move across the screen**, not fade in/out. See **[docs/ANIMATION_STYLE.md](./ANIMATION_STYLE.md)** for detailed animation principles and testing strategy.

---

## Current Project Status

### Completed Phases

✅ **Phase 0: Environment Setup & Validation**
- FILM model validated and working
- Claude API tested and working
- Docker infrastructure configured
- See [docs/PHASE_0_SUMMARY.md](./PHASE_0_SUMMARY.md) and [docs/PHASE_0_FINDINGS.md](./PHASE_0_FINDINGS.md)

✅ **Phase 1: Core Backend Services**
- Built `film_service.py` with image preprocessing and FILM integration
- Built `claude_service.py` with prompt engineering for NL parsing
- Defined Pydantic schemas for data validation
- Unit tests passing for both services
- See [docs/PHASE_1_SUMMARY.md](./PHASE_1_SUMMARY.md)

### Current Status: Model Evaluation Phase

⚠️ **PAUSE ON PHASE 2** - Model Evaluation in Progress

Phase 0 testing revealed **critical limitations** with FILM:
- ❌ Color + Motion = ghosting (red→blue ball shows two faint balls, no purple)
- ❌ Object transformations = crossfading instead of motion
- ⚠️ Only works well for same-color objects or camera pans

**Current Activity**: Evaluating alternative models to find best fit
- See [docs/MODEL_COMPARISON_PLAN.md](./MODEL_COMPARISON_PLAN.md) for research strategy
- See [docs/PHASE_0_FINDINGS.md](./PHASE_0_FINDINGS.md) for detailed FILM analysis

**Experiment Branches**:
- `experiment/rife` - Testing RIFE (anime-focused interpolation)
- `experiment/ebsynth` - Testing Ebsynth (style-preserving synthesis)
- `experiment/animatediff` - Testing AnimateDiff (diffusion-based, optional)

**Decision Point**: Once model evaluation complete, will either:
1. Continue with FILM (accept limitations, document clearly)
2. Switch to better model (RIFE, Ebsynth, or hybrid)
3. Resume Phase 2 with chosen model

### On Hold Until Model Decision

🔄 **Phase 2: Task Queue & Job Processing** (PAUSED)
- Setup Celery worker with Redis
- Implement `generate_frames` async task
- Add progress tracking
- Error handling and cleanup

*Note: Will resume once we've decided on the interpolation model*

---

## Project Structure

```
vizier/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI entry point (to be created)
│   │   ├── services/
│   │   │   ├── film_service.py        # ✅ FILM model wrapper + image processing
│   │   │   └── claude_service.py      # ✅ Claude API client + prompt engineering
│   │   ├── workers/
│   │   │   └── celery_worker.py       # Async task: generate_frames() (to be created)
│   │   ├── models/
│   │   │   └── schemas.py             # ✅ Pydantic models (AnimationParams, JobStatus)
│   │   └── routers/
│   │       └── generation.py          # API endpoints (to be created)
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── pages/
│   │   └── index.tsx                  # Main application page (to be created)
│   ├── components/
│   │   ├── KeyframeUploader.tsx       # Drag-drop file upload (to be created)
│   │   ├── InstructionInput.tsx       # Natural language textarea (to be created)
│   │   ├── TimelinePreview.tsx        # Canvas-based frame viewer (to be created)
│   │   └── DownloadPanel.tsx          # Download + metadata display (to be created)
│   ├── hooks/
│   │   └── useJobStatus.ts            # Job polling hook (to be created)
│   ├── utils/
│   │   └── api.ts                     # Axios API client (to be created)
│   └── package.json
│
├── models/
│   └── film/                          # Google FILM repo (cloned, gitignored)
│
├── docs/                              # 📁 Documentation
│   ├── CLAUDE.md                      # This file - AI assistant context
│   ├── MODEL_COMPARISON_PLAN.md       # Model evaluation research plan
│   ├── ANIMATION_STYLE.md             # Animation principles and testing strategy
│   ├── PHASE_0_SUMMARY.md             # Phase 0 results
│   ├── PHASE_0_FINDINGS.md            # FILM behavior analysis
│   └── PHASE_1_SUMMARY.md             # Phase 1 results
│
├── tests/                             # 📁 All test files
│   ├── test_film_setup.py             # FILM validation script
│   ├── test_film_with_images.py       # FILM + transparency test
│   ├── test_claude_api.py             # Claude API test
│   ├── test_services.py               # Service unit tests
│   ├── test_physics_interpolation.py  # Physics-based motion tests
│   ├── test_physics_with_background.py
│   ├── test_same_color_motion.py
│   ├── test_images/                   # Test assets
│   └── test_output/                   # Generated test outputs
│
├── uploads/                           # Temp keyframe storage (gitignored)
├── outputs/                           # Generated frames by job_id (gitignored)
│
├── docker-compose.yml                 # Orchestrates: redis, backend, celery, frontend
├── .env                               # Secrets (gitignored)
├── .env.example                       # Template
│
└── README.md                          # User-facing documentation
```

---

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Task Queue**: Celery + Redis
- **AI Models**:
  - **Interpolation**: FILM (current), evaluating RIFE/Ebsynth alternatives
  - **NL Parsing**: Claude API (`claude-sonnet-4-5-20250929`)
- **Image Processing**: Pillow, OpenCV, NumPy

### Frontend
- **Framework**: Next.js 14 + React 18 + TypeScript
- **Styling**: TailwindCSS
- **HTTP**: Axios

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Storage**: Local filesystem (uploads/, outputs/)
- **Cache**: Redis 7

---

## Key Technical Findings (Phase 0)

### FILM Model Behavior
- **Source**: TensorFlow Hub (`https://tfhub.dev/google/film/1`)
- **Input Format**: Dictionary with keys `{'x0': tensor, 'x1': tensor, 'time': [[t]]}`
- **Output**: `result['image'][0]` - interpolated frame as numpy array
- **Image Format**: RGB only (0.0-1.0 range, sometimes slightly outside)
- **Performance**: ~2-3 seconds per frame on CPU (M-series Mac)
- **Limitations**:
  - Generates 2^n-1 frames recursively (can't request exact count)
  - Requires even dimensions (width/height divisible by 2)
  - No alpha channel support (must handle separately)

### Transparency Handling
**Critical**: FILM only processes RGB channels. Alpha must be separated before processing and interpolated independently.

```python
# Separate alpha before FILM
rgb = np.array(pil_img.convert('RGB')).astype(np.float32) / 255.0
alpha = np.array(pil_img.split()[3]).astype(np.float32) / 255.0

# Interpolate RGB with FILM
result = model({'x0': rgb_batch, 'x1': rgb_batch2, 'time': [[t]]})

# Interpolate alpha linearly
alpha_interpolated = (1 - t) * alpha1 + t * alpha2

# Recombine
rgba = np.dstack([rgb_output * 255, alpha_interpolated * 255])
```

### Claude API
- **Model**: `claude-sonnet-4-5-20250929`
- **Response Time**: ~1-2 seconds
- **Accuracy**: 100% on test cases
- **Cost**: ~$0.003 per request
- **Output**: Returns valid JSON when prompted correctly

---

# MVP Plan: AI-Assisted 2D Animation Inbetweening Tool

## Problem Statement

**User Context:**
- Beginner artist using Procreate for 2D animation
- Proficient at drawing individual keyframes
- Struggles with drawing in-between frames (inbetweening/tweening)
- Needs assistance creating smooth transitions between keyframes

**Core Problem:**
Manual frame interpolation is time-consuming and technically challenging for beginners. The tool should accept two keyframes and a natural language description of the desired motion, then automatically generate intermediate frames that bridge the gap.

**Specific Requirements:**
- Accept PNG files with transparency (Procreate export format)
- Parse natural language instructions (e.g., "create 8 bouncy frames") into animation parameters
- Generate intermediate frames that maintain visual consistency
- Preserve transparency in all generated frames
- Provide preview and download capabilities
- Work on local machine without GPU (CPU-only processing acceptable)

**Expected Input:**
- Frame 1: PNG with transparency (start keyframe)
- Frame 2: PNG with transparency (end keyframe)
- Instruction: Natural language text describing desired motion and frame count

**Expected Output:**
- Sequence of PNG frames with transparency preserved
- Downloadable as individual files or ZIP archive
- Importable back into Procreate for further editing

---

## System Architecture

### High-Level Flow
```
User Upload (2 keyframes + instruction)
    ↓
FastAPI (validate, save files, create job)
    ↓
Celery Queue (Redis)
    ↓
Celery Worker
    ├→ Claude API (parse instruction → parameters)
    ├→ Preprocess images (resize, ensure even dimensions)
    ├→ FILM Model (generate intermediate frames)
    └→ Post-process (preserve transparency, select frames)
    ↓
Store output frames
    ↓
Return to frontend (preview + download)
```

### Component Responsibilities

**FastAPI Server:**
- Handle file uploads (multipart/form-data)
- Validate PNG files
- Create unique job IDs
- Queue generation tasks
- Serve generated frames
- Provide job status polling endpoint
- Create ZIP archives for download

**Celery Worker:**
- Process generation jobs asynchronously
- Update job progress at each stage
- Handle errors and cleanup
- Run single-threaded (concurrency=1 for CPU)

**Claude Service:** ✅ IMPLEMENTED
- Parse natural language instructions
- Extract structured parameters (frame count, motion type, timing curve)
- Return JSON with animation specifications

**FILM Service:** ✅ IMPLEMENTED
- Preprocess images (resize, even dimensions, format conversion)
- Execute FILM model
- Handle recursive frame generation
- Select appropriate frames based on timing parameters
- Preserve alpha channel (transparency)

**Frontend:**
- Provide drag-and-drop file upload
- Show upload previews
- Display progress during generation
- Render frame timeline with scrubber
- Enable playback at various FPS
- Provide download options

---

## API Endpoints (Phase 3)

### POST /api/generate
- Accept: multipart/form-data (frame1, frame2, instruction)
- Validate files are PNG
- Save to uploads/{job_id}_frame1.png, uploads/{job_id}_frame2.png
- Queue Celery task
- Return: `{job_id: string, status: "queued"}`

### GET /api/jobs/{job_id}
- Poll job status
- Return: `{status: "pending|processing|complete|failed", progress: 0-100, stage?: string, frames?: string[], params?: object, error?: string}`

### GET /api/frames/{job_id}/{frame_name}
- Serve individual generated frame as PNG
- Return: Image file response

### GET /api/download/{job_id}
- Create ZIP of all frames in job
- Return: ZIP file download

---

## Data Schemas

### AnimationParams (Claude Output) ✅ IMPLEMENTED
```python
{
    "num_frames": int,           # 4-32
    "motion_type": str,          # "linear" | "ease-in" | "ease-out" | "ease-in-out" | "bounce" | "elastic"
    "speed": str,                # "very-slow" | "slow" | "normal" | "fast" | "very-fast"
    "emphasis": str,             # Brief description
    "interpolation_times": List[float]  # Optional: [0.0, 0.25, 0.5, 0.75, 1.0]
}
```

### JobStatus (API Response) ✅ IMPLEMENTED
```python
{
    "job_id": str,               # UUID4
    "status": str,               # "pending" | "processing" | "complete" | "failed"
    "progress": int,             # 0-100
    "stage": Optional[str],      # "analyzing" | "preprocessing" | "generating" | "complete"
    "frames": Optional[List[str]],  # ["frame_001.png", "frame_002.png", ...]
    "params": Optional[AnimationParams],
    "error": Optional[str]
}
```

---

## Task Pipeline (Celery - Phase 2)

```python
@celery_app.task(bind=True)
def generate_frames(self, job_id, frame1_path, frame2_path, instruction):
    # Stage 1: Analyzing (0-20%)
    update_status(job_id, "analyzing", 0)
    params = claude_service.parse_instruction(instruction)
    update_status(job_id, "analyzing", 20)

    # Stage 2: Preprocessing (30-40%)
    update_status(job_id, "preprocessing", 30)
    rgb1, alpha1, rgb2, alpha2 = film_service.preprocess(frame1_path, frame2_path)
    update_status(job_id, "preprocessing", 40)

    # Stage 3: Generating (50-70%)
    update_status(job_id, "generating", 50)
    frames = film_service.interpolate(rgb1, rgb2, alpha1, alpha2, params)
    update_status(job_id, "generating", 70)

    # Stage 4: Saving (80-90%)
    update_status(job_id, "generating", 80)
    save_frames(job_id, frames)

    # Stage 5: Complete (100%)
    update_status(job_id, "complete", 100, frames=frame_list)
```

---

## Docker Services Configuration

### Services
1. **redis**: Redis 7 Alpine (message broker)
2. **backend**: FastAPI server (port 8000)
3. **celery_worker**: Celery worker (concurrency=1)
4. **frontend**: Next.js dev server (port 3000)

### Shared Volumes
- `./uploads:/app/uploads` - Uploaded keyframes
- `./outputs:/app/outputs` - Generated frames
- `./models/film:/models/film:ro` - FILM model (read-only)

### Environment Variables
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...  # Anthropic API key
REDIS_URL=redis://redis:6379/0      # Redis connection
API_URL=http://localhost:8000        # Backend URL
```

---

## Key Technical Considerations

### Image Preprocessing Requirements
- FILM requires even dimensions (width and height divisible by 2)
- Optimal resolution: 512-1024px for CPU performance
- Downscale large images (>1024px) to avoid memory issues
- Maintain aspect ratio during resize

### Natural Language Parsing Strategy
- Use Claude with strict JSON output format
- Provide clear examples in system prompt
- Handle cases where Claude returns markdown code blocks
- Validate all required fields present
- Use sensible defaults if parsing fails partially
- Retry once on malformed JSON

### Performance Expectations (CPU-only)
- Claude API call: 1-3 seconds
- Image preprocessing: <1 second per image
- FILM generation: 10-30 seconds per frame pair (depends on resolution)
- Total time for 8 frames: 1-3 minutes
- User should see progress updates every 10-20%

### Error Handling Requirements
- Validate file types (PNG only)
- Check file size limits (max 10MB per frame)
- Handle API failures (Claude, Redis)
- Handle model errors (FILM crashes)
- Clean up temporary files on failure
- Provide user-friendly error messages

### Storage Management
- Each job uses ~100MB (2 keyframes + 8-16 output frames)
- Implement cleanup task for jobs older than 24 hours
- Store job metadata in Redis (expires after 24h)
- Consider disk space limits for personal use

---

## MVP Success Criteria

### Functional Requirements
- Successfully upload 2 PNG keyframes with transparency
- Parse natural language instructions with 90%+ accuracy on common phrases
- Generate intermediate frames without crashes
- Preserve transparency in all output frames
- Preview animation with play/pause and scrubbing
- Download frames as properly named ZIP
- Complete processing in under 3 minutes for 8 frames on CPU

### Quality Requirements
- Frames visually interpolate between keyframes (even if not hand-drawn style)
- Transparency edges remain clean (no artifacts)
- Frame numbering is consistent and importable to Procreate
- UI is intuitive for non-technical users
- Error messages are clear and actionable

### Performance Requirements
- Handle images up to 2000x2000px
- Process 4-32 frames per job
- Support concurrent job if needed (single user, unlikely)
- Frontend remains responsive during processing

---

## Known MVP Limitations

1. **No style preservation**: Frames will look interpolated/morphed, not hand-drawn
2. **CPU-only processing**: Slower than GPU (1-3 minutes vs 10-30 seconds)
3. **Single job processing**: Celery configured for one job at a time
4. **No batch mode**: Process one keyframe pair at a time
5. **No manual control**: Cannot adjust timing curves manually
6. **No frame editing**: Cannot modify individual generated frames
7. **No project persistence**: Jobs expire after 24 hours
8. **No Procreate integration**: Manual export/import workflow

---

## Development Phases

### Phase 0: Environment Setup ✅ COMPLETE
- Project structure created
- FILM model tested and working
- Claude API tested and working
- Docker infrastructure configured

### Phase 1: Core Backend Services ✅ COMPLETE
- Built `film_service.py` with image preprocessing
- Built `claude_service.py` with prompt engineering
- Defined Pydantic schemas
- Unit tested both services

### Phase 2: Task Queue & Job Processing 🔄 NEXT
- Setup Celery worker
- Implement `generate_frames` task
- Add progress tracking in Redis
- Error handling and cleanup

### Phase 3: FastAPI HTTP Layer
- Create FastAPI app with CORS
- Build `/api/generate`, `/api/jobs/{id}`, `/api/frames`, `/api/download`
- File upload validation
- ZIP generation

### Phase 4: Frontend Foundation
- Setup Next.js + TailwindCSS
- Build 4 main components (Uploader, Input, Timeline, Download)
- Mock data testing

### Phase 5: Frontend-Backend Integration
- Build API client (`api.ts`)
- Build job polling hook (`useJobStatus.ts`)
- Wire up complete user flow

### Phase 6: Polish & Error Handling
- User-friendly errors
- Loading states and animations
- Keyboard shortcuts
- Documentation

### Phase 7: Testing & Cleanup
- End-to-end testing
- Cleanup scripts (24h TTL)
- Performance testing
- Security audit

---

## Development Guidelines for AI Assistants

### Code Quality Standards

**Follow Clean Code Principles:**
- **Meaningful names**: Use descriptive variable, function, and class names
- **Single Responsibility**: Each function should do one thing well
- **DRY (Don't Repeat Yourself)**: Extract common logic into reusable functions
- **Small functions**: Keep functions focused and under 50 lines when possible
- **Clear comments**: Explain "why" not "what" - code should be self-documenting
- **Type hints**: Use Python type hints and TypeScript types everywhere
- **Error handling**: Use specific exceptions with clear messages

**Python Style:**
- Follow PEP 8 style guide
- Use type hints for all function signatures
- Prefer Pydantic models over raw dictionaries
- Use list comprehensions and generators where appropriate
- Avoid nested conditionals (early returns preferred)
- Use context managers (`with` statements) for file/resource handling

**TypeScript/React Style:**
- Use functional components with hooks
- Destructure props and state
- Use TypeScript interfaces for all data structures
- Prefer `const` over `let`, avoid `var`
- Use meaningful component names (PascalCase)
- Extract complex logic into custom hooks

### File Organization
- One class/component per file
- Group related functionality in modules
- Keep imports organized (stdlib, third-party, local)
- Use absolute imports where possible

### Testing Requirements
- Write unit tests for all services
- Test edge cases and error conditions
- Use descriptive test names: `test_should_handle_missing_alpha_channel`
- Mock external services (Claude API, Redis)
- Validate test data in `tests/` directory

### Git Workflow

**IMPORTANT: Do NOT commit changes automatically**

When you make changes:
1. ✅ Use `git add` to stage files
2. ✅ Show the user what will be committed with `git status` and `git diff --staged`
3. ❌ **NEVER** run `git commit` yourself
4. ❌ **NEVER** run `git push` yourself
5. ⏸️ **WAIT** for the user to review and commit manually

**Example workflow:**
```bash
# ✅ Stage changes
git add backend/app/services/new_service.py
git add backend/app/models/schemas.py

# ✅ Show what will be committed
git status
git diff --staged

# ⏸️ STOP HERE - tell user:
# "I've staged the changes. Please review with 'git diff --staged'
# and commit when ready."
```

**Commit Message Guidelines (for user reference):**
- Use present tense: "add feature" not "added feature"
- Be concise but descriptive
- Reference issue/phase numbers where applicable
- Format: `<type>: <description>` (e.g., `feat: add celery worker task`)

### Documentation
- Update relevant docs when changing functionality
- Keep this CLAUDE.md file updated with major changes
- Document complex algorithms inline
- Add docstrings to all public functions/classes

### Security Considerations
- Never log API keys or secrets
- Validate all user inputs (file types, sizes, content)
- Sanitize file paths to prevent directory traversal
- Use environment variables for all secrets
- Never commit `.env` file

---

## Common Commands

### Development
```bash
# Start Docker services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f celery_worker

# Restart service
docker-compose restart backend

# Stop all
docker-compose down

# Test FILM
source .venv/bin/activate
python tests/test_film_setup.py

# Test Claude
export ANTHROPIC_API_KEY="..."
python tests/test_claude_api.py

# Run service tests
python tests/test_services.py
```

### Backend Development
```bash
cd backend
source ../.venv/bin/activate

# Run FastAPI locally
uvicorn app.main:app --reload

# Run Celery worker locally
celery -A app.workers.celery_worker worker --loglevel=info
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev  # Starts on http://localhost:3000
```

---

## Quick Reference Links

- **FILM GitHub**: https://github.com/google-research/frame-interpolation
- **FILM TF Hub**: https://tfhub.dev/google/film/1
- **Claude API Docs**: https://docs.anthropic.com
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Celery Docs**: https://docs.celeryproject.org
- **Next.js Docs**: https://nextjs.org/docs

---

## Notes for AI Assistants

1. **Always read this file first** when starting work on this project
2. **Check [docs/ANIMATION_STYLE.md](./ANIMATION_STYLE.md)** for animation principles
3. **Review phase summaries** in docs/ to understand what's been completed
4. **Use test scripts** to validate changes (tests/test_*.py)
5. **Follow the development phases** - don't skip ahead
6. **Stage changes but don't commit** - let the user review and commit
7. **Ask for clarification** if requirements are ambiguous
8. **Update documentation** when making significant changes

---

**Last Updated**: Model Evaluation Phase - October 27, 2025
