# Phase 3: RIFE Integration & Arc Path Warping - PLAN

**Date**: December 10, 2025
**Status**: Planning
**Branch**: `phase3-rife-arc-paths`
**Previous Phase**: Phase 2 - Intelligent Principle Detection (COMPLETE)

---

## Executive Summary

Phase 3 replaces the simple object-based interpolation with a **hybrid RIFE + arc path warping** approach that delivers production-quality frame interpolation on CPU while respecting animation principles.

**Key Innovation**: Instead of AnimateDiff (requires GPU), we use:
1. **RIFE** for high-quality base frame interpolation
2. **Arc path warping** to apply curved motion paths
3. **Timing redistribution** to honor easing curves from principles
4. **Real VALIDATOR** using Claude Vision for quality assessment

---

## Goals

1. [TODO] Integrate RIFE model for base frame generation
2. [TODO] Implement arc path calculation in PLANNER
3. [TODO] Apply arc path warping in GENERATOR
4. [TODO] Implement real quality validation with Claude Vision
5. [TODO] Enable the refinement loop (VALIDATOR → REFINER routing)
6. [TODO] Test with multiple motion types

---

## Architecture Overview

### Current Pipeline (Phase 2)

```
ANALYZER → PRINCIPLES → PLANNER → GENERATOR → VALIDATOR → END
                                     ↓
                          (object-based interpolation)
                          (straight line motion only)
```

### Phase 3 Pipeline

```
ANALYZER → PRINCIPLES → PLANNER → GENERATOR → VALIDATOR ─┐
                           ↓           ↓           ↓      │
                    (arc path calc) (RIFE +    (Claude    │
                                    arc warp)  Vision)    │
                                                          │
              ┌───────────────────────────────────────────┘
              │
              ├─ quality >= 8.0 → END [DONE]
              │
              ├─ quality >= 6.0 → REFINER → VALIDATOR (loop)
              │                      ↓
              │              (temporal smoothing,
              │               artifact cleanup)
              │
              └─ quality < 6.0 → PLANNER (replan with feedback)
```

---

## Component Design

### 1. RIFE Service

**New File**: `backend/app/services/rife_service.py`

**Purpose**: Generate high-quality intermediate frames using RIFE neural interpolation

**RIFE Model Selection**: `rife-ncnn-vulkan` or `practical-rife`
- CPU-compatible (uses ncnn or ONNX runtime)
- ~2-5 seconds per frame on modern CPU
- Handles complex shapes, textures, motion blur
- Recursive interpolation: 2 frames → 3 → 5 → 9 → 17...

**Interface**:
```python
class RifeService:
    def __init__(self, model_path: str = None):
        """Initialize RIFE model (downloads if needed)"""

    def interpolate(
        self,
        frame1: np.ndarray,  # RGBA uint8
        frame2: np.ndarray,  # RGBA uint8
        t: float = 0.5       # Interpolation factor (0-1)
    ) -> np.ndarray:
        """Generate single intermediate frame at position t"""

    def interpolate_sequence(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray,
        num_frames: int,
        t_values: List[float] = None  # Custom t values (for easing)
    ) -> List[np.ndarray]:
        """Generate multiple frames with custom timing"""

    def recursive_interpolate(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray,
        depth: int = 3  # 2^depth + 1 frames
    ) -> List[np.ndarray]:
        """Recursive doubling: 2→3→5→9→17 frames"""
```

**Implementation Strategy**:

Option A: **rife-ncnn-vulkan** (Recommended)
- Pre-compiled binary, very fast
- Works on CPU via Vulkan simulation
- ~1-3 sec/frame
- Download from: https://github.com/nihui/rife-ncnn-vulkan

Option B: **practical-rife** (Python native)
- Pure Python/PyTorch
- Slower on CPU (~5-10 sec/frame)
- Easier to integrate and modify
- pip installable

**Recommendation**: Start with rife-ncnn-vulkan for speed, fall back to Python RIFE if issues.

---

### 2. Arc Path Calculator

**Location**: `backend/app/telekinesis/agents.py` (planner_agent enhancement)

**Purpose**: Calculate curved motion paths based on arc principles

**Arc Types**:
1. **Linear** (no arc): Straight line A→B
2. **Parabolic**: Natural gravity arc (jumping, bouncing)
3. **Circular**: Pendulum, swinging motion
4. **Elliptical**: Head turns, arm rotations
5. **S-Curve**: Complex reversing motion

