# Phase 1 Testing Instructions

## Quick Start

Phase 1 implementation is complete! Here's how to test it:

### 1. Set Up Environment

```bash
# Activate virtual environment (already created)
source .venv/bin/activate

# Verify dependencies are installed
python3 -c "import langgraph; print('Dependencies OK')"
```

### 2. Set API Key

You'll need an Anthropic API key for Claude Vision analysis:

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
```

Or create a `.env` file:
```bash
echo "ANTHROPIC_API_KEY=sk-ant-api03-your-key-here" > .env
```

### 3. Run Test

```bash
python3 tests/test_telekinesis_phase1.py
```

### 4. View Results

```bash
# List generated frames
ls -la outputs/phase1_test/

# View frames (macOS)
open outputs/phase1_test/

# Or on Linux
xdg-open outputs/phase1_test/
```

---

## What to Expect

### Console Output

You should see output like this:

```
============================================================
PHASE 1 TEST: Telekinesis Minimal Viable Pipeline
============================================================

[SETUP] Using test images:
  Keyframe 1: .../tests/test_images/frame1.png
  Keyframe 2: .../tests/test_images/frame2.png

[1/6] Building Telekinesis graph...
  [DONE] Graph built successfully

[2/6] Creating initial state...
  [DONE] Initial state created

[3/6] Executing agent pipeline...
  This will take ~10-30 seconds...

  [1] ANALYZER agent completed
      Motion: translation
      Style: line_art
      Energy: medium
  [2] PRINCIPLES agent completed
      Principles: 3 identified
  [3] PLANNER agent completed
      Frames planned: 8
      Timing: linear
  [4] GENERATOR agent completed
      Frames generated: 8
      Files created: True
  [5] VALIDATOR agent completed
      Quality score: 8.0/10

[SUCCESS] Phase 1 Pipeline Test Passed!
```

### Generated Frames

You should see 8 PNG files in `outputs/phase1_test/`:
- `frame_000.png` - First keyframe (copy)
- `frame_001.png` - Interpolated frame (t=0.14)
- `frame_002.png` - Interpolated frame (t=0.29)
- `frame_003.png` - Interpolated frame (t=0.43)
- `frame_004.png` - Interpolated frame (t=0.57)
- `frame_005.png` - Interpolated frame (t=0.71)
- `frame_006.png` - Interpolated frame (t=0.86)
- `frame_007.png` - Second keyframe (copy)

### Quality Expectations

**IMPORTANT**: Phase 1 uses simple interpolation (alpha blending), so frames will be:
- Blurry and morphed (expected!)
- Linear motion (no arcs)
- No structural preservation
- Ghosting artifacts

This is **completely normal** for Phase 1. The goal is proving the pipeline works end-to-end.

Better quality comes in:
- Phase 3: AnimateDiff + ControlNet (structural guidance)
- Phase 4: Validation loop (quality checks)
- Phase 5: Squash/stretch deformation

---

## Troubleshooting

### Error: "ANTHROPIC_API_KEY not found"

**Solution**: Set the environment variable:
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### Error: "Module not found: langgraph"

**Solution**: Install dependencies:
```bash
source .venv/bin/activate
pip install -e .
```

### Error: "Test images not found"

**Solution**: Ensure you're running from project root:
```bash
cd /path/to/vizier/.conductor/jakarta
python3 tests/test_telekinesis_phase1.py
```

### Test passes but no frames on disk

**Possible causes**:
1. Generator failed but test didn't catch it
2. Permissions issue with `outputs/` directory
3. Wrong working directory

**Debug**:
```bash
# Check outputs directory
ls -la outputs/

# Try creating manually
mkdir -p outputs/phase1_test
chmod 755 outputs/phase1_test

# Run test with verbose logging
python3 tests/test_telekinesis_phase1.py 2>&1 | tee test_output.log
```

### Claude API errors

**Rate limiting**: Wait a few seconds and retry

**Invalid API key**: Check your key is correct and active

**Network errors**: Check internet connection

---

## What's Being Tested

### Agent Flow

1. **ANALYZER** (Phase 1 implemented)
   - Calls Claude Vision API
   - Analyzes both keyframes
   - Detects motion type, style, energy
   - Returns structured JSON analysis

2. **PRINCIPLES** (Phase 0 stub - unchanged)
   - Returns hardcoded principles (arc, slow_in_slow_out, timing)
   - No actual analysis (Phase 2 will add this)

3. **PLANNER** (Phase 0 stub - unchanged)
   - Creates simple 8-frame linear schedule
   - No arc calculations (Phase 3 will add this)

4. **GENERATOR** (Phase 1 implemented)
   - Loads both keyframes as RGBA
   - Interpolates linearly with alpha blending
   - Saves 8 PNG frames to disk
   - Preserves transparency

5. **VALIDATOR** (Phase 0 stub - unchanged)
   - Always returns quality score 8.0
   - No actual validation (Phase 4 will add this)

### Success Criteria

Test passes if:
- [X] Graph builds without errors
- [X] All 5 agents execute
- [X] Analysis contains Claude Vision results
- [X] 8 frames are generated
- [X] Frame files exist on disk
- [X] Frames are valid PNG images
- [X] Validation score is returned

---

## Next Steps After Testing

Once you confirm Phase 1 works:

1. **Review generated frames** - Check that interpolation looks reasonable
2. **Commit changes** - Review git diff and commit
3. **Plan Phase 2** - Start thinking about principle detection
4. **Optional**: Try different test images to see how analysis varies

### Phase 2 Preview

Phase 2 will add:
- Real principle detection (Claude analyzes which of 12 principles apply)
- Enhanced motion analysis (MediaPipe, optical flow)
- Principle-aware planning (different strategies for different motions)

---

## Test Images

The test uses images from `tests/test_images/`:
- `frame1.png` - Simple geometric shape (start position)
- `frame2.png` - Same shape in different position (end position)

You can test with your own images by modifying the test script:
```python
keyframe1 = str(Path("path/to/your/frame1.png"))
keyframe2 = str(Path("path/to/your/frame2.png"))
```

Best test images:
- Simple objects on transparent background
- Clear motion between frames
- PNG format with alpha channel
- 512-1024px resolution

---

## Performance Notes

**Typical execution time**: 10-30 seconds
- Claude Vision API: 5-10 seconds (2 calls)
- Frame generation: 2-5 seconds (8 frames)
- Other agents: < 1 second

**Cost per test run**: ~$0.01-0.02 (Claude API calls)

**Disk space**: ~5-10 MB per test (8 frames at ~1 MB each)

---

## Files Modified in Phase 1

### Created:
- `backend/app/services/claude_vision_service.py` - Vision analysis
- `backend/app/services/frame_generator_service.py` - Frame interpolation
- `tests/test_telekinesis_phase1.py` - This test script
- `docs/PHASE_1_TELEKINESIS_SUMMARY.md` - Detailed documentation
- `.venv/` - Virtual environment (gitignored)

### Modified:
- `backend/app/telekinesis/agents.py` - ANALYZER and GENERATOR
- `pyproject.toml` - Fixed dependency versions

### Unchanged:
- Graph structure (still works as designed)
- State schema (compatible)
- Other agents (PRINCIPLES, PLANNER, VALIDATOR, REFINER)

---

**Ready to test!** Run the command and see your first Telekinesis-generated animation frames!
