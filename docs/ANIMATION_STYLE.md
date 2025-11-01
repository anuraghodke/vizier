# Animation Style Guide - Vizier

## Target Animation Style: Classic Cel Animation with Dynamic Camera Work

### Core Philosophy
Vizier is designed to assist with **old-school cel animation** techniques, specifically targeting the eccentric, boundary-pushing style exemplified by films like **"The Thief and the Cobbler"** (Richard Williams).

This style combines traditional hand-drawn animation with:
- Complex camera movements in 2D space
- Sophisticated perspective systems
- Physics-based motion interpolation
- Dynamic architectural environments

---

## Reference: The Thief and the Cobbler Techniques

### 1. Dynamic Tracking Shots
- **What it is**: Entire environments drawn to simulate camera movement through 3D space
- **In Vizier**: When interpolating between keyframes, the system should understand spatial relationships and maintain consistent perspective shifts
- **Example**: A character walking through a corridor - interpolated frames should show gradual perspective changes, not just position changes

### 2. Simulated Dolly and Crane Shots
- **What it is**: Meticulous frame-by-frame perspective animation to emulate:
  - Dolly-ins (camera moving toward subject)
  - Crane rises (camera moving vertically)
  - Circular tracking shots (camera orbiting subject)
- **In Vizier**: Interpolation should account for scale changes and perspective distortion as "camera" moves

### 3. Extreme Rotations
- **What it is**: Full 360° motion around architectural structures
- **In Vizier**: When interpolating rotating objects or environments, maintain proper vanishing point transitions
- **Challenge**: Telekinesis agents must analyze rotational motion and plan arc-based paths for natural rotation

### 4. Complex Perspective Systems
- **Multiple Vanishing Points**: 2-, 3-, even 5-point perspective in complex scenes
- **Moving Vanishing Points**: Unlike static backgrounds, vanishing points shift frame-by-frame
- **Depth and Parallax**: True parallax where every object is redrawn at new depths
- **In Vizier**: This is the most challenging aspect - interpolation must preserve perspective consistency

---

## Critical Requirement: Physics-Based Interpolation

### The Problem with Naive Interpolation

**BAD Example** (Simple Crossfade):
```
Frame 1: Red ball (left side)
Frame 3: Blue ball (right side)

Naive interpolation:
Frame 2: Semi-transparent red ball (left) + Semi-transparent blue ball (right)
         → Ghosting effect, no motion
```

**GOOD Example** (Physics-Based):
```
Frame 1: Red ball (left side, x=10)
Frame 3: Blue ball (right side, x=90)

Physics-based interpolation:
Frame 2: Purple ball (center, x=50)
         → Color: RGB interpolation (255,0,0) → (128,0,128) → (0,0,255)
         → Position: Linear path (10 → 50 → 90)
         → Result: Ball appears to MOVE and change color
```

### Key Principle: **Objects Should Move, Not Fade**

Vizier's interpolation must:
1. **Track objects spatially** - Understand that the same object exists in both keyframes
2. **Interpolate properties smoothly**:
   - Position (x, y coordinates)
   - Color (RGB/RGBA values)
   - Scale (size changes)
   - Rotation (orientation)
   - Opacity (alpha channel)
3. **Maintain object continuity** - One object becoming another, not two separate objects

---

## Telekinesis Agent Loop Architecture

### How Vizier Generates Animation

Vizier uses a **multi-agent system** called Telekinesis that applies the **12 Principles of Animation** to generate intermediate frames. Instead of naive pixel interpolation, specialized AI agents work together to:

1. **ANALYZER Agent**: Understands what's changing between keyframes
   - Visual analysis using Claude Vision
   - Motion type detection (rotation, translation, deformation)
   - Object segmentation and part identification
   - Pose detection and style analysis

2. **PRINCIPLES Agent**: Determines which animation principles apply
   - Identifies relevant principles (arc, squash & stretch, timing, etc.)
   - Assigns confidence scores
   - Extracts principle-specific parameters

3. **PLANNER Agent**: Creates detailed frame-by-frame generation plan
   - Generates timing curves (ease-in, ease-out, custom)
   - Calculates arc paths for natural motion
   - Plans deformation schedules (squash/stretch per frame)
   - Designs motion layers for overlapping action

4. **GENERATOR Agent**: Creates intermediate frames using generative models
   - Uses FrameGeneratorService for object-based interpolation (Phase 1)
   - Will integrate AnimateDiff + ControlNet guidance (future phases)
   - Applies frame-by-frame deformations
   - Preserves transparency from original keyframes