**Interface**:
```python
def calculate_arc_path(
    start_pos: Tuple[float, float],   # (x1, y1)
    end_pos: Tuple[float, float],     # (x2, y2)
    arc_type: str,                     # "parabolic", "circular", etc.
    arc_intensity: float,              # 0.0-1.0 (how curved)
    t: float                           # Interpolation parameter (0-1)
) -> Tuple[float, float]:
    """Returns (x, y) position along arc at parameter t"""
```

**Arc Implementations**:

```python
# Parabolic arc (gravity, bouncing)
def parabolic_arc(x1, y1, x2, y2, intensity, t):
    # Linear interpolation for x
    x = lerp(x1, x2, t)
    # Parabolic curve for y (peaks at t=0.5)
    y_linear = lerp(y1, y2, t)
    # Arc height proportional to distance and intensity
    arc_height = abs(x2 - x1) * intensity * 0.3
    y_offset = -4 * arc_height * t * (1 - t)  # Parabola
    y = y_linear + y_offset
    return (x, y)

# Circular arc (pendulum)
def circular_arc(x1, y1, x2, y2, intensity, t):
    # Find midpoint and radius
    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
    distance = sqrt((x2-x1)**2 + (y2-y1)**2)

    # Arc bulges perpendicular to line
    angle_start = atan2(y1 - mid_y, x1 - mid_x)
    angle_end = atan2(y2 - mid_y, x2 - mid_x)

    # Interpolate angle
    angle = lerp(angle_start, angle_end, t)
    radius = distance / 2 * (1 + intensity * 0.5)

    x = mid_x + radius * cos(angle)
    y = mid_y + radius * sin(angle)
    return (x, y)

# Elliptical arc (rotation)
def elliptical_arc(x1, y1, x2, y2, intensity, t):
    # Similar to circular but with different x/y radii
    # Used for head turns, arm swings
    ...
```

**Integration with PLANNER**:

```python
def planner_agent(state: AnimationState) -> AnimationState:
    # ... existing logic ...

    # NEW: Calculate arc positions for each frame
    if arc_type != "none" and arc_intensity > 0:
        # Get object positions from analysis
        # (requires ANALYZER to detect object centroids)
        start_pos = state["analysis"].get("object_position_start", (0.5, 0.5))
        end_pos = state["analysis"].get("object_position_end", (0.5, 0.5))

        for frame in frame_schedule:
            t = frame["t"]  # Already eased
            arc_x, arc_y = calculate_arc_path(
                start_pos, end_pos, arc_type, arc_intensity, t
            )
            frame["arc_position"] = {"x": arc_x, "y": arc_y}
```

---

### 3. Arc Path Warping

**Location**: `backend/app/services/frame_generator_service.py` (enhancement)

**Purpose**: Warp RIFE-generated frames to follow arc paths

**Strategy**:

RIFE generates frames assuming linear motion. To apply arc paths:

1. **Object Detection**: Find primary object in each RIFE frame
2. **Current Position**: Detect where object currently is (centroid)
3. **Target Position**: Where object should be (from arc path)
4. **Translation**: Shift object to target position
5. **Optional**: Apply rotation if arc implies it

**Interface**:
```python
def apply_arc_warp(
    frame: np.ndarray,           # RIFE output frame (RGBA)
    current_pos: Tuple[float, float],  # Where object is
    target_pos: Tuple[float, float],   # Where it should be (from arc)
    rotation: float = 0.0        # Optional rotation (degrees)
) -> np.ndarray:
    """Warp frame to move object from current_pos to target_pos"""
```

**Implementation**:

```python
def apply_arc_warp(frame, current_pos, target_pos, rotation=0.0):
    """
    Simple translation warp for arc path following.

    For simple cases: Just translate the whole frame.
    For complex cases: Segment object and translate only that.
    """
    # Calculate offset
    dx = target_pos[0] - current_pos[0]
    dy = target_pos[1] - current_pos[1]

    # Convert to pixel space
    h, w = frame.shape[:2]
    dx_px = int(dx * w)
    dy_px = int(dy * h)

    # Create translation matrix
    M = np.float32([
        [1, 0, dx_px],
        [0, 1, dy_px]
    ])

    # Apply affine transform
    warped = cv2.warpAffine(
        frame, M, (w, h),
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0)  # Transparent border
    )

    # Optional rotation around object center
    if rotation != 0:
        center = (int(target_pos[0] * w), int(target_pos[1] * h))
        R = cv2.getRotationMatrix2D(center, rotation, 1.0)
        warped = cv2.warpAffine(warped, R, (w, h))

    return warped
```

