# Model Comparison Research Plan

## Overview

Phase 0 testing revealed that **FILM has critical limitations** with our core use case (color + motion). We need to evaluate alternative models to find the best fit for Vizier's animation goals.

## Research Strategy

**Approach**: Evaluate each model in **separate git branches** to allow parallel exploration without conflicts.

### Branch Structure
```
main                    # Current stable code with FILM
├── experiment/rife     # RIFE model integration
├── experiment/ebsynth  # Ebsynth integration
└── experiment/animatediff  # AnimateDiff (optional)
```

**Workflow**:
1. Create feature branch for each model
2. Implement integration in isolated branch
3. Run standard test suite
4. Document results in branch
5. Compare all branches side-by-side
6. Merge winner back to main

---

## Test Suite - Standard Cases

Create these test images to evaluate all models fairly:

### Test 1: Color + Motion ⭐ CRITICAL
**Our Core Use Case**
- **Frame 1**: Red circle, left side (x=50, y=256)
- **Frame 2**: Blue circle, right side (x=450, y=256)
- **Expected**: Purple circle in middle, smooth motion
- **FILM Result**: ❌ Ghosting (two faint balls, no purple)
- **Test with**: RIFE, Ebsynth, AnimateDiff

### Test 2: Rotation (No Color Change)
- **Frame 1**: Simple character facing left
- **Frame 2**: Same character facing right
- **Expected**: Clean rotation, style preserved
- **Test**: All models

### Test 3: Squash & Stretch
- **Frame 1**: Circle (100px diameter)
- **Frame 2**: Ellipse (150px wide, 50px tall)
- **Expected**: Volume-preserving transformation
- **Test**: All models

### Test 4: Camera Pan
- **Frame 1**: Detailed background, left view
- **Frame 2**: Same background, right view
- **Expected**: Smooth parallax scrolling
- **Test**: All models

### Test 5: Complex Character Motion
- **Frame 1**: Hand-drawn character, pose A
- **Frame 2**: Hand-drawn character, pose B
- **Expected**: Style-preserving in-between
- **Test**: Ebsynth (primary), others for comparison

---

## Models to Evaluate

### 1. RIFE (Real-Time Intermediate Flow Estimation)
**Branch**: `experiment/rife`

**What it is**: Anime-focused frame interpolation using optical flow

**Repository**: https://github.com/megvii-research/ECCV2022-RIFE

**Setup**:
```bash
git checkout -b experiment/rife
cd models/
git clone https://github.com/megvii-research/ECCV2022-RIFE rife
cd rife
pip install -r requirements.txt
# Download pretrained weights
```

**Integration**: Create `backend/app/services/rife_service.py` (similar to `film_service.py`)

**Expected Pros**:
- Designed for anime/cartoon content
- Faster than FILM
- Better at stylized content

**Expected Cons**:
- Still optical flow-based (may have similar limitations)
- May still ghost on color+motion

**Success Criteria**:
- [ ] Handles color+motion better than FILM (Test 1)
- [ ] Preserves cel animation style (Test 2, 5)
- [ ] Easy Python integration
- [ ] Speed acceptable on CPU

---

### 2. Ebsynth (Style-Preserving Video Synthesis)
**Branch**: `experiment/ebsynth`

**What it is**: Professional rotoscoping tool used by animators for style transfer

**Website**: https://ebsynth.com/

**Setup**:
```bash
git checkout -b experiment/ebsynth
# Download Ebsynth from website
# Research: CLI interface or Python API?
```

**Integration**: More complex - requires "guide frames"

**Workflow Difference**:
- Traditional: User provides 2 keyframes → 8 in-betweens
- Ebsynth: User provides keyframes at intervals + style guides

**Expected Pros**:
- ✅ Actually preserves hand-drawn style
- ✅ Used by professional animators
- ✅ Handles transformations better
- ✅ Can maintain artistic look

**Expected Cons**:
- ❌ Requires guide frames (more complex)
- ❌ May not have Python API
- ❌ Non-commercial license (check terms)
- ❌ Workflow more manual

**Success Criteria**:
- [ ] Excellent style preservation (Test 5)
- [ ] Handles color+motion cleanly (Test 1)
- [ ] Automation feasible (can we generate guides?)
- [ ] Integration complexity acceptable

---

### 3. AnimateDiff (Stable Diffusion Animation)
**Branch**: `experiment/animatediff` (OPTIONAL)

**What it is**: AI-generated animation using Stable Diffusion + ControlNet

**Repository**: https://github.com/guoyww/AnimateDiff

