# Claude Context File - Vizier Project
**AI-Assisted 2D Animation Inbetweening Tool**

> This file provides complete context for AI assistants when working on this project. Read this first to understand the project structure, current status, and development guidelines.

---

## Project Overview

**Name**: Vizier
**Purpose**: Help beginner artists create smooth 2D animations by auto-generating intermediate frames between keyframes
**Target User**: Artists using Procreate who struggle with manual inbetweening
**Current Status**: **Multi-Agent System Development** - Phase 0 complete, building intelligent principle-aware animation system

### What It Does
1. User uploads 2 PNG keyframes with transparency (Procreate exports)
2. User describes motion in natural language (e.g., "create 8 bouncy frames")
3. Multi-agent AI system analyzes motion and applies animation principles
4. Specialized agents plan, generate, validate, and refine frames
5. User downloads frames as ZIP → imports back to Procreate

### Animation Philosophy
Vizier supports **classic cel animation techniques** with physics-based interpolation. Objects should **move across the screen**, not fade in/out. See **[docs/ANIMATION_STYLE.md](./ANIMATION_STYLE.md)** for detailed animation principles and testing strategy.

---

## Current Project Status

### Completed Phases

[COMPLETE] **Phase 0: Environment Setup & Validation** (Archived - FILM approach)
- FILM model validated and working (archived approach)
- Claude API tested and working
- Docker infrastructure configured
- See [docs/film/PHASE_0_SUMMARY.md](./film/PHASE_0_SUMMARY.md) and [docs/film/PHASE_0_FINDINGS.md](./film/PHASE_0_FINDINGS.md)

[COMPLETE] **Phase 1: Core Backend Services** (Archived - FILM approach)
- Built `claude_service.py` with prompt engineering for NL parsing
- Defined Pydantic schemas for data validation
- Unit tests passing for Claude service
- Note: FILM service was discontinued in favor of Telekinesis agent loop
- See [docs/film/PHASE_1_SUMMARY.md](./film/PHASE_1_SUMMARY.md) for historical reference

[COMPLETE] **Phase 0: Telekinesis Multi-Agent Foundation** (NEW DIRECTION)
- Built LangGraph-based multi-agent system
- Created 6 specialized agent stubs (ANALYZER, PRINCIPLES, PLANNER, GENERATOR, VALIDATOR, REFINER)
- Defined AnimationState TypedDict for agent communication
- Implemented conditional routing and iteration logic
- Created Animation Principles Knowledge Base (12 principles)
- Infrastructure tests passing
- See [docs/PHASE_0_TELEKINESIS_SUMMARY.md](./PHASE_0_TELEKINESIS_SUMMARY.md)

[COMPLETE] **Phase 1: Telekinesis Minimal Viable Pipeline** (NEW DIRECTION)
- Implemented Claude Vision integration in ANALYZER agent
- Built object-based frame generation in GENERATOR agent
- Created FrameGeneratorService with color-based segmentation
- Full end-to-end pipeline execution working
- See [docs/PHASE_1_TELEKINESIS_SUMMARY.md](./PHASE_1_TELEKINESIS_SUMMARY.md)

### Current Status: Multi-Agent System Development

**NEW APPROACH**: Principle-Aware Animation System

After discovering limitations with naive frame interpolation, we've pivoted to a **multi-agent architecture** that understands and applies the **12 Principles of Animation**. Instead of treating animation as a pure computer vision problem, we now treat it as an animation problem solved by specialized AI agents.

**Key Innovation**: Rather than simple morphing/interpolation, the system:
- Analyzes what's actually moving between keyframes
- Determines which animation principles apply (arc, squash & stretch, timing, etc.)
- Plans frame-by-frame motion incorporating these principles
- Generates frames with structural guidance (ControlNet, pose estimation)
- Validates quality and adherence to principles
- Iteratively refines until quality threshold is met