5. **VALIDATOR Agent**: Assesses quality and principle adherence
   - Quality assessment using Claude Vision
   - Volume consistency checking
   - Motion smoothness analysis
   - Principle adherence validation

6. **REFINER Agent**: Fixes specific issues identified by validator
   - Style transfer for consistency
   - Inpainting for problem regions
   - Temporal smoothing
   - Line art cleanup

**Key Advantage**: This agent-based approach treats animation as an animation problem, not just a computer vision problem, ensuring principles like arc motion, squash & stretch, and timing are properly applied.

---

## Testing Strategy for Physics-Based Interpolation

### Test Case 1: Simple Translation + Color Change
```python
# Frame 1: Red ball (left)
# Frame 2: Blue ball (right)
# Expected: Ball moves right while changing red → blue
```

### Test Case 2: Rotation
```python
# Frame 1: Character facing left
# Frame 2: Character facing right (180° rotation)
# Expected: Smooth rotation, not morphing
```

### Test Case 3: Scale Change
```python
# Frame 1: Small object (near)
# Frame 2: Large object (far) - simulating dolly-in
# Expected: Gradual scale increase, perspective-aware
```

### Test Case 4: Arc Motion (with intermediate keyframe)
```python
# Frame 1: Ball at bottom-left
# Frame 2: Ball at top-center (apex of arc)
# Frame 3: Ball at bottom-right
# Expected: Parabolic path, not linear
```

### Test Case 5: Squash and Stretch
```python
# Frame 1: Ball (round, at top)
# Frame 2: Ball (squashed, at bottom) - impact
# Expected: Maintains volume, shows compression
```

---

## Implementation Through Telekinesis Agents

### ANALYZER Agent Responsibilities
1. **Visual Analysis**:
   - Use Claude Vision to understand what's in each keyframe
   - Detect if images represent "same object in different states"
   - Identify objects, characters, backgrounds

2. **Motion Type Detection**:
   - **Translation**: Object position changes (most common)
   - **Rotation**: Object orientation changes
   - **Scale**: Object size changes (depth simulation)
   - **Deformation**: Object shape changes (squash/stretch)
   - **Hybrid**: Combination of above

3. **Object Segmentation**:
   - Identify moving parts vs static elements
   - Detect pose changes (for characters)
   - Measure volume and structural properties

### PRINCIPLES Agent Responsibilities
1. **Principle Identification**:
   - Analyze motion to identify relevant principles
   - Assign confidence scores to each applicable principle
   - Extract principle-specific parameters (arc angle, squash amount, etc.)

2. **Motion Intent Parsing** (via Claude Service):
   - "bounce" → arc motion with squash/stretch
   - "rotate" → rotational interpolation with arc
   - "zoom" → scale interpolation with slow-in/slow-out
   - "glide" → smooth linear translation

3. **Timing Curve Extraction**:
   - "ease-in" → slow start, fast end
   - "ease-out" → fast start, slow end
   - "linear" → constant speed
   - "bounce" → elastic timing curve

### PLANNER Agent Responsibilities
1. **Frame Schedule Generation**:
   - Create detailed frame-by-frame plan
   - Calculate interpolation parameters (t values)
   - Apply timing curves from principles

2. **Motion Path Planning**:
   - Calculate arc paths for natural motion
   - Plan position interpolation with curves
   - Design deformation schedules (squash/stretch per frame)

3. **Generation Strategy**:
   - Determine ControlNet strategy (pose, line art, depth)
   - Plan motion layers for overlapping action
   - Set volume preservation constraints

---

## Validation Criteria

### Minimum Viable Product (MVP)
An interpolated animation passes validation if:
1. [COMPLETE] **No ghosting**: Objects don't appear duplicated or semi-transparent
2. [COMPLETE] **Smooth motion**: Objects move along clear paths, not teleport
3. [COMPLETE] **Property continuity**: Color/scale/rotation changes are gradual
4. [COMPLETE] **Temporal consistency**: Motion speed feels natural

### Stretch Goals (Post-MVP)
1. **Perspective-aware**: Maintains vanishing point consistency
2. **Style preservation**: Output looks hand-drawn, not morphed
3. **Arc motion**: Supports natural curved paths (not just linear)
4. **Squash/stretch**: Preserves volume in deformations

---

## Known Limitations (To Address in Future Phases)

