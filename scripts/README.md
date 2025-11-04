# Multi-Frame Interpolation Script

This script allows you to upload multiple keyframe images and generate interpolated frames between each consecutive pair.

## Usage

### Basic Setup

1. Edit the configuration variables at the bottom of `multi_frame_interpolation.py`:

```python
# Specify your keyframe image paths
KEYFRAME_PATHS = [
    "path/to/keyframe1.png",
    "path/to/keyframe2.png",
    "path/to/keyframe3.png",
    "path/to/keyframe4.png",
]

# Specify frames between each consecutive pair
# Length must be len(KEYFRAME_PATHS) - 1
FRAME_COUNTS = [
    1,  # 1 frame between keyframe 1 and 2
    2,  # 2 frames between keyframe 2 and 3
    0,  # 0 frames between keyframe 3 and 4
]

# Output directory
OUTPUT_DIR = "outputs/my_sequence"

# Timing curve: "linear", "ease-in-out", "ease-in", "ease-out"
TIMING_CURVE = "linear"
```

2. Run the script:

```bash
python scripts/multi_frame_interpolation.py
```

## Example

Given 4 keyframes and `FRAME_COUNTS = [1, 2, 0]`:

```
Input:
  keyframe1.png
  keyframe2.png
  keyframe3.png
  keyframe4.png

FRAME_COUNTS = [1, 2, 0]

Output sequence:
  frame_000.png  <- keyframe1.png
  frame_001.png  <- interpolated between 1 and 2
  frame_002.png  <- keyframe2.png
  frame_003.png  <- interpolated 1/2 between 2 and 3
  frame_004.png  <- interpolated 2/2 between 2 and 3
  frame_005.png  <- keyframe3.png
  frame_006.png  <- keyframe4.png (no interpolation)
```

## Image Requirements

- **Format**: PNG (preferred), JPG, WEBP, or GIF
- **Transparency**: PNG with alpha channel works best
- **Size**: No strict limits, but consistent dimensions recommended
- **Content**: Works best with clear objects on transparent or solid backgrounds

## Parameters

### KEYFRAME_PATHS
- List of paths to your keyframe images
- Can be absolute or relative to project root
- Minimum: 2 keyframes
- Maximum: No hard limit (keep under ~20 for performance)

### FRAME_COUNTS
- List of integers specifying how many frames to generate between each pair
- Length must equal `len(KEYFRAME_PATHS) - 1`
- Each value can be 0 or greater
- Example: `[5, 10, 3]` for 4 keyframes

### OUTPUT_DIR
- Directory where generated frames will be saved
- Created automatically if it doesn't exist
- Default: `outputs/my_interpolation_sequence`

### TIMING_CURVE
- Easing function for interpolation
- Options:
  - `"linear"`: Constant speed
  - `"ease-in-out"`: Slow start and end, fast middle
  - `"ease-in"`: Slow start, fast end
  - `"ease-out"`: Fast start, slow end

## Output

The script generates:
1. Sequential PNG frames named `frame_000.png`, `frame_001.png`, etc.
2. Console output showing progress and frame mapping
3. All frames saved in the specified `OUTPUT_DIR`

## Troubleshooting

### "frame_counts length must be keyframe_paths length - 1"
- Make sure `FRAME_COUNTS` has exactly one fewer element than `KEYFRAME_PATHS`
- For 4 keyframes, you need 3 frame counts

### "Keyframe not found"
- Check that all paths in `KEYFRAME_PATHS` are correct
- Use absolute paths or paths relative to project root
- Verify files exist with `ls path/to/keyframe.png`

### "Could not detect moving objects in keyframes"
- The current implementation uses object detection for interpolation
- Works best with objects on transparent backgrounds
- Try using PNG images with clear alpha channels
