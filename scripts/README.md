# Multi-Frame Interpolation Script

Generate interpolated frames between multiple keyframe images using AI-powered motion analysis.

## Quick Start

### CLI Usage (Recommended)

```bash
# Basic usage with auto-generated output directory
python scripts/multi_frame_interpolation.py tests/test_images/bouncing_ball

# Specify number of frames between each pair
python scripts/multi_frame_interpolation.py tests/test_images/bouncing_ball --frames-between 5

# Custom output directory
python scripts/multi_frame_interpolation.py tests/test_images/bouncing_ball --output-dir outputs/my_animation

# Custom frame counts for each pair (4 keyframes = 3 pairs)
python scripts/multi_frame_interpolation.py tests/test_images/bouncing_ball -c 1 -c 5 -c 2

# With easing curve
python scripts/multi_frame_interpolation.py tests/test_images/bouncing_ball -n 3 -t ease-in-out

# Get help
python scripts/multi_frame_interpolation.py --help
```

### Configuration File Usage (Alternative)

If you prefer not to use CLI arguments, you can edit the configuration variables at the bottom of the script and run without arguments:

1. Edit `scripts/multi_frame_interpolation.py`:

```python
KEYFRAME_FOLDER = "tests/test_images/bouncing_ball"
FRAMES_BETWEEN = 1
FRAME_COUNTS = None  # or [1, 5, 2] for custom counts
OUTPUT_DIR = None    # Auto-generate or specify path
TIMING_CURVE = "linear"
```

2. Run:

```bash
python scripts/multi_frame_interpolation.py
```

## CLI Arguments

### Positional Arguments

- `keyframe_folder` (required): Folder containing keyframe images
  - Images should have trailing numbers (e.g., `frame-1.png`, `frame-2.png`, `ball_001.png`)
  - Supported formats: PNG, JPG, JPEG, WEBP

### Options

- `--output-dir`, `-o`: Output directory for generated frames
  - Default: Auto-generated as `outputs/{folder_name}_001`, `outputs/{folder_name}_002`, etc.
  - Example: `-o outputs/my_animation`

- `--frames-between`, `-n`: Number of frames between each keyframe pair (uniform)
  - Default: 1
  - Example: `-n 5` generates 5 frames between each pair

- `--frame-counts`, `-c`: Custom frame counts for each pair (overrides `--frames-between`)
  - Specify once per pair (for N keyframes, need N-1 values)
  - Example: For 4 keyframes: `-c 1 -c 5 -c 2`

- `--timing-curve`, `-t`: Easing function for interpolation
  - Options: `linear`, `ease-in-out`, `ease-in`, `ease-out`
  - Default: `linear`

## Examples

### Example 1: Bouncing Ball with 5 Frames Between Each

```bash
python scripts/multi_frame_interpolation.py tests/test_images/bouncing_ball -n 5
```

**Output**: `outputs/bouncing_ball_001/frame_000.png` ... `frame_030.png` (for 7 keyframes)

### Example 2: Custom Frame Counts

Given 4 keyframes in `tests/test_images/walk_cycle`:

```bash
python scripts/multi_frame_interpolation.py tests/test_images/walk_cycle -c 1 -c 5 -c 2
```

**Result**:
- 1 frame between keyframes 1 and 2
- 5 frames between keyframes 2 and 3
- 2 frames between keyframes 3 and 4

**Total frames**: 4 (keyframes) + 1 + 5 + 2 = 12 frames

### Example 3: Ease-In-Out Timing

```bash
python scripts/multi_frame_interpolation.py tests/test_images/bouncing_ball -n 3 -t ease-in-out
```

Frames will move slowly at start/end, faster in the middle.

### Example 4: Custom Output Directory

```bash
python scripts/multi_frame_interpolation.py tests/test_images/bouncing_ball -n 5 -o outputs/bouncing_animation_v2
```

Saves frames to `outputs/bouncing_animation_v2/` instead of auto-generated path.

## Folder Structure Requirements

### Input Folder

Keyframe images must have **trailing numbers** in their filenames. The script automatically sorts files by these numbers.

**Supported formats**: `.png`, `.jpg`, `.jpeg`, `.webp`

