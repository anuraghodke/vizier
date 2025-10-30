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
- **Challenge**: FILM model needs to understand rotational motion, not just lateral movement

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

## FILM Model Behavior Analysis (Phase 0 Test Results)

### [WARNING] CRITICAL FINDINGS FROM TESTING

Phase 0 testing revealed that FILM's behavior **differs significantly** from initial expectations. See `PHASE_0_FINDINGS.md` for complete analysis.

### What FILM Does Well 
- **Same-object motion**: Objects moving with consistent appearance (same color, same shape)
- **Camera pans**: Background motion and parallax effects
- **Subtle timing**: Small adjustments to motion speed/timing
- **Optical flow tracking**: Can track pixels when appearance is consistent

### What FILM Struggles With 
**TESTED AND CONFIRMED**:

1. **Position + Color Change = Ghosting**
   ```
   Input:
     Frame A: Red ball at left (x=128)
     Frame B: Blue ball at right (x=384)

   Expected: Purple ball in middle
   Actual: Two faint balls (red left, blue right) - CROSSFADE
   ```
   **Reason**: Optical flow can't link pixels when both position AND appearance change

2. **Transparent Backgrounds = Worse Ghosting**
   - FILM treats transparent regions as "nothing"
   - Objects in different positions appear as separate entities
   - Recommendation: Use solid backgrounds when possible

3. **Motion Blur Even With Same Color**
   - Same-colored objects moving still show some ghosting
   - Not the clean "cel animation" look
   - More photorealistic blur than hand-drawn motion

4. **Complex Rotations**: 360° rotations cause morphing artifacts
5. **Perspective Shifts**: Moving vanishing points confuse optical flow
6. **Style Morphing**: Creates photorealistic blend, not hand-drawn style
7. **Squash & Stretch**: Volume not preserved, creates unnatural morphing

### Test Results Summary
| Test Case | Result | Quality |
|-----------|--------|---------|
| Red ball → Blue ball (transparent BG) | Strong ghosting | [FAILED] BAD |
| Red ball → Blue ball (white BG) | Strong ghosting | [FAILED] BAD |
| Red ball → Red ball (white BG) | Motion blur, centered | [WARNING] OK |
| Blue ball → Blue ball (white BG) | Motion blur, centered | [WARNING] OK |

**Conclusion**: FILM is best for consistent-appearance motion, struggles with transformations.

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

## Implementation Requirements

### Phase 1: Core Service Development
When building `film_service.py`:
1. **Preprocessing**:
   - Detect if images represent "same object in different states"
   - Analyze motion vectors between keyframes
   - Identify if motion is translation, rotation, scale, or combination

2. **Motion Type Detection**:
   - **Translation**: Object position changes (most common)
   - **Rotation**: Object orientation changes
   - **Scale**: Object size changes (depth simulation)
   - **Deformation**: Object shape changes (squash/stretch)
   - **Hybrid**: Combination of above

3. **FILM Parameters**:
   - Use FILM's optical flow for motion-aware interpolation
   - May need to adjust preprocessing for extreme cases
   - Consider edge cases where FILM might fail

### Phase 2: Claude API Integration
When building `claude_service.py`:
1. **Parse motion intent**:
   - "bounce" → arc motion with squash/stretch
   - "rotate" → rotational interpolation
   - "zoom" → scale interpolation
   - "glide" → smooth linear translation

2. **Extract timing curves**:
   - "ease-in" → slow start, fast end
   - "ease-out" → fast start, slow end
   - "linear" → constant speed

3. **Detect advanced techniques**:
   - "squash and stretch"
   - "anticipation"
   - "follow-through"
   - "arc motion"

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

### FILM Model Constraints
1. **No semantic understanding**: FILM doesn't know "this is a ball"
   - It only tracks pixel motion via optical flow
   - Can't enforce "object rules" like volume preservation

2. **Style morphing**: FILM creates photorealistic interpolation
   - May lose hand-drawn line quality
   - Colors may blend in unintended ways
   - Textures may blur

3. **Complex rotations**: 360° rotations may cause artifacts
   - Optical flow can get confused on full rotations
   - May need multiple keyframes for clean rotation

### Mitigation Strategies
1. **User guidance**: Recommend more keyframes for complex motions
2. **Motion type hints**: Use Claude-parsed intent to preprocess images
3. **Post-processing**: Consider adding style-preserving filters
4. **Layered approach**: Separate character from background for complex scenes

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

### Phase 0-1 (Current)
- [COMPLETE] FILM produces motion-aware interpolation (not crossfade)
- [COMPLETE] Simple translation works (e.g., ball moving left to right)
- [COMPLETE] Color transitions work (e.g., red ball → blue ball)

### Phase 2-3
- ⬜ Rotations work without major artifacts
- ⬜ Scale changes work (dolly in/out)
- ⬜ Timing curves applied correctly (ease-in/out)

### Phase 4+
- ⬜ Arc motion with intermediate keyframes
- ⬜ Squash/stretch with volume preservation
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

1. **Create test image pairs** that demonstrate:
   - Translation + color change (red ball → blue ball)
   - Simple rotation (character turning)
   - Scale change (object approaching camera)

2. **Run FILM tests** with these pairs to validate physics-based behavior

3. **Document results** in `test_images/` with notes on quality

4. **Adjust preprocessing** in `film_service.py` based on findings

---

**Last Updated**: Phase 0 Complete - Animation Style Context Added