**Advanced Warping** (if simple translation insufficient):

```python
def apply_arc_warp_with_segmentation(frame, object_mask, target_pos):
    """
    More sophisticated: Only move the object, leave background.

    1. Segment object from background
    2. Translate object to target position
    3. Composite back onto background
    """
    # Separate foreground and background
    fg = frame.copy()
    fg[~object_mask] = [0, 0, 0, 0]

    bg = frame.copy()
    bg[object_mask] = [0, 0, 0, 0]

    # Translate only foreground
    fg_warped = translate_image(fg, target_pos)

    # Composite
    result = composite_over(fg_warped, bg)
    return result
```

---

### 4. Enhanced GENERATOR Agent

**Location**: `backend/app/telekinesis/agents.py` (generator_agent)

**Phase 3 Implementation**:

```python
def generator_agent(state: AnimationState) -> AnimationState:
    """
    Phase 3: RIFE + Arc Path Warping

    1. Use RIFE to generate base interpolated frames
    2. Apply arc path warping to each frame
    3. Save frames with transparency preserved
    """
    keyframe1 = state["keyframe1"]
    keyframe2 = state["keyframe2"]
    plan = state["plan"]
    job_id = state.get("job_id", "default")

    # Initialize services
    rife = RifeService()

    # Load keyframes
    kf1 = load_image(keyframe1)  # RGBA numpy array
    kf2 = load_image(keyframe2)

    # Get frame schedule with arc positions
    frame_schedule = plan["frame_schedule"]
    t_values = [f["t"] for f in frame_schedule]

    # Generate base frames with RIFE
    # RIFE uses eased t values from PLANNER
    base_frames = rife.interpolate_sequence(kf1, kf2, len(t_values), t_values)

    # Apply arc path warping if needed
    arc_type = plan.get("arc_type", "none")
    if arc_type != "none":
        warped_frames = []
        for i, (frame, schedule) in enumerate(zip(base_frames, frame_schedule)):
            arc_pos = schedule.get("arc_position", {})
            if arc_pos:
                # Detect current object position in RIFE frame
                current_pos = detect_object_centroid(frame)
                target_pos = (arc_pos["x"], arc_pos["y"])

                # Warp to arc path
                warped = apply_arc_warp(frame, current_pos, target_pos)
                warped_frames.append(warped)
            else:
                warped_frames.append(frame)
        frames = warped_frames
    else:
        frames = base_frames

    # Save frames
    output_dir = f"outputs/{job_id}"
    os.makedirs(output_dir, exist_ok=True)

    frame_paths = []
    for i, frame in enumerate(frames):
        path = f"{output_dir}/frame_{i:03d}.png"
        save_image(frame, path)
        frame_paths.append(path)

    state["frames"] = frame_paths
    state["messages"].append({
        "agent": "GENERATOR",
        "action": f"Generated {len(frames)} frames with RIFE + arc warping",
        "_phase": 3,
        "_status": "rife_arc_warp"
    })

    return state
```

---

### 5. Real VALIDATOR Agent

**Location**: `backend/app/telekinesis/agents.py` (validator_agent)

**Purpose**: Actually assess quality using Claude Vision

**What to Validate**:
1. **Motion Smoothness**: Do frames transition smoothly?
2. **Arc Adherence**: Does motion follow the planned arc?
3. **Volume Consistency**: Do objects maintain size/shape?
4. **Artifact Detection**: Ghosting, tearing, morphing artifacts?
5. **Style Consistency**: Does art style remain consistent?

**Implementation**:

```python
def validator_agent(state: AnimationState) -> AnimationState:
    """
    Phase 3: Real validation using Claude Vision

    Assesses quality across multiple dimensions and provides
    actionable feedback for REFINER.
    """
    frames = state["frames"]
    keyframe1 = state["keyframe1"]
    keyframe2 = state["keyframe2"]
    plan = state["plan"]

    # Sample frames for validation (don't send all to save cost)
    # First, middle, last, and 2 random
    sample_indices = [0, len(frames)//4, len(frames)//2, 3*len(frames)//4, -1]
    sample_frames = [frames[i] for i in sample_indices if i < len(frames)]

    # Use Claude Vision to assess
    validation = claude_vision_validate(
        keyframe1=keyframe1,
        keyframe2=keyframe2,
        sample_frames=sample_frames,
        plan=plan
    )

    # Structure validation result
    state["validation"] = {
        "overall_quality_score": validation["score"],  # 0-10
        "motion_smoothness": validation["smoothness"],  # 0-10
        "arc_adherence": validation["arc_adherence"],  # 0-10
        "volume_consistency": validation["volume"],  # 0-10
        "artifact_score": validation["artifacts"],  # 0-10 (higher = fewer)
        "style_consistency": validation["style"],  # 0-10
        "issues": validation["issues"],  # List of specific problems
        "suggestions": validation["suggestions"],  # How to fix
        "needs_refinement": validation["score"] < 8.0,
        "_phase": 3,
        "_status": "claude_vision_validated"
    }

    state["messages"].append({
        "agent": "VALIDATOR",
        "action": f"Quality score: {validation['score']:.1f}/10",
        "issues": len(validation["issues"])
    })

    return state
```

**Claude Vision Validation Service**:

```python
def claude_vision_validate(keyframe1, keyframe2, sample_frames, plan):
    """
    Use Claude Vision to assess animation quality.
    """
    # Encode images
    images = [
        encode_image(keyframe1),  # Reference start
        *[encode_image(f) for f in sample_frames],
        encode_image(keyframe2),  # Reference end
    ]

    prompt = f"""
    Analyze this animation sequence for quality. The sequence should
    interpolate from the first image to the last image.

    Planned motion:
    - Arc type: {plan.get('arc_type', 'none')}
    - Timing curve: {plan.get('timing_curve', 'linear')}
    - Frame count: {plan.get('num_frames', 8)}

    Score each dimension 0-10 (10 = perfect):

    1. Motion Smoothness: Do frames flow naturally?
    2. Arc Adherence: Does motion follow the expected path?
    3. Volume Consistency: Do objects maintain size/shape?
    4. Artifacts: Any ghosting, tearing, or morphing issues?
    5. Style Consistency: Does art style remain consistent?

    Return JSON:
    {{
        "score": <overall 0-10>,
        "smoothness": <0-10>,
        "arc_adherence": <0-10>,
        "volume": <0-10>,
        "artifacts": <0-10, higher=fewer artifacts>,
        "style": <0-10>,
        "issues": ["list of specific problems"],
        "suggestions": ["list of fixes"]
    }}
    """

    # Call Claude with images
    response = claude_client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        system=[{
            "type": "text",
            "text": VALIDATION_SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"}
        }],
        messages=[{
            "role": "user",
            "content": [
                *[{"type": "image", "source": img} for img in images],
                {"type": "text", "text": prompt}
            ]
        }]
    )

    return parse_json_response(response)
```

---

### 6. REFINER Agent (Basic Implementation)

**Location**: `backend/app/telekinesis/agents.py` (refiner_agent)

**Purpose**: Fix specific issues identified by VALIDATOR

**Phase 3 Scope** (basic refinement):
1. **Temporal Smoothing**: Reduce frame-to-frame jitter
2. **Alpha Cleanup**: Fix transparency edge artifacts
3. **Color Consistency**: Normalize color shifts

**Future Phases**: Ebsynth style transfer, inpainting, advanced fixes