### Current Phase 1 Constraints (Object-Based Interpolation)
1. **Limited to simple object motion**: FrameGeneratorService uses color-based segmentation
   - Works well for simple objects (balls, shapes)
   - May struggle with complex characters or multiple objects
   - Basic interpolation without generative models

2. **No generative enhancement**: Currently using simple position/color interpolation
   - Will improve with AnimateDiff integration (Phase 1+)
   - ControlNet guidance will add structural control
   - Style preservation requires refinement agent

3. **Principle application is basic**: Some principles not yet fully implemented
   - Arc motion: Basic path calculation (Phase 1)
   - Squash/stretch: Planned for Phase 5
   - Overlapping action: Planned for Phase 5

### Future Improvements
1. **AnimateDiff Integration**: Add motion-aware generation (Phase 1)
2. **ControlNet Guidance**: Structural control for pose and line art (Phase 3)
3. **Advanced Principles**: Full squash/stretch, overlapping action (Phase 5)
4. **Style Preservation**: Ebsynth-style refinement (Phase 4+)

---

## User Workflow Recommendations

### For Best Results, Users Should:
1. **Use clear keyframes**: Distinct start/end states
2. **Add intermediate keyframes** for:
   - Extreme rotations (add 90°, 180°, 270° frames)
   - Arc motion (add apex keyframe)
   - Squash/stretch (add compressed state keyframe)
3. **Describe motion intent**: "ball bounces" vs "ball moves"
4. **Match perspective**: Keep vanishing points consistent if possible

### Example Workflow
```
Goal: Animate ball bouncing across screen

Keyframes:
  1. Ball at left (round)
  2. Ball at apex (slightly stretched upward)
  3. Ball at mid-ground (squashed on impact)
  4. Ball at right (round)

Instructions to Vizier:
  "Create 4 bouncy frames between each keyframe"

Result:
  - Frames 1-2: Rising arc with stretch
  - Frames 2-3: Falling arc
  - Frames 3-4: Squash on impact + rise again
```

---

## Success Metrics

### Phase 0: Telekinesis Foundation [COMPLETE]
- [COMPLETE] Multi-agent infrastructure (LangGraph)
- [COMPLETE] 6 agent stubs created and routing works
- [COMPLETE] AnimationState TypedDict defined
- [COMPLETE] Animation Principles Knowledge Base created

### Phase 1: Minimal Viable Pipeline [IN PROGRESS]
- ⬜ Claude Vision analysis in ANALYZER agent
- ⬜ FrameGeneratorService integration in GENERATOR agent
- ⬜ End-to-end agent loop execution
- ⬜ Simple object motion interpolation works

### Phase 2: Vision Analysis
- ⬜ Real motion detection (translation, rotation, scale)
- ⬜ Claude-based principle identification
- ⬜ Principle parameters extraction

### Phase 3: ControlNet Guidance
- ⬜ Structural control (pose + line art)
- ⬜ Arc path calculations
- ⬜ Timing curves applied correctly (ease-in/out)

### Phase 4: Validation Loop
- ⬜ Real quality checking
- ⬜ Refiner implementation
- ⬜ Iterative improvement

### Phase 5: Advanced Principles
- ⬜ Squash/stretch with volume preservation
- ⬜ Overlapping action (motion layers)
- ⬜ Complex perspective shifts (moving vanishing points)

---

## References

### Films for Inspiration
- **The Thief and the Cobbler** (Richard Williams) - Dynamic camera work
- **Akira** (1988) - Complex perspective and motion
- **Paprika** (2006) - Extreme camera movements
- **Redline** (2009) - High-speed motion with style preservation

### Technical Resources
- **The Animator's Survival Kit** (Richard Williams) - Timing and spacing
- **Disney's 12 Principles of Animation** - Squash/stretch, arc motion, etc.
- **Perspective for Comic Book Artists** - Multiple vanishing points

---

## Next Steps

1. **Complete Phase 1 Implementation**:
   - Integrate Claude Vision in ANALYZER agent
   - Connect FrameGeneratorService to GENERATOR agent
   - End-to-end test with simple object motion

2. **Create test image pairs** that demonstrate:
   - Translation + color change (red ball → blue ball)
   - Simple rotation (character turning)
   - Scale change (object approaching camera)

3. **Validate agent coordination**:
   - Test that agents pass state correctly
   - Verify principle detection works
   - Check frame generation quality

4. **Document results** in `test_images/` with notes on quality

---

**Last Updated**: Telekinesis Agent Loop Architecture - Phase 0 Complete, Phase 1 In Progress