**Setup**:
```bash
git checkout -b experiment/animatediff
# Complex setup - requires SD environment
# May skip if no GPU available
```

**Expected Pros**:
- Can match artistic style with prompts
- Generative flexibility

**Expected Cons**:
- ❌ Non-deterministic (same input ≠ same output)
- ❌ Requires GPU
- ❌ Slow generation
- ❌ May hallucinate details
- ❌ Harder to control

**Success Criteria**:
- [ ] Predictable enough for production?
- [ ] Can run on CPU or user GPUs?
- [ ] Style controllable via prompts?
- [ ] Generation time acceptable?

---

## Evaluation Criteria

Score each model on these criteria:

| Criteria | Weight | Why It Matters | FILM Baseline |
|----------|--------|----------------|---------------|
| **Color+Motion** | 3x | Core use case | 2/10 (ghosting) |
| **Style Preservation** | 3x | Hand-drawn look | 3/10 (photorealistic) |
| **Transparency** | 2x | Procreate exports | 7/10 (manual handling) |
| **Integration** | 2x | Can we build it? | 9/10 (clean API) |
| **Speed** | 1x | User wait time | 7/10 (2-3s/frame CPU) |
| **Predictability** | 1x | Consistent results | 9/10 (deterministic) |
| **License** | 1x | Can we use it? | 10/10 (Apache 2.0) |

**Total Score** = Sum(Score × Weight)

---

## Branch Workflow

### Starting a Model Experiment

```bash
# 1. Start from clean main
git checkout main
git pull origin main

# 2. Create experiment branch
git checkout -b experiment/rife

# 3. Install model dependencies
cd models/
# ... setup specific to model

# 4. Create service wrapper
# Copy backend/app/services/film_service.py → rife_service.py
# Adapt for new model

# 5. Update tests
# Copy tests/test_services.py → tests/test_rife_service.py
# Run test suite

# 6. Document results
# Create docs/RIFE_EVALUATION.md with findings

# 7. Commit to branch
git add .
git commit -m "experiment: rife model integration and evaluation"
git push origin experiment/rife
```

### Comparing Results

After testing all models, create comparison document:

```bash
git checkout main
# Create docs/MODEL_COMPARISON_RESULTS.md
# Include screenshots, scores, recommendation
```

### Merging Winner

```bash
# Once we've chosen the best model
git checkout main
git merge experiment/rife  # (or whichever won)
git push origin main

# Archive other experiments
git branch -d experiment/ebsynth
git branch -d experiment/animatediff
```

---

## Test Harness

Create `tests/model_comparison.py` to run standardized tests:

```python
"""
Model comparison test harness.

Usage:
    python tests/model_comparison.py --model rife --test-case color_motion
    python tests/model_comparison.py --model ebsynth --test-case all
"""

import time
from pathlib import Path
from PIL import Image
import json

class ModelTester:
    """Standardized testing framework for frame interpolation models."""

    TEST_CASES = {
        'color_motion': {
            'frame1': 'tests/test_images/physics_test/frame1_red_left.png',
            'frame2': 'tests/test_images/physics_test/frame2_blue_right.png',
            'expected': 'Purple ball in center, smooth motion path',
        },
        'rotation': {
            'frame1': 'tests/test_images/rotation/frame1_left.png',
            'frame2': 'tests/test_images/rotation/frame2_right.png',
            'expected': 'Clean rotation preserving style',
        },
        # ... more test cases
    }

    def __init__(self, model_name):
        self.model_name = model_name
        self.results = []

    def run_test(self, test_case_name, num_frames=8):
        """Run a single test case."""
        test_case = self.TEST_CASES[test_case_name]

        print(f"\n{'='*60}")
        print(f"Testing {self.model_name} on {test_case_name}")
        print(f"{'='*60}")

        # Load frames
        frame1 = Image.open(test_case['frame1'])
        frame2 = Image.open(test_case['frame2'])

        # Time the interpolation
        start = time.time()
        frames = self.interpolate(frame1, frame2, num_frames)
        elapsed = time.time() - start

        # Analyze results
        quality_scores = self.analyze_quality(frames, test_case_name)

        # Save results
        self.save_results(test_case_name, frames, quality_scores, elapsed)

        # Print summary
        print(f"⏱️  Time: {elapsed:.2f}s ({elapsed/num_frames:.2f}s/frame)")
        print(f"📊 Quality Scores:")
        for metric, score in quality_scores.items():
            print(f"   {metric}: {score}/10")

    def interpolate(self, frame1, frame2, num_frames):
        """Interpolate frames using the current model."""
        if self.model_name == 'film':
            from backend.app.services import film_service
            return film_service.interpolate_frames(frame1, frame2, num_frames)
        elif self.model_name == 'rife':
            from backend.app.services import rife_service
            return rife_service.interpolate_frames(frame1, frame2, num_frames)
        elif self.model_name == 'ebsynth':
            from backend.app.services import ebsynth_service
            return ebsynth_service.interpolate_frames(frame1, frame2, num_frames)
        else:
            raise ValueError(f"Unknown model: {self.model_name}")

    def analyze_quality(self, frames, test_case_name):
        """Analyze frame quality with various metrics."""
        scores = {}

        # Ghosting detection (for color_motion test)
        if test_case_name == 'color_motion':
            scores['ghosting'] = self.detect_ghosting(frames)

        # Style consistency
        scores['style_consistency'] = self.measure_style_consistency(frames)

        # Motion smoothness
        scores['motion_smoothness'] = self.measure_motion_smoothness(frames)

        return scores

    def detect_ghosting(self, frames):
        """
        Detect ghosting artifacts (multiple faint objects).

        Returns: Score 1-10 (10 = no ghosting)
        """
        # TODO: Implement ghosting detection
        # Count distinct "blobs" in middle frame
        # More than 1 blob = ghosting
        return 5  # Placeholder

    def measure_style_consistency(self, frames):
        """
        Measure how well style is preserved.

        Returns: Score 1-10 (10 = perfect style preservation)
        """
        # TODO: Compare edge detection, line quality
        return 5  # Placeholder

    def measure_motion_smoothness(self, frames):
        """
        Measure motion path smoothness.

        Returns: Score 1-10 (10 = perfectly smooth)
        """
        # TODO: Track object centroid across frames
        # Check if path is linear/smooth
        return 5  # Placeholder

    def save_results(self, test_case_name, frames, quality_scores, elapsed):
        """Save frames and results to disk."""
        output_dir = Path(f"tests/comparison_results/{self.model_name}/{test_case_name}")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save frames
        for i, frame in enumerate(frames):
            frame.save(output_dir / f"frame_{i:03d}.png")

        # Save metadata
        metadata = {
            'model': self.model_name,
            'test_case': test_case_name,
            'num_frames': len(frames),
            'time_elapsed': elapsed,
            'time_per_frame': elapsed / len(frames),
            'quality_scores': quality_scores,
        }

        with open(output_dir / 'results.json', 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"💾 Results saved to {output_dir}")

    def run_all_tests(self):
        """Run all test cases."""
        for test_case_name in self.TEST_CASES:
            self.run_test(test_case_name)

        # Generate comparison report
        self.generate_report()

    def generate_report(self):
        """Generate markdown report with all results."""
        # TODO: Create side-by-side comparison images
        # TODO: Generate markdown with scores and screenshots
        pass


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Test frame interpolation models')
    parser.add_argument('--model', required=True, choices=['film', 'rife', 'ebsynth', 'animatediff'])
    parser.add_argument('--test-case', default='all', help='Test case name or "all"')
    parser.add_argument('--frames', type=int, default=8, help='Number of frames to generate')

    args = parser.parse_args()

    tester = ModelTester(args.model)

    if args.test_case == 'all':
        tester.run_all_tests()
    else:
        tester.run_test(args.test_case, args.frames)
```

---

## Documentation Template

For each model branch, create `docs/{MODEL}_EVALUATION.md`:

### 1. Setup Experience (1-10)
- Installation steps taken
- Dependencies installed
- Time to first working test
- Issues encountered

### 2. Test Results

| Test Case | Quality (1-10) | Speed (s/frame) | Notes |
|-----------|----------------|-----------------|-------|
| Color+Motion | ? | ? | Ghosting? Clean? Purple ball visible? |
| Rotation | ? | ? | Style preserved? Artifacts? |
| Squash/Stretch | ? | ? | Natural deformation? Volume preserved? |
| Camera Pan | ? | ? | Smooth parallax? Jittering? |
| Character Motion | ? | ? | Hand-drawn feel? Line quality? |

### 3. Integration Assessment (1-10)
- [ ] Python API available?
- [ ] Easy to wrap in service class?
- [ ] Can parameterize frame count?
- [ ] Error handling complexity?
- [ ] Transparency support?

### 4. Performance Benchmarks
- CPU time per frame: ?s
- GPU time per frame: ?s (if applicable)
- Memory usage: ?MB
- Total time for 8-frame sequence: ?s