**Architecture**: LangGraph-based agent loop with 6 specialized agents
- See [docs/TELEKINESIS_PLAN.md](./TELEKINESIS_PLAN.md) for complete system design
- See [docs/ANIMATION_PRINCIPLES_KNOWLEDGE_BASE.md](./ANIMATION_PRINCIPLES_KNOWLEDGE_BASE.md) for principle reference

**Current Phase**: Phase 0 Complete (Infrastructure) → Moving to Phase 1 (Minimal Viable Pipeline)

**Phase 1 Goals**:
- Implement basic Claude Vision analysis
- Add AnimateDiff frame generation
- End-to-end pipeline execution
- Quality will be rough, but demonstrates agent coordination

---

## Project Structure

```
vizier/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI entry point (to be created)
│   │   ├── services/
│   │   │   ├── claude_service.py      # [COMPLETE] Claude API client + prompt engineering
│   │   │   ├── claude_vision_service.py  # [COMPLETE] Claude Vision for image analysis
│   │   │   └── frame_generator_service.py  # [COMPLETE] Object-based frame interpolation
│   │   ├── telekinesis/               # [COMPLETE] Multi-agent animation system
│   │   │   ├── __init__.py            # Module exports
│   │   │   ├── state.py               # [COMPLETE] AnimationState TypedDict
│   │   │   ├── agents.py              # [COMPLETE] 6 agent stub functions
│   │   │   ├── graph.py               # [COMPLETE] LangGraph StateGraph with routing
│   │   │   └── logging_config.py      # [COMPLETE] Logging configuration
│   │   ├── workers/
│   │   │   └── celery_worker.py       # Async task: generate_frames() (to be created)
│   │   ├── models/
│   │   │   └── schemas.py             # [COMPLETE] Pydantic models (AnimationParams, JobStatus)
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
├── models/                            # Model storage (optional, for future use)
│
├── docs/                              # Documentation
│   ├── CLAUDE.md                      # This file - AI assistant context
│   ├── TELEKINESIS_PLAN.md            # [COMPLETE] CURRENT: Multi-agent system design and roadmap
│   ├── ANIMATION_PRINCIPLES_KNOWLEDGE_BASE.md  # [COMPLETE] CURRENT: 12 principles reference for agents
│   ├── PHASE_0_TELEKINESIS_SUMMARY.md # [COMPLETE] CURRENT: Phase 0 multi-agent infrastructure
│   ├── ANIMATION_STYLE.md             # [COMPLETE] CURRENT: Animation principles and testing strategy
│   └── film/                          # OLD: Previous FILM-based approach (archived)
│       ├── MODEL_COMPARISON_PLAN.md   # Model evaluation research (archived)
│       ├── PHASE_0_SUMMARY.md         # FILM validation results (archived)
│       ├── PHASE_0_FINDINGS.md        # FILM behavior analysis (archived)
│       └── PHASE_1_SUMMARY.md         # Services implementation (archived)
│
├── tests/                             # All test files
│   ├── test_claude_api.py             # Claude API test
│   ├── test_services.py               # Service unit tests (Claude service)
│   ├── test_telekinesis_phase0.py     # Telekinesis infrastructure tests
│   ├── test_telekinesis_phase1.py     # Telekinesis agent loop tests
│   ├── test_physics_interpolation.py  # Physics-based motion tests (archived)
│   ├── test_physics_with_background.py  # Background tests (archived)
│   ├── test_same_color_motion.py     # Motion tests (archived)
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
- **Multi-Agent System**: LangGraph + LangChain
- **Observability**: LangSmith (agent tracing and debugging)
- **AI Models**:
  - **Analysis & Reasoning**: Claude API (`claude-sonnet-4-5-20250929`)
  - **Frame Generation**: AnimateDiff (planned), ControlNet guidance
  - **Style Transfer**: Ebsynth (planned for refinement)
- **Image Processing**: Pillow, OpenCV, NumPy, MediaPipe (planned)

### Frontend
- **Framework**: Next.js 14 + React 18 + TypeScript
- **Styling**: TailwindCSS
- **HTTP**: Axios

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Storage**: Local filesystem (uploads/, outputs/)
- **Cache**: Redis 7

---

## Documentation Organization

**IMPORTANT**: The Vizier project has evolved through multiple approaches:

### Current Implementation (Top-Level Docs)
The following documents represent the **CURRENT** multi-agent system approach and should be followed for all development:
- **[TELEKINESIS_PLAN.md](./TELEKINESIS_PLAN.md)** - Complete system design and roadmap
- **[ANIMATION_PRINCIPLES_KNOWLEDGE_BASE.md](./ANIMATION_PRINCIPLES_KNOWLEDGE_BASE.md)** - 12 principles reference
- **[PHASE_0_TELEKINESIS_SUMMARY.md](./PHASE_0_TELEKINESIS_SUMMARY.md)** - Current phase status
- **[ANIMATION_STYLE.md](./ANIMATION_STYLE.md)** - Animation philosophy and testing strategy

### Archived Approaches (docs/film/)
The `docs/film/` directory contains documentation from a previous FILM-based interpolation approach that was **discontinued** due to technical limitations. These documents are archived for reference only:
- [FAILED] `film/MODEL_COMPARISON_PLAN.md` - Old model evaluation plan (not current)
- [FAILED] `film/PHASE_0_SUMMARY.md` - FILM validation (archived)
- [FAILED] `film/PHASE_0_FINDINGS.md` - FILM limitations analysis (archived)
- [FAILED] `film/PHASE_1_SUMMARY.md` - Old service implementation (archived)

**For AI Assistants**: Only implement features and follow plans from **top-level documentation**. Files in `docs/film/` are for historical reference only and should NOT guide current development.

---

## Multi-Agent System Architecture (Telekinesis)

### Overview

The Telekinesis system is a LangGraph-based multi-agent architecture that applies the **12 Principles of Animation** to generate intermediate frames. Rather than naive interpolation, specialized AI agents analyze, plan, generate, validate, and refine frames with deep understanding of animation fundamentals.

**Core Philosophy**: Treat animation as an animation problem, not just a computer vision problem.

### The 6 Agents

#### 1. ANALYZER Agent
**Purpose**: Understand what's changing between keyframes

**Responsibilities**:
- Visual analysis using Claude Vision
- Motion type detection (rotation, translation, deformation)
- Object segmentation and part identification
- Pose detection (MediaPipe for characters)
- Style analysis (line art, cel-shaded, realistic)
- Volume and structure measurement

**Output**: Analysis dictionary with motion characteristics, detected objects, and style information

#### 2. PRINCIPLES Agent
**Purpose**: Determine which of the 12 animation principles apply

**Responsibilities**:
- Analyze motion to identify relevant principles (arc, squash & stretch, timing, etc.)
- Assign confidence scores to each applicable principle
- Extract principle-specific parameters
- Reference Animation Principles Knowledge Base

**Output**: List of applicable principles with confidence scores, parameters, and reasoning

**The 12 Principles**:
1. Squash and Stretch
2. Anticipation
3. Staging
4. Straight Ahead Action and Pose to Pose
5. Follow Through and Overlapping Action
6. Slow In and Slow Out
7. Arc
8. Secondary Action
9. Timing
10. Exaggeration
11. Solid Drawing
12. Appeal

See [ANIMATION_PRINCIPLES_KNOWLEDGE_BASE.md](./ANIMATION_PRINCIPLES_KNOWLEDGE_BASE.md) for details.

#### 3. PLANNER Agent
**Purpose**: Create detailed frame-by-frame generation plan

**Responsibilities**:
- Generate timing curves based on principles (ease-in, ease-out, custom)
- Calculate arc paths for natural motion
- Plan deformation schedules (squash/stretch per frame)
- Design motion layers for overlapping action
- Determine ControlNet strategy (pose, line art, depth)
- Ensure volume preservation constraints

**Output**: Frame schedule with interpolation parameters, timing curves, and generation strategy

#### 4. GENERATOR Agent
**Purpose**: Create intermediate frames using generative models

**Responsibilities**:
- Execute AnimateDiff with ControlNet guidance
- Apply frame-by-frame deformations
- Generate motion layers separately for overlapping action
- Composite layers with timing offsets
- Preserve transparency from original keyframes

**Output**: List of generated frame image paths

#### 5. VALIDATOR Agent
**Purpose**: Assess quality and principle adherence

**Responsibilities**:
- Quality assessment using Claude Vision
- Volume consistency checking (OpenCV)
- Motion smoothness analysis (optical flow)
- Principle adherence validation (does motion follow planned arc?)
- Style consistency checking (CLIP/DINO features)
- Artifact detection (morphing, ghosting, distortion)

**Output**: Quality score (0-10), principle adherence scores, detected issues, refinement suggestions

**Routing Logic**:
- Quality ≥ 8.0 → END (success)
- Quality < 6.0 and iteration < 2 → REPLAN
- Quality ≥ 6.0 and iteration < 3 → REFINE
- Iteration ≥ 3 → END (accept best effort)

#### 6. REFINER Agent
**Purpose**: Fix specific issues identified by validator

**Responsibilities**:
- Ebsynth style transfer for consistency
- Inpainting for problem regions
- Temporal smoothing to reduce flicker
- Volume normalization
- Line art cleanup and weight adjustment
- Enhance subtle effects (squash/stretch, motion blur)

**Output**: List of refined frame image paths

### Agent Flow Diagram

```
START
  ↓