**Examples**:
```
Good:
  frame-1.png
  frame-2.png
  frame-3.png
  frame-4.png

Also Good:
  ball_001.png
  ball_002.png
  ball_003.png

Also Good:
  bouncing-ball-1.png
  bouncing-ball-2.png
  bouncing-ball-10.png  <- Sorted correctly as 10, not between 1 and 2

Bad (no trailing numbers):
  frame_a.png
  frame_b.png
```

### Output Directory

**Auto-generated (default)**:
- First run: `outputs/bouncing_ball_001/`
- Second run: `outputs/bouncing_ball_002/`
- Third run: `outputs/bouncing_ball_003/`
- Pattern: `outputs/{folder_name}_{number}/`

**Custom (specified with `-o`)**:
- Example: `outputs/my_custom_animation/`

## Output

The script generates:
1. Sequential PNG frames named `frame_000.png`, `frame_001.png`, etc.
2. Console output showing:
   - Discovered keyframes in order
   - Frame generation progress
   - Final frame mapping
3. All frames saved in the output directory

## Image Requirements

- **Format**: PNG (preferred), JPG, JPEG, WEBP
- **Transparency**: PNG with alpha channel works best
- **Size**: No strict limits, but consistent dimensions recommended
- **Content**: Works best with clear objects on transparent or solid backgrounds

## Timing Curves

Different easing functions create different motion feels:

- **linear**: Constant speed throughout (robotic)
- **ease-in-out**: Slow start, fast middle, slow end (natural)
- **ease-in**: Slow start, fast end (accelerating)
- **ease-out**: Fast start, slow end (decelerating)

## Troubleshooting

### "Folder not found"
- Check that the keyframe folder path is correct
- Use absolute paths or paths relative to project root
- Example: `python scripts/multi_frame_interpolation.py /full/path/to/keyframes`

### "No image files found in folder"
- Ensure folder contains PNG, JPG, JPEG, or WEBP files
- Check file extensions are lowercase (`.png` not `.PNG`)
- Verify files exist: `ls tests/test_images/bouncing_ball`

### "No trailing number found in filename"
- Files must have numbers at the end of their name (before extension)
- Good: `frame1.png`, `ball-05.png`, `key_003.png`
- Bad: `frame_a.png`, `1_ball.png` (number at start)

### "frame_counts length must be keyframe_paths length - 1"
- For N keyframes, you need exactly N-1 frame count values
- Example: 4 keyframes need 3 counts: `-c 1 -c 5 -c 2`
- Check how many keyframes were detected in console output

### "Could not detect moving objects in keyframes"
- Works best with objects on transparent backgrounds
- Try using PNG images with clear alpha channels
- Ensure objects have different positions/colors between keyframes
- Current implementation uses object-based interpolation (Phase 1)

## Technical Details

### Current Implementation (Phase 1)

The script uses **object-based motion interpolation**:
- Detects objects using color segmentation
- Interpolates object position and color
- Applies easing curves to timing

**Limitations**:
- No deformation/squash-stretch (coming in Phase 5)
- Works best with simple objects
- May not handle complex backgrounds well

### Future Enhancements

- AnimateDiff integration for motion-aware generation
- ControlNet for structural guidance
- Deformation and squash-stretch support
- Advanced principle detection

## Advanced Usage

### Using Both Config and CLI

CLI arguments override configuration file variables:

```python
# In script
KEYFRAME_FOLDER = "tests/test_images/bouncing_ball"
FRAMES_BETWEEN = 1
```

```bash
# Override FRAMES_BETWEEN via CLI
python scripts/multi_frame_interpolation.py tests/test_images/walk_cycle -n 5
```

Result: Uses `walk_cycle` folder with 5 frames between each pair.

### Zero Interpolation (Direct Cuts)

Use `0` in frame counts for no interpolation between certain pairs:

```bash
# 4 keyframes: interpolate between 1-2 and 3-4, but cut directly from 2-3
python scripts/multi_frame_interpolation.py tests/test_images/keyframes -c 5 -c 0 -c 5
```

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review console output for specific error messages
3. Verify keyframe folder structure and file naming
4. See project documentation in `docs/` directory