```python
def refiner_agent(state: AnimationState) -> AnimationState:
    """
    Phase 3: Basic refinement based on validator feedback

    - Temporal smoothing (reduce jitter)
    - Alpha channel cleanup
    - Color normalization
    """
    frames = state["frames"]
    validation = state["validation"]
    issues = validation.get("issues", [])

    refined_frames = []

    # Load all frames
    frame_arrays = [load_image(f) for f in frames]

    # Apply temporal smoothing if motion not smooth
    if validation.get("motion_smoothness", 10) < 7:
        frame_arrays = temporal_smooth(frame_arrays, kernel_size=3)

    # Fix alpha edges if artifacts detected
    if validation.get("artifact_score", 10) < 7:
        frame_arrays = [cleanup_alpha_edges(f) for f in frame_arrays]

    # Color normalization if style inconsistent
    if validation.get("style_consistency", 10) < 7:
        frame_arrays = normalize_colors(frame_arrays, frames[0], frames[-1])

    # Save refined frames
    job_id = state.get("job_id", "default")
    output_dir = f"outputs/{job_id}"

    for i, frame in enumerate(frame_arrays):
        path = f"{output_dir}/refined_frame_{i:03d}.png"
        save_image(frame, path)
        refined_frames.append(path)

    state["refined_frames"] = refined_frames
    state["iteration_count"] = state.get("iteration_count", 0) + 1

    state["messages"].append({
        "agent": "REFINER",
        "action": f"Refined {len(refined_frames)} frames",
        "fixes_applied": ["temporal_smooth", "alpha_cleanup", "color_norm"],
        "_phase": 3
    })

    return state


def temporal_smooth(frames, kernel_size=3):
    """
    Apply temporal smoothing to reduce jitter.
    Simple approach: weighted average of adjacent frames.
    """
    smoothed = []
    n = len(frames)

    for i in range(n):
        # Weighted average of nearby frames
        weights = []
        neighbors = []

        for j in range(max(0, i - kernel_size//2), min(n, i + kernel_size//2 + 1)):
            weight = 1.0 - abs(j - i) / (kernel_size // 2 + 1)
            weights.append(weight)
            neighbors.append(frames[j])

        # Normalize weights
        total = sum(weights)
        weights = [w / total for w in weights]

        # Weighted average
        result = np.zeros_like(frames[i], dtype=np.float32)
        for w, f in zip(weights, neighbors):
            result += w * f.astype(np.float32)

        smoothed.append(result.astype(np.uint8))

    return smoothed
```

---

## Implementation Plan

### Step 1: RIFE Service Setup (2-3 hours)

1. Research RIFE options (rife-ncnn-vulkan vs practical-rife)
2. Create `rife_service.py` with model loading
3. Implement `interpolate()` method
4. Implement `interpolate_sequence()` with custom t values
5. Test standalone RIFE interpolation
6. Handle transparency (RIFE typically RGB only)

**Deliverable**: Working RIFE service that generates smooth frames

### Step 2: Arc Path Calculator (1-2 hours)

1. Implement `calculate_arc_path()` function
2. Add parabolic, circular, elliptical arc types
3. Update PLANNER to populate `arc_position` in frame schedule
4. Test arc calculations independently

**Deliverable**: PLANNER outputs valid arc positions

### Step 3: Arc Path Warping (2-3 hours)

1. Implement `apply_arc_warp()` function
2. Add object centroid detection for RIFE frames
3. Integrate warping into GENERATOR
4. Test with various arc types

**Deliverable**: Frames follow curved paths

### Step 4: GENERATOR Integration (2-3 hours)

1. Update generator_agent to use RIFE
2. Add arc path warping pipeline
3. Handle transparency throughout
4. Fallback to Phase 1 method if RIFE fails
5. Test end-to-end generation

**Deliverable**: GENERATOR produces RIFE + arc warped frames

### Step 5: Real VALIDATOR (2-3 hours)

1. Create validation service with Claude Vision
2. Implement quality scoring across dimensions
3. Update validator_agent to use real validation
4. Test validation on good and bad frames

**Deliverable**: VALIDATOR provides meaningful scores

### Step 6: REFINER Implementation (1-2 hours)

1. Implement temporal smoothing
2. Implement alpha cleanup
3. Implement color normalization
4. Update refiner_agent
5. Test refinement loop

**Deliverable**: Working refinement with basic fixes

### Step 7: Integration & Testing (2-3 hours)

1. End-to-end pipeline test
2. Test routing (VALIDATOR → REFINER → VALIDATOR)
3. Test multiple motion types
4. Create test_telekinesis_phase3.py
5. Update documentation

**Deliverable**: Complete Phase 3 implementation

---

## Dependencies to Add

```toml
# pyproject.toml additions

# RIFE - choose one:
# Option A: rife-ncnn-vulkan (binary, install separately)
# Option B: practical-rife (Python)
"torch>=2.0.0",
"torchvision>=0.15.0",

# Already installed but confirm versions:
"opencv-python-headless>=4.10.0",
"numpy>=2.2.0",
"Pillow>=11.0.0",
```

**Note**: RIFE model files (~100MB) will be downloaded on first use.

---

## Files to Create/Modify

### New Files