[ANALYZER] → analysis
  ↓           (What's moving? How?)
[PRINCIPLES] → animation_principles
  ↓             (Which principles apply?)
[PLANNER] → plan
  ↓          (Frame-by-frame motion plan)
[GENERATOR] → frames
  ↓            (Generate images)
[VALIDATOR] → validation
  ↓            (Quality check)
  ├─ quality ≥ 8.0 → END [DONE]
  ├─ quality ≥ 6.0 → [REFINER] → refined_frames → [VALIDATOR]
  └─ quality < 6.0 → [PLANNER] (re-plan)
```

### AnimationState

The state container passed between agents:

```python
class AnimationState(TypedDict):
    # Input
    keyframe1: str
    keyframe2: str
    instruction: str

    # Agent outputs
    analysis: dict
    animation_principles: dict
    plan: dict
    frames: List[str]
    validation: dict
    refined_frames: List[str]

    # Control flow
    iteration_count: int
    messages: List[dict]
```

See `backend/app/telekinesis/state.py` for full definition.

### Integration with Vizier

The Telekinesis system integrates into Vizier's Celery worker:

```python
@celery_app.task(bind=True)
def generate_frames_advanced(self, job_id, kf1, kf2, instruction):
    """Advanced generation using Telekinesis agent loop"""

    graph = build_telekinesis_graph()

    initial_state = {
        "keyframe1": kf1,
        "keyframe2": kf2,
        "instruction": instruction,
        "iteration_count": 0,
        "messages": []
    }

    # Stream execution with progress updates
    for state in graph.stream(initial_state):
        current_agent = list(state.keys())[0]
        self.update_state(
            state='PROGRESS',
            meta={'agent': current_agent, 'progress': calculate_progress(state)}
        )

    return state.get("refined_frames") or state.get("frames")
```

### Development Phases

**Phase 0: Foundation** [COMPLETE] COMPLETE
- LangGraph infrastructure
- Agent stubs
- State management
- Animation Principles Knowledge Base

**Phase 1: Minimal Viable Pipeline** [IN PROGRESS] NEXT
- Claude Vision analysis
- Hardcoded principles
- Simple linear planning
- AnimateDiff generation (no ControlNet)
- Stub validator (always passes)

**Phase 2: Add Vision Analysis**
- Real motion analysis
- Claude-based principle detection
- Incorporate principles into planning

**Phase 3: Add ControlNet Guidance**
- Structural control (pose + line art)
- Arc path calculations
- Timing curves

**Phase 4: Add Validation Loop**
- Real quality checking
- Refiner implementation
- Iterative improvement

**Phase 5: Advanced Principles**
- Squash/stretch deformation
- Overlapping action (motion layers)
- Full principle integration

**Phase 6: Optimization**
- Caching
- Parallel processing
- Cost reduction

---

## Key Technical Findings

### Telekinesis Agent Loop (Current Implementation)
- **Framework**: LangGraph + LangChain
- **Architecture**: 6 specialized agents (ANALYZER, PRINCIPLES, PLANNER, GENERATOR, VALIDATOR, REFINER)
- **State Management**: AnimationState TypedDict passed between agents
- **Routing**: Conditional routing based on validation quality scores
- **Current Phase**: Phase 0 Complete (Infrastructure), Phase 1 In Progress

### FrameGeneratorService (Phase 1)
- **Approach**: Object-based motion interpolation
- **Method**: Color-based segmentation to detect objects
- **Interpolation**: Position and color interpolation with easing curves
- **Limitations**: Works best with simple objects, will enhance with AnimateDiff in future phases
- **Transparency**: Full RGBA support, preserves alpha channel

### Claude API
- **Model**: `claude-sonnet-4-5-20250929`
- **Response Time**: ~1-2 seconds
- **Accuracy**: 100% on test cases
- **Cost**: ~$0.003 per request
- **Output**: Returns valid JSON when prompted correctly

### Prompt Caching
- **Implementation**: All Claude API calls use prompt caching for system prompts
- **Cache Control**: `cache_control: {"type": "ephemeral"}` on system prompts
- **Validation**: Strict enforcement that caching is working (errors if not cached)
- **Cost Savings**: ~90% reduction in token costs for repeated calls
- **Files**: `claude_service.py`, `claude_vision_service.py`

### LangSmith Tracing
- **Purpose**: Comprehensive observability of agent loop execution
- **Implementation**: `@traceable` decorator on `run_telekinesis_pipeline()` in `graph.py:130-188`
- **Metadata**: Job ID, instruction, and keyframe paths tagged per run
- **Configuration**: Environment variables in `.env.example`
- **Dependency**: `langsmith>=0.1.0` in `pyproject.toml`
- **Status**: [COMPLETE] Enabled in production (commit 603f974)

---

## Observability & Tracing

### LangSmith Integration

Vizier uses **LangSmith** for comprehensive observability of the Telekinesis agent loop execution. This enables debugging, performance monitoring, and understanding of complex multi-agent interactions.

**Features**:
- Automatic tracing of all agent executions
- Metadata tagging (job_id, instruction, keyframe paths)
- Hierarchical trace visualization showing agent flow
- Performance monitoring and timing analysis
- Error tracking and debugging support

**Setup**:
```bash
# In .env file
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_your_key_here
LANGCHAIN_PROJECT=vizier
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

**Implementation Details**:
- `@traceable` decorator applied to `run_telekinesis_pipeline()` function
- Metadata includes job context (job_id, instruction, keyframes)
- Tags include "telekinesis" and "job:{job_id}" for filtering
- Traces show complete agent execution flow with timing

**View Traces**:
Visit https://smith.langchain.com/projects/vizier after running tests or jobs

**Optional**: Set `LANGCHAIN_TRACING_V2=false` to disable tracing during development

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

**Claude Service:** [COMPLETE] IMPLEMENTED
- Parse natural language instructions
- Extract structured parameters (frame count, motion type, timing curve)
- Return JSON with animation specifications

**FrameGeneratorService:** [COMPLETE] IMPLEMENTED
- Object-based motion interpolation
- Detects objects using color segmentation
- Interpolates object position and color
- Renders objects at intermediate states
- Preserves transparency (alpha channel)

**Telekinesis Agent Loop:** [IN PROGRESS] Phase 0 Complete, Phase 1 In Progress
- Multi-agent system with 6 specialized agents
- Applies 12 Principles of Animation
- See [docs/TELEKINESIS_PLAN.md](./TELEKINESIS_PLAN.md) for details

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

### AnimationParams (Claude Output) [COMPLETE] IMPLEMENTED
```python
{
    "num_frames": int,           # 4-32
    "motion_type": str,          # "linear" | "ease-in" | "ease-out" | "ease-in-out" | "bounce" | "elastic"
    "speed": str,                # "very-slow" | "slow" | "normal" | "fast" | "very-fast"
    "emphasis": str,             # Brief description
    "interpolation_times": List[float]  # Optional: [0.0, 0.25, 0.5, 0.75, 1.0]
}
```

### JobStatus (API Response) [COMPLETE] IMPLEMENTED
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

    # Stage 2: Agent Loop Execution (30-90%)
    update_status(job_id, "analyzing", 30)
    # Build Telekinesis graph and execute agent loop
    graph = build_telekinesis_graph()
    initial_state = create_initial_state(
        keyframe1=frame1_path,
        keyframe2=frame2_path,
        instruction=instruction,
        job_id=job_id
    )
    
    # Stream execution with progress updates
    for state_update in graph.stream(initial_state):
        current_agent = list(state_update.keys())[0]
        progress = calculate_agent_progress(current_agent)
        update_status(job_id, f"agent_{current_agent}", progress)
    
    # Extract final frames from state
    final_state = state_update
    frames = final_state.get("refined_frames") or final_state.get("frames", [])
    update_status(job_id, "generating", 90)

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

### Phase 0: Environment Setup [COMPLETE] (Archived - FILM approach)
- Project structure created
- Claude API tested and working
- Docker infrastructure configured
- See [docs/film/PHASE_0_SUMMARY.md](./film/PHASE_0_SUMMARY.md) for historical reference

### Phase 1: Core Backend Services [COMPLETE] (Archived - FILM approach)
- Built `claude_service.py` with prompt engineering
- Defined Pydantic schemas
- Unit tested Claude service
- Note: FILM service discontinued in favor of Telekinesis
- See [docs/film/PHASE_1_SUMMARY.md](./film/PHASE_1_SUMMARY.md) for historical reference

### Phase 0: Telekinesis Multi-Agent Foundation [COMPLETE] COMPLETE (NEW)
- LangGraph infrastructure setup
- 6 agent stubs created (ANALYZER, PRINCIPLES, PLANNER, GENERATOR, VALIDATOR, REFINER)
- AnimationState TypedDict defined
- Conditional routing and iteration logic implemented
- Animation Principles Knowledge Base created
- Infrastructure tests passing

### Phase 1: Telekinesis Minimal Viable Pipeline [IN PROGRESS] NEXT (NEW)
- Implement Claude Vision analysis in ANALYZER
- Keep hardcoded principles in PRINCIPLES agent
- Simple linear planning in PLANNER
- AnimateDiff generation (no ControlNet yet)
- Stub validator (always passes)
- Goal: End-to-end execution with rough quality

### Phase 2: Telekinesis Vision Analysis (NEW)
- Real motion analysis
- Claude-based principle detection
- Incorporate principles into planning
- Goal: Intelligent principle identification

### Phase 3: Telekinesis ControlNet Guidance (NEW)
- Structural control (pose + line art)
- Arc path calculations
- Timing curves
- Goal: Frames maintain structure and follow natural motion

### Phase 4: Telekinesis Validation Loop (NEW)
- Real quality checking
- Refiner implementation
- Iterative improvement
- Goal: Self-correcting system with high quality output

### Phase 5: Telekinesis Advanced Principles (NEW)
- Squash/stretch deformation
- Overlapping action (motion layers)
- Full principle integration
- Goal: Professional quality animation

### Phase 6: Telekinesis Optimization (NEW)
- Caching
- Parallel processing
- Cost reduction
- Goal: Production-ready performance

### Future Phases: FastAPI HTTP Layer & Frontend
- Create FastAPI app with CORS
- Build `/api/generate`, `/api/jobs/{id}`, `/api/frames`, `/api/download`
- File upload validation
- Setup Next.js + TailwindCSS
- Build frontend components
- Wire up complete user flow

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
- **No emojis**: NEVER use emojis in code, comments, or documentation - use text markers instead ([COMPLETE], [IN PROGRESS], [WARNING], [FAILED], [X], [DONE])

**Python Style:**
- Follow PEP 8 style guide
- Use type hints for all function signatures
- Prefer Pydantic models over raw dictionaries
- Use list comprehensions and generators where appropriate
- Avoid nested conditionals (early returns preferred)
- Use context managers (`with` statements) for file/resource handling
- **NEVER use lazy imports**: All imports must be at the top of the file, never inside functions or methods
  - Lazy imports harm readability, break IDE support, complicate debugging, and provide no real performance benefit
  - All module dependencies should be explicit and visible at the top of the file

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
- **All imports at the top of the file** - never use lazy imports inside functions or methods

### Testing Requirements
- Write unit tests for all services
- Test edge cases and error conditions
- Use descriptive test names: `test_should_handle_missing_alpha_channel`
- Mock external services (Claude API, Redis)
- Validate test data in `tests/` directory

### Git Workflow

**IMPORTANT: Do NOT commit changes automatically**

When you make changes:
1. [COMPLETE] Use `git add` to stage files
2. [COMPLETE] Show the user what will be committed with `git status` and `git diff --staged`
3. [FAILED] **NEVER** run `git commit` yourself
4. [FAILED] **NEVER** run `git push` yourself
5. **WAIT** for the user to review and commit manually

**Example workflow:**
```bash
# [COMPLETE] Stage changes
git add backend/app/services/new_service.py
git add backend/app/models/schemas.py

# [COMPLETE] Show what will be committed
git status
git diff --staged

# STOP HERE - tell user:
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

# Test Telekinesis
source .venv/bin/activate
python tests/test_telekinesis_phase0.py
python tests/test_telekinesis_phase1.py

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

### Observability (LangSmith)
```bash
# Set up LangSmith tracing (optional)
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY="lsv2_pt_..."
export LANGCHAIN_PROJECT=vizier
export LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

# View traces in browser
open https://smith.langchain.com/projects/vizier

# Disable tracing for development
export LANGCHAIN_TRACING_V2=false
```

---

## Quick Reference Links

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **LangChain Docs**: https://python.langchain.com/
- **LangSmith Docs**: https://docs.smith.langchain.com/
- **Claude API Docs**: https://docs.anthropic.com
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Celery Docs**: https://docs.celeryproject.org
- **Next.js Docs**: https://nextjs.org/docs

---

## Notes for AI Assistants

1. **Always read this file first** when starting work on this project
2. **IMPORTANT: Only follow top-level docs** - Files in `docs/film/` are archived and NOT current
3. **Current system design**: See [TELEKINESIS_PLAN.md](./TELEKINESIS_PLAN.md) and [PHASE_0_TELEKINESIS_SUMMARY.md](./PHASE_0_TELEKINESIS_SUMMARY.md)
4. **Check [docs/ANIMATION_STYLE.md](./ANIMATION_STYLE.md)** for animation principles
5. **Use test scripts** to validate changes (tests/test_*.py)
6. **Follow the Telekinesis development phases** (Phase 0-6) - don't skip ahead
7. **Stage changes but don't commit** - let the user review and commit
8. **Ask for clarification** if requirements are ambiguous
9. **Update documentation** when making significant changes
10. **NEVER use emojis** - Use text markers: [COMPLETE], [IN PROGRESS], [WARNING], [FAILED], [X], [DONE]

---

**Last Updated**: Multi-Agent System Development (Phase 0 Complete) - October 30, 2025
