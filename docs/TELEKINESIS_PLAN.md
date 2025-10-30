# Telekinesis: Animation Principles-Driven Agent Loop

**Status**: Planning Phase
**Created**: October 29, 2025
**Purpose**: Multi-agent system that understands the 12 principles of animation to intelligently interpolate between keyframe images

---

## Executive Summary

Telekinesis is an advanced multi-agent system that goes beyond simple frame interpolation by understanding and applying the **12 Principles of Animation** (Disney's foundational animation theory). Rather than generating frames through basic morphing or optical flow, this system uses a LangGraph-based agent loop where specialized AI agents analyze, plan, generate, validate, and refine animation frames with deep understanding of animation fundamentals.

**Key Innovation**: Instead of treating animation as a computer vision problem, we treat it as an animation problem - applying classical animation theory through AI agents.

---

## The 12 Principles of Animation

These principles, developed by Disney animators Ollie Johnston and Frank Thomas, form the foundation of Telekinesis:

### 1. **Squash and Stretch**
- Defines rigidity and mass of objects
- Objects deform during motion (compress on impact, stretch during fast movement)
- Maintains volume consistency

### 2. **Anticipation**
- Preparation before main action
- Helps audience prepare for major movements
- Example: Crouch before jump, wind-up before throw

### 3. **Staging**
- Clear presentation of ideas
- Directs attention to what's important
- Ensures key actions are visible and unmistakable

### 4. **Straight Ahead Action vs Pose to Pose**
- Straight Ahead: Draw frame by frame from start to finish
- Pose to Pose: Draw key poses, then fill in between (what we're doing)
- Telekinesis uses pose-to-pose with intelligent inbetweening

### 5. **Follow Through and Overlapping Action**
- Different parts move at different rates
- Nothing stops all at once
- Hair, clothing, appendages continue moving after main body stops

### 6. **Slow In and Slow Out**
- Actions start and end gradually
- More frames near extremes of motion
- Creates natural acceleration/deceleration (easing)

### 7. **Arc**
- Most natural motion follows arcs, not straight lines
- Heads turn in arcs, arms swing in arcs
- Even linear translations often have subtle arcs

### 8. **Secondary Action**
- Supporting actions that emphasize main action
- Tail wagging while dog walks, facial expressions during speech
- Must not distract from primary action

### 9. **Timing**
- Number of frames determines speed and weight
- Heavy objects: slow, gradual acceleration
- Light objects: quick, snappy movements

### 10. **Exaggeration**
- Push reality for dramatic effect
- Too realistic can be stiff and boring
- Find sweet spot between realism and cartoon

### 11. **Solid Drawing**
- Forms have volume, weight, balance
- Understand 3D space even in 2D
- Maintain consistent volume and proportions

### 12. **Appeal**
- Characters/objects should be pleasing to look at
- Clear design, readable silhouettes
- Charisma and charm in movement

---

## System Architecture

### LangGraph State Machine

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Annotated
import operator

class AnimationState(TypedDict):
    # Input
    keyframe1: str  # Path to first keyframe
    keyframe2: str  # Path to second keyframe
    instruction: str  # Natural language instruction

    # Agent outputs
    analysis: dict  # Visual and motion analysis
    animation_principles: dict  # Which principles apply
    plan: dict  # Frame generation plan
    frames: List[str]  # Generated frame paths
    validation: dict  # Quality assessment
    refined_frames: List[str]  # Post-refinement frames

    # Control flow
    iteration_count: int
    messages: Annotated[List[dict], operator.add]
```

---

## Agent Definitions

### 1. ANALYZER AGENT

**Purpose**: Understand what's changing between keyframes and identify relevant animation principles

**Tools**:
- `claude_vision_analyze()` - Deep visual understanding using Claude Vision
- `mediapipe_detect_pose()` - Detect human/character poses and landmarks
- `opencv_extract_lines()` - Extract line art and structural features
- `calculate_motion_diff()` - Compute motion magnitude and direction
- `segment_objects()` - Identify and segment moving objects
- `analyze_volume()` - Check object volume/size consistency

**Input**: keyframe1, keyframe2, instruction

**Output**:
```python
analysis = {
    "motion_type": str,  # "translation", "rotation", "deformation", "transformation"
    "primary_subject": str,  # Description of main moving subject
    "parts_moved": List[str],  # ["head", "left_arm", "torso"]
    "motion_magnitude": dict,  # {"translation": 150px, "rotation": 45deg}
    "motion_direction": dict,  # {"angle": 45, "arc_detected": True}
    "style": str,  # "line_art", "cel_shaded", "painted", "realistic"
    "pose_data": dict,  # MediaPipe skeleton data
    "object_segments": List[dict],  # Segmented objects with masks
    "color_palette": List[str],  # Dominant colors
    "volume_analysis": dict  # Volume measurements per object
}
```

**Next**: → PRINCIPLES AGENT

---

### 2. PRINCIPLES AGENT

**Purpose**: Determine which of the 12 animation principles apply to this specific motion

**Tools**:
- `claude_analyze_principles()` - Reason about which principles are relevant
- `detect_squash_stretch()` - Check if objects should deform
- `detect_anticipation_need()` - Check if anticipation would help
- `detect_arc_motion()` - Identify if motion follows natural arcs
- `analyze_timing_needs()` - Determine speed/weight characteristics
- `check_overlapping_parts()` - Identify parts that need follow-through

**Input**: analysis, instruction

**Output**:
```python
animation_principles = {
    "applicable_principles": [
        {
            "principle": "arc",
            "confidence": 0.95,
            "reason": "Character head rotates 45 degrees - natural arc motion",
            "parameters": {"arc_curve": "ease-out", "apex_position": 0.4}
        },
        {
            "principle": "slow_in_slow_out",
            "confidence": 0.9,
            "reason": "Heavy object movement requires gradual acceleration",
            "parameters": {"ease_in": 0.3, "ease_out": 0.5}
        },
        {
            "principle": "follow_through",
            "confidence": 0.85,
            "reason": "Hair and clothing should continue moving after body stops",
            "parameters": {"parts": ["hair", "shirt_bottom"], "delay_frames": 2}
        },
        {
            "principle": "squash_and_stretch",
            "confidence": 0.75,
            "reason": "Bouncing ball should compress on landing",
            "parameters": {"squash_factor": 0.7, "stretch_factor": 1.3}
        }
    ],
    "dominant_principle": "arc",
    "complexity_score": 0.7  # 0-1, affects refinement iterations
}
```

**Next**: → PLANNER AGENT

---

### 3. PLANNER AGENT

**Purpose**: Create detailed frame generation plan incorporating animation principles

**Tools**:
- `claude_plan_animation()` - High-level planning with Claude
- `calculate_arc_path()` - Generate arc trajectories
- `generate_timing_curve()` - Create custom easing functions
- `calculate_frame_spacing()` - Non-uniform frame distribution
- `compute_squash_stretch_schedule()` - Frame-by-frame deformation
- `plan_overlapping_motion()` - Stagger motion for different parts
- `volume_preservation_planner()` - Ensure consistent volume

**Input**: analysis, animation_principles, instruction

**Output**:
```python
plan = {
    "num_frames": int,  # Total frames to generate
    "frame_schedule": [
        {
            "frame_index": 0,
            "t": 0.0,  # Interpolation parameter (0-1)
            "arc_position": {"x": 100, "y": 200},
            "squash_stretch": {"x_scale": 1.0, "y_scale": 1.0},
            "parts_positions": {
                "head": {"x": 100, "y": 200, "rotation": 0},
                "left_arm": {"x": 80, "y": 220, "rotation": -10}
            }
        },
        # ... more frames
    ],
    "timing_curve": str,  # "ease-in-out", "bounce", "custom"
    "custom_easing": List[float],  # If custom timing
    "arc_type": str,  # "circular", "parabolic", "elliptical"
    "controlnet_strategy": str,  # "pose", "line_art", "depth", "hybrid"
    "controlnet_strength": float,  # 0-1
    "deformation_schedule": dict,  # Squash/stretch per frame
    "layered_motion": bool,  # True if overlapping action needed
    "motion_layers": List[dict],  # Separate plans for body, hair, clothing
    "volume_constraints": dict,  # Volume preservation targets
}
```

**Next**: → GENERATOR AGENT

---

### 4. GENERATOR AGENT

**Purpose**: Create frames using generative models guided by the plan

**Tools**:
- `comfyui_execute_workflow()` - ComfyUI API for complex workflows
- `animatediff_generate()` - AnimateDiff for motion generation
- `controlnet_apply_guidance()` - Structural control (pose/line/depth)
- `render_skeleton_guides()` - Visualize pose targets
- `interpolate_lineart()` - Blend keyframe line art
- `apply_deformation()` - Squash/stretch transformations
- `layer_composite()` - Combine motion layers for overlapping action
- `preserve_alpha()` - Maintain transparency

**Input**: plan, keyframe1, keyframe2, analysis

**Output**:
```python
frames = [
    "/outputs/job_id/frame_001.png",
    "/outputs/job_id/frame_002.png",
    # ...
]
```

**Generation Strategy**:
1. Generate base motion with AnimateDiff + ControlNet
2. Apply deformations (squash/stretch) per frame
3. Generate motion layers separately if overlapping action needed
4. Composite layers with appropriate timing offsets
5. Preserve transparency from original keyframes
6. Apply style transfer if needed to match keyframe style

**Next**: → VALIDATOR AGENT

---

### 5. VALIDATOR AGENT

**Purpose**: Assess quality and check adherence to animation principles

**Tools**:
- `claude_vision_assess_quality()` - Overall quality check with vision model
- `check_volume_consistency()` - Verify objects maintain volume (OpenCV)
- `analyze_line_weights()` - Check line art consistency
- `check_motion_smoothness()` - Optical flow analysis
- `calculate_style_similarity()` - CLIP/DINO feature matching
- `validate_arc_motion()` - Check if motion follows planned arcs
- `validate_timing()` - Check if spacing matches timing curve
- `check_deformation_quality()` - Verify squash/stretch looks natural
- `detect_artifacts()` - Find morphing, ghosting, or distortion

**Input**: frames, keyframe1, keyframe2, plan, animation_principles

**Output**:
```python
validation = {
    "overall_quality_score": float,  # 0-10
    "principle_adherence": {
        "arc": {"score": 8.5, "notes": "Motion follows arc well"},
        "slow_in_slow_out": {"score": 7.0, "notes": "Could use more ease-out"},
        "squash_and_stretch": {"score": 6.5, "notes": "Deformation too subtle"},
        "follow_through": {"score": 9.0, "notes": "Hair motion excellent"}
    },
    "technical_quality": {
        "volume_consistency": 0.92,
        "line_quality": 0.88,
        "motion_smoothness": 0.95,
        "style_match": 0.85,
        "no_artifacts": 0.90
    },
    "issues": [
        {
            "severity": "medium",
            "type": "volume_inconsistency",
            "frames": [3, 4, 5],
            "description": "Object appears to grow 15% in mid-motion",
            "suggested_fix": "Apply volume normalization"
        },
        {
            "severity": "low",
            "type": "timing",
            "frames": [6, 7],
            "description": "Motion could ease out more smoothly",
            "suggested_fix": "Add one more frame near end"
        }
    ],
    "needs_refinement": bool,
    "fix_suggestions": List[str]  # Prioritized list of fixes
}
```

**Decision Logic**:
- If `overall_quality_score >= 8.0`: → END
- If `overall_quality_score >= 6.0 AND iteration_count < 3`: → REFINER
- If `overall_quality_score < 6.0 AND iteration_count < 2`: → PLANNER (re-plan)
- If `iteration_count >= 3`: → END (accept best attempt)

**Next**: → REFINER (conditional) or END

---

### 6. REFINER AGENT

**Purpose**: Fix specific issues identified by validator

**Tools**:
- `ebsynth_style_transfer()` - Apply keyframe style to frames
- `inpaint_problem_regions()` - Fix specific areas with issues
- `adjust_line_weights()` - Normalize line art
- `restore_transparency()` - Fix alpha channel issues
- `blend_frames_smoothly()` - Temporal smoothing
- `normalize_volume()` - Adjust object sizes for consistency
- `apply_motion_blur()` - Add natural motion blur
- `color_correct()` - Match color palette to keyframes
- `enhance_deformation()` - Adjust squash/stretch if too subtle

**Input**: frames, validation, keyframe1, keyframe2, plan

**Output**:
```python
refined_frames = [
    "/outputs/job_id/refined_frame_001.png",
    "/outputs/job_id/refined_frame_002.png",
    # ...
]
```

**Refinement Strategy**:
1. Address high-severity issues first
2. Apply targeted fixes (inpainting) rather than regenerating
3. Use Ebsynth for style consistency
4. Temporal smoothing to reduce flicker
5. Volume normalization if needed
6. Enhance subtle effects if validator requests

**Next**: → VALIDATOR (re-check) or END

---

## LangGraph Flow Diagram

```
START
  ↓
[ANALYZER] ──→ analysis
  ↓           (What's moving? How? Where?)
  ↓
[PRINCIPLES] ──→ animation_principles
  ↓              (Which of the 12 principles apply?)
  ↓
[PLANNER] ──→ plan
  ↓           (Frame-by-frame motion plan)
  ↓
[GENERATOR] ──→ frames
  ↓             (Generate images)
  ↓
[VALIDATOR] ──→ validation
  ↓             (Quality check)
  ↓
  ├─ quality >= 8.0 ──→ END [DONE]
  │
  ├─ quality >= 6.0 ──→ [REFINER] ──→ refined_frames
  │                         ↓
  │                     [VALIDATOR] (re-check)
  │                         ↓
  │                     iteration < 3?
  │                         ├─ Yes → loop
  │                         └─ No → END
  │
  └─ quality < 6.0 ──→ [PLANNER] (re-plan with feedback)
                           ↓
                       (continues from PLANNER)
```

---

## LangGraph Implementation

```python
def build_telekinesis_graph():
    workflow = StateGraph(AnimationState)

    # Add nodes
    workflow.add_node("analyzer", analyzer_agent)
    workflow.add_node("principles", principles_agent)
    workflow.add_node("planner", planner_agent)
    workflow.add_node("generator", generator_agent)
    workflow.add_node("validator", validator_agent)
    workflow.add_node("refiner", refiner_agent)

    # Define flow
    workflow.set_entry_point("analyzer")

    workflow.add_edge("analyzer", "principles")
    workflow.add_edge("principles", "planner")
    workflow.add_edge("planner", "generator")
    workflow.add_edge("generator", "validator")

    # Conditional edge: validator decides next step
    workflow.add_conditional_edges(
        "validator",
        route_from_validator,
        {
            "refine": "refiner",
            "replan": "planner",
            "end": END
        }
    )

    # Conditional edge: refiner always goes back to validator
    workflow.add_edge("refiner", "validator")

    return workflow.compile()


def route_from_validator(state: AnimationState) -> str:
    """Intelligent routing based on quality and iteration count"""
    validation = state["validation"]
    iteration = state["iteration_count"]
    quality = validation["overall_quality_score"]

    # Good enough - done
    if quality >= 8.0:
        return "end"

    # Poor quality and early iterations - try replanning
    if quality < 6.0 and iteration < 2:
        state["iteration_count"] += 1
        return "replan"

    # Medium quality and budget remains - refine
    if quality >= 6.0 and iteration < 3:
        state["iteration_count"] += 1
        return "refine"

    # Out of iterations - accept result
    return "end"
```

---

## Implementation Phases

### PHASE 0: Foundation (Week 1)
**Goal**: Basic infrastructure

**Tasks**:
- Install LangGraph, LangChain, Anthropic SDK
- Setup Redis for state management
- Create AnimationState TypedDict
- Build empty StateGraph with 6 nodes
- Create agent stub functions
- Setup logging and monitoring

**Deliverable**: Empty graph that can be invoked without errors

---

### PHASE 1: Minimal Viable Pipeline (Week 2)
**Goal**: End-to-end flow with minimal logic

**Agents**:
- **ANALYZER**: Claude Vision only, basic description
- **PRINCIPLES**: Hardcoded response (always returns "arc" + "slow_in_slow_out")
- **PLANNER**: Simple linear interpolation plan
- **GENERATOR**: AnimateDiff only, no ControlNet
- **VALIDATOR**: Always returns score=8.0 (stub)
- **REFINER**: Not implemented

**Flow**: ANALYZER → PRINCIPLES → PLANNER → GENERATOR → VALIDATOR → END

**Test**: Upload 2 keyframes → Get blurry morphed frames

**Status**: BAD QUALITY but pipeline works

---

### PHASE 2: Add Vision Analysis (Week 3)
**Goal**: Real analysis and principle detection

**Upgrades**:
- **ANALYZER**: Add MediaPipe, OpenCV, segmentation
- **PRINCIPLES**: Use Claude to reason about which principles apply
- **PLANNER**: Incorporate principle parameters into plan

**Flow**: Same linear path

**Test**: System correctly identifies arcs, timing needs

**Status**: INTELLIGENT PLANNING but generation still basic

---

### PHASE 3: Add ControlNet Guidance (Week 4)
**Goal**: Better generation with structural control

**Upgrades**:
- **PLANNER**: Add arc calculations, timing curves
- **GENERATOR**: Add ControlNet (pose + line art), skeleton guides

**Flow**: Same linear path

**Test**: Frames follow structure, motion follows arcs

**Status**: GOOD STRUCTURE but may have artifacts

---

### PHASE 4: Add Validation Loop (Week 5)
**Goal**: Quality checking and iteration

**Upgrades**:
- **VALIDATOR**: Real quality checks (volume, smoothness, style)
- **REFINER**: Ebsynth, inpainting, blending

**Flow**: Add conditional routing from validator

**Test**: System iterates on low-quality frames

**Status**: SELF-CORRECTING, good quality

---

### PHASE 5: Advanced Principles (Week 6)
**Goal**: Squash/stretch, overlapping action

**Upgrades**:
- **PLANNER**: Add deformation schedules, motion layers
- **GENERATOR**: Apply deformations, layer compositing
- **VALIDATOR**: Check deformation quality

**Test**: Complex motions with squash/stretch work well

**Status**: PROFESSIONAL QUALITY

---

### PHASE 6: Optimization (Week 7+)
**Goal**: Speed and cost reduction

**Optimizations**:
- Cache Claude decisions for similar motions
- Parallel frame generation
- Skip refiner if quality > 8.5
- Reduce iterations for simple motions
- Batch processing in validator

**Monitoring**:
- Track which principles apply most often
- Measure iteration patterns
- Log quality improvements per iteration

**Status**: PRODUCTION READY

---

## Integration with Vizier

Telekinesis will be integrated into Vizier as an advanced mode:

```python
# In Vizier's Celery worker
@celery_app.task(bind=True)
def generate_frames_advanced(self, job_id, kf1, kf2, instruction):
    """Advanced generation using Telekinesis agent loop"""

    # Build Telekinesis graph
    graph = build_telekinesis_graph()

    # Initial state
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
            meta={
                'agent': current_agent,
                'progress': calculate_progress(state),
                'state': state
            }
        )

    # Return final frames
    final_frames = state.get("refined_frames") or state.get("frames")
    return {
        'frames': final_frames,
        'quality_score': state["validation"]["overall_quality_score"],
        'principles_applied': state["animation_principles"]["applicable_principles"],
        'iterations': state["iteration_count"],
        'messages': state["messages"]
    }
```

---

## Cost Estimate

Per animation job (8 frames):

| Phase | Claude Calls | Image Gen | Total Cost |
|-------|-------------|-----------|------------|
| Phase 1 | 3 | 1 | $0.02 |
| Phase 2 | 5 | 1 | $0.03 |
| Phase 3 | 5 | 1 | $0.04 |
| Phase 4 | 7 (w/ iteration) | 1-2 | $0.06 |
| Phase 5 | 8 | 1-2 | $0.08 |
| Phase 6 (optimized) | 5 (cached) | 1 | $0.04 |

**Target**: < $0.05 per animation with caching

---

## Success Metrics

### Phase 1
- Pipeline completes without errors
- Frames are generated (any quality)

### Phase 2
- Correct principle identification in 80%+ of cases
- Plans reflect appropriate principles

### Phase 3
- Motion follows planned arcs
- Frames maintain structural consistency

### Phase 4
- Quality score > 7.0 in 60%+ of cases
- Refinement improves quality by avg 1.5 points

### Phase 5
- Squash/stretch visible and natural
- Overlapping action works correctly
- Quality score > 7.0 in 80%+ of cases

### Phase 6
- Average cost < $0.05
- Average time < 3 minutes
- Cache hit rate > 40%

---

## Testing Strategy

### Unit Tests
```python
def test_analyzer_output():
    """Test analyzer produces valid analysis dict"""
    result = analyzer_agent(test_state)
    assert "motion_type" in result["analysis"]
    assert "parts_moved" in result["analysis"]

def test_principles_detection():
    """Test principle agent identifies correct principles"""
    result = principles_agent(state_with_arc_motion)
    principles = [p["principle"] for p in result["animation_principles"]["applicable_principles"]]
    assert "arc" in principles
```

### Integration Tests
```python
def test_full_pipeline():
    """Test complete graph execution"""
    graph = build_telekinesis_graph()
    result = graph.invoke(test_state)
    assert "frames" in result or "refined_frames" in result
    assert result["validation"]["overall_quality_score"] > 5.0
```

### Animation Quality Tests
- Visual inspection of generated frames
- Compare to hand-animated references
- User study with animators (later phase)

---

## Research Questions

1. **Can Claude Vision reliably detect which principles apply?**
   - Test: Curated dataset with ground truth labels
   - Metric: Precision/recall per principle

2. **Does principle-guided generation outperform naive interpolation?**
   - Test: A/B comparison with FILM, RIFE
   - Metric: User preference, animator ratings

3. **How many iterations are typically needed?**
   - Collect: Iteration counts per animation type
   - Goal: Minimize iterations while maintaining quality

4. **Which principles are most impactful?**
   - Test: Ablation study - disable principles one at a time
   - Metric: Quality score degradation

5. **Can we cache principle decisions?**
   - Test: Similar motions should have similar principle sets
   - Metric: Cache hit rate, quality impact

---

## Future Extensions

### Multi-Keyframe Support
- Extend to 3+ keyframes
- Apply principles across entire sequence
- Detect rhythm and pacing

### Interactive Refinement
- User provides feedback on specific frames
- Agent re-generates with constraints
- Learning from corrections

### Style Learning
- Train LoRA on user's art style
- Apply consistently across generations
- Preserve hand-drawn aesthetic

### Principle Customization
- Allow users to emphasize/de-emphasize principles
- Custom principle definitions
- Per-character principle profiles

---

## Conclusion

Telekinesis represents a paradigm shift in AI-assisted animation: from naive interpolation to principle-driven synthesis. By encoding the foundational knowledge of animation into an agent loop, we can generate frames that don't just morph between images, but truly animate with understanding, weight, and appeal.

This is animation made by an AI that understands animation.

---

**Next Steps**:
1. Begin Phase 0 - setup infrastructure
2. Create animation_principles.json knowledge base
3. Build agent stub functions
4. Test end-to-end graph execution