1. `backend/app/services/rife_service.py` - RIFE integration
2. `backend/app/services/validation_service.py` - Claude Vision validation
3. `tests/test_telekinesis_phase3.py` - Phase 3 tests
4. `docs/PHASE_3_TELEKINESIS_SUMMARY.md` - Completion summary

### Modified Files

1. `backend/app/telekinesis/agents.py`:
   - Update `planner_agent()` with arc path calculation
   - Update `generator_agent()` with RIFE + arc warping
   - Update `validator_agent()` with real validation
   - Update `refiner_agent()` with basic refinement

2. `backend/app/services/frame_generator_service.py`:
   - Add `apply_arc_warp()` function
   - Add `detect_object_centroid()` function

3. `pyproject.toml`:
   - Add torch/torchvision dependencies

4. `docs/CLAUDE.md`:
   - Update phase status
   - Add Phase 3 documentation

---

## Success Criteria

### Phase 3 Complete When:

- [ ] RIFE generates smooth intermediate frames
- [ ] Arc paths are calculated based on motion type
- [ ] Frames follow curved paths (not straight lines)
- [ ] VALIDATOR provides real quality scores
- [ ] Refinement loop executes when quality < 8.0
- [ ] End-to-end pipeline works with routing
- [ ] Test script validates all functionality
- [ ] Documentation updated

### Quality Expectations

**Expected**:
- Smooth frame transitions (RIFE quality)
- Natural curved motion for arc-type motions
- Quality scores reflect actual frame quality
- Basic refinement improves scores by 0.5-1.5 points

**Not Yet** (Future Phases):
- Squash/stretch deformation (Phase 5)
- Style transfer refinement (Phase 4+)
- Multi-object scenes (Phase 4+)
- Complex pose preservation (Phase 4+)

---

## Risk Assessment

### Technical Risks

1. **RIFE Performance on CPU**
   - Risk: Too slow (>10s per frame)
   - Mitigation: Use rife-ncnn-vulkan, reduce resolution, or accept longer times
   - Fallback: Keep Phase 1 interpolation as option

2. **RIFE Transparency Handling**
   - Risk: RIFE outputs RGB, loses alpha channel
   - Mitigation: Extract alpha from keyframes, composite back
   - Alternative: Pre-multiply alpha, post-process

3. **Arc Warping Artifacts**
   - Risk: Translation creates visible seams
   - Mitigation: Use feathered edges, blend regions
   - Alternative: Simpler arc influence (blend positions, not hard warp)

4. **Claude Vision Validation Cost**
   - Risk: High API costs if validating every job
   - Mitigation: Sample frames (5 of N), cache prompts
   - Budget: ~$0.02-0.05 per validation

### Contingency Plans

1. If RIFE too slow → Use half resolution, or keep Phase 1 for "fast" mode
2. If arc warping fails → Disable arc warping, just use easing curves
3. If validation unreliable → Use simpler heuristics (optical flow smoothness)

---

## Estimated Timeline

| Step | Description | Hours |
|------|-------------|-------|
| 1 | RIFE Service Setup | 2-3 |
| 2 | Arc Path Calculator | 1-2 |
| 3 | Arc Path Warping | 2-3 |
| 4 | GENERATOR Integration | 2-3 |
| 5 | Real VALIDATOR | 2-3 |
| 6 | REFINER Implementation | 1-2 |
| 7 | Integration & Testing | 2-3 |
| **Total** | | **12-19** |

**Estimated Completion**: 2-3 focused sessions

---

## Questions for Confirmation

Before implementation, please confirm:

1. **RIFE Approach**: Start with rife-ncnn-vulkan binary or Python practical-rife?
   - Recommended: rife-ncnn-vulkan for speed

2. **Arc Complexity**: Implement all arc types (parabolic, circular, elliptical) or start with one?
   - Recommended: Start with parabolic, add others incrementally

3. **Validation Frequency**: Validate every job or only on user request?
   - Recommended: Every job (enables refinement loop)

4. **Refinement Scope**: Basic fixes (smoothing, alpha, color) sufficient for Phase 3?
   - Recommended: Yes, save Ebsynth for Phase 4

---

## Next Steps

1. Review and approve this plan
2. Decide on RIFE implementation approach
3. Begin Step 1: RIFE Service Setup

---

**Phase 3 Status**: PLANNING

**Ready to Implement**: Awaiting approval