### 5. Output Quality (Screenshots)
- Include screenshots of each test case
- Side-by-side comparison with FILM
- Highlight artifacts or improvements

### 6. Recommendation
- Overall score: ?/10
- Best use cases: ...
- Dealbreakers: ...
- Integration effort: Low/Medium/High

---

## Hybrid/Ensemble Possibilities

If no single model is perfect, consider combining them:

### Option 1: Model Router
Route to best model based on animation type:

```python
def choose_model(frame1, frame2, instruction):
    """Intelligently route to best model for this animation."""
    analysis = analyze_keyframes(frame1, frame2)

    if analysis.color_change and analysis.position_change:
        return "ebsynth"  # Best for complex transformations
    elif analysis.camera_motion:
        return "film"     # Good at background motion
    elif analysis.simple_motion:
        return "rife"     # Fast for simple cases
    else:
        return "rife"     # Default
```

### Option 2: Sequential Pipeline
Use multiple models in sequence:

```python
# Step 1: RIFE for speed (initial pass)
rough_frames = rife.interpolate(frame1, frame2, count=8)

# Step 2: Ebsynth for style (refinement pass)
styled_frames = [
    ebsynth.stylize(frame, reference=frame1)
    for frame in rough_frames
]
```

### Option 3: Separate Position and Color
Interpolate components independently:

```python
# Interpolate spatial position with optical flow
position_frames = rife.interpolate_grayscale(frame1, frame2)

# Interpolate color linearly
color_frames = interpolate_color_smooth(frame1, frame2)

# Combine position and color
final_frames = [
    apply_color_to_structure(pos, color)
    for pos, color in zip(position_frames, color_frames)
]
```

**Branch**: `experiment/hybrid` (if needed after evaluating all models)

---

## Timeline

### Week 1: RIFE Exploration
- Create `experiment/rife` branch
- Integrate RIFE model
- Run test suite
- Document in `docs/RIFE_EVALUATION.md`

### Week 2: Ebsynth Exploration
- Create `experiment/ebsynth` branch
- Prototype Ebsynth integration
- Test workflow complexity
- Document in `docs/EBSYNTH_EVALUATION.md`

### Week 3: AnimateDiff (Optional)
- Create `experiment/animatediff` branch (if time permits)
- Quick feasibility test
- Document in `docs/ANIMATEDIFF_EVALUATION.md`

### Week 4: Decision & Integration
- Create `docs/MODEL_COMPARISON_RESULTS.md`
- Compare all branches side-by-side
- Make final decision
- Merge winning branch to main
- Update architecture if needed

---

## Success Criteria

We've found the right model when:

✅ **Test 1 (Color+Motion)** produces:
- Purple ball visible in center frame
- Smooth motion path (not two separate objects)
- NO ghosting or crossfading
- Clean edges on transparency

✅ **Test 5 (Character Motion)** produces:
- Hand-drawn style preserved
- Clean lines (not photorealistic blur)
- Natural in-between pose

✅ **Integration is feasible**:
- Python API or CLI wrapper exists
- Workflow can be automated
- Processing time acceptable (<5s/frame on CPU)
- Can handle transparency properly

✅ **License is compatible**:
- Commercial use allowed
- Open source or affordable
- No restrictive terms

---

## Decision Framework

After evaluating all models:

1. **Calculate weighted scores** using evaluation criteria
2. **Identify dealbreakers** (e.g., no Python API, GPU-only, bad license)
3. **Consider integration effort** vs. quality improvement
4. **Check user experience** (processing time, predictability)
5. **Make recommendation** with clear justification

**Final decision documented in**: `docs/MODEL_COMPARISON_RESULTS.md`

---

## Notes for AI Assistants

When working on model comparison:

1. **Always work in the appropriate experiment branch**
2. **Don't modify main branch** during exploration
3. **Keep test cases consistent** across all models for fair comparison
4. **Document everything** - setup issues, surprises, workarounds
5. **Take screenshots** of visual results for comparison
6. **Stage changes but don't commit** - let user review
7. **Update this plan** if you discover new models or approaches

---

## Questions to Answer

By the end of this research, we should know:

- [ ] Which model handles color+motion best?
- [ ] Which model preserves hand-drawn style best?
- [ ] What are the integration complexity tradeoffs?
- [ ] Is any model worth switching from FILM?
- [ ] Should we use a hybrid approach?
- [ ] What's the path forward for Phase 2?

---

**Created**: 2025-10-27
**Status**: Planning - ready to begin experimentation
**Next Step**: Create `experiment/rife` branch and start testing
