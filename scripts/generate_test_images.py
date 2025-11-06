#!/usr/bin/env python3
"""
Generate test images for Phase 2 Telekinesis testing.

Phase 2 focuses on intelligent principle detection, so we need test images that
demonstrate various animation principles:
- Arc motion
- Translation
- Rotation
- Squash and stretch
- Color change with motion
"""

from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np


def create_simple_ball(size=(400, 400), ball_pos=(100, 200), ball_radius=40, ball_color=(255, 0, 0)):
    """Create a simple colored ball on a transparent background"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw ball with anti-aliasing simulation (multiple circles with alpha)
    x, y = ball_pos
    for i in range(3):
        alpha = 255 - (i * 30)
        r = ball_radius - i
        color_with_alpha = (*ball_color, alpha)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=color_with_alpha)

    return img


def create_arc_motion_frames():
    """
    Create keyframes demonstrating arc motion (bouncing ball).
    This tests the PRINCIPLES agent's ability to detect arc motion.
    """
    print("Creating arc motion test frames...")
    output_dir = Path(__file__).parent.parent / "tests" / "test_images"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Frame 1: Ball at bottom left (start of arc)
    frame1 = create_simple_ball(
        size=(400, 400),
        ball_pos=(100, 320),  # Bottom left
        ball_radius=40,
        ball_color=(255, 100, 100)  # Red
    )
    frame1.save(output_dir / "arc_frame1.png")

    # Frame 2: Ball at top center (apex of arc)
    frame2 = create_simple_ball(
        size=(400, 400),
        ball_pos=(200, 100),  # Top center
        ball_radius=40,
        ball_color=(255, 150, 150)  # Lighter red
    )
    frame2.save(output_dir / "arc_frame2.png")

    print(f"  Saved: arc_frame1.png and arc_frame2.png")


def create_translation_frames():
    """
    Create keyframes demonstrating simple translation with color change.
    This is the basic test case from Phase 1.
    """
    print("Creating translation + color change frames...")
    output_dir = Path(__file__).parent.parent / "tests" / "test_images"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Frame 1: Red ball on left
    frame1 = create_simple_ball(
        size=(400, 400),
        ball_pos=(100, 200),
        ball_radius=40,
        ball_color=(255, 0, 0)  # Red
    )
    frame1.save(output_dir / "frame1.png")

    # Frame 2: Blue ball on right
    frame2 = create_simple_ball(
        size=(400, 400),
        ball_pos=(300, 200),
        ball_radius=40,
        ball_color=(0, 0, 255)  # Blue
    )
    frame2.save(output_dir / "frame2.png")

    print(f"  Saved: frame1.png and frame2.png")


def create_rotation_frame():
    """
    Create keyframes demonstrating rotation.
    Using a simple rectangle that rotates.
    """
    print("Creating rotation test frames...")
    output_dir = Path(__file__).parent.parent / "tests" / "test_images"
    output_dir.mkdir(parents=True, exist_ok=True)

    size = (400, 400)

    # Frame 1: Horizontal rectangle
    frame1 = Image.new('RGBA', size, (0, 0, 0, 0))
    draw1 = ImageDraw.Draw(frame1)
    center = (200, 200)
    # Draw horizontal rectangle
    draw1.rectangle([center[0]-60, center[1]-20, center[0]+60, center[1]+20],
                    fill=(100, 200, 100, 255))
    # Add a dot to show orientation
    draw1.ellipse([center[0]+40, center[1]-10, center[0]+50, center[1]],
                  fill=(255, 0, 0, 255))
    frame1.save(output_dir / "rotation_frame1.png")

    # Frame 2: Rotated rectangle (45 degrees)
    frame2 = Image.new('RGBA', size, (0, 0, 0, 0))
    # Create rotated version
    temp = Image.new('RGBA', size, (0, 0, 0, 0))
    draw2 = ImageDraw.Draw(temp)
    draw2.rectangle([center[0]-60, center[1]-20, center[0]+60, center[1]+20],
                    fill=(100, 200, 150, 255))
    draw2.ellipse([center[0]+40, center[1]-10, center[0]+50, center[1]],
                  fill=(255, 0, 0, 255))
    frame2 = temp.rotate(45, center=center, expand=False)
    frame2.save(output_dir / "rotation_frame2.png")

    print(f"  Saved: rotation_frame1.png and rotation_frame2.png")


def create_squash_stretch_frames():
    """
    Create keyframes demonstrating squash and stretch.
    Ball in normal state vs squashed state.
    """
    print("Creating squash/stretch test frames...")
    output_dir = Path(__file__).parent.parent / "tests" / "test_images"
    output_dir.mkdir(parents=True, exist_ok=True)

    size = (400, 400)

    # Frame 1: Normal round ball (at top)
    frame1 = Image.new('RGBA', size, (0, 0, 0, 0))
    draw1 = ImageDraw.Draw(frame1)
    center = (200, 100)
    radius = 40
    draw1.ellipse([center[0]-radius, center[1]-radius,
                   center[0]+radius, center[1]+radius],
                  fill=(255, 200, 0, 255))
    frame1.save(output_dir / "squash_frame1.png")

    # Frame 2: Squashed ball (at bottom, hitting ground)
    frame2 = Image.new('RGBA', size, (0, 0, 0, 0))
    draw2 = ImageDraw.Draw(frame2)
    center = (200, 330)
    # Squashed: wider, shorter
    draw2.ellipse([center[0]-55, center[1]-25,
                   center[0]+55, center[1]+25],
                  fill=(255, 200, 0, 255))
    # Add impact line
    draw2.line([50, 355, 350, 355], fill=(100, 100, 100, 200), width=3)
    frame2.save(output_dir / "squash_frame2.png")

    print(f"  Saved: squash_frame1.png and squash_frame2.png")


def create_scale_change_frames():
    """
    Create keyframes demonstrating scale change (depth simulation).
    Small object (far) to large object (near).
    """
    print("Creating scale change (depth) test frames...")
    output_dir = Path(__file__).parent.parent / "tests" / "test_images"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Frame 1: Small ball (far away)
    frame1 = create_simple_ball(
        size=(400, 400),
        ball_pos=(200, 200),
        ball_radius=20,  # Small
        ball_color=(150, 100, 255)
    )
    frame1.save(output_dir / "scale_frame1.png")

    # Frame 2: Large ball (close)
    frame2 = create_simple_ball(
        size=(400, 400),
        ball_pos=(200, 200),
        ball_radius=80,  # Large
        ball_color=(150, 100, 255)
    )
    frame2.save(output_dir / "scale_frame2.png")

    print(f"  Saved: scale_frame1.png and scale_frame2.png")


def create_readme():
    """Create a README explaining the test images"""
    output_dir = Path(__file__).parent.parent / "tests" / "test_images"

    readme_content = """# Test Images for Phase 2 - Intelligent Principles Detection

This directory contains test image pairs designed to test the PRINCIPLES agent's ability to detect which of the 12 animation principles apply to different types of motion.

## Test Image Sets

### 1. Basic Translation + Color Change
- `frame1.png` - Red ball on left
- `frame2.png` - Blue ball on right
- **Tests**: Translation, color interpolation
- **Expected Principles**: Slow in/slow out, timing

### 2. Arc Motion
- `arc_frame1.png` - Ball at bottom left
- `arc_frame2.png` - Ball at top center
- **Tests**: Arc detection, parabolic motion
- **Expected Principles**: Arc, slow in/slow out

### 3. Rotation
- `rotation_frame1.png` - Horizontal rectangle
- `rotation_frame2.png` - Rotated rectangle (45°)
- **Tests**: Rotational motion detection
- **Expected Principles**: Arc (rotation is circular), timing

### 4. Squash and Stretch
- `squash_frame1.png` - Round ball at top
- `squash_frame2.png` - Squashed ball at bottom
- **Tests**: Deformation detection, volume preservation
- **Expected Principles**: Squash and stretch, timing

### 5. Scale Change (Depth)
- `scale_frame1.png` - Small ball (far)
- `scale_frame2.png` - Large ball (near)
- **Tests**: Scale interpolation, depth simulation
- **Expected Principles**: Slow in/slow out, timing

## Usage

These images are used by:
- `tests/test_telekinesis_phase1.py` - Uses frame1.png and frame2.png
- `tests/test_object_motion.py` - Uses frame1.png and frame2.png
- Future phase 2 tests - Will use principle-specific image pairs

## Image Specifications

- **Format**: PNG with transparency (RGBA)
- **Size**: 400x400 pixels
- **Background**: Transparent
- **Objects**: Simple geometric shapes with solid colors
- **Style**: Clean, no anti-aliasing artifacts

## Regenerating Images

To regenerate these test images:

```bash
python scripts/generate_test_images.py
```

This will create all test image pairs in this directory.
"""

    readme_path = output_dir / "README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)

    print(f"  Saved: README.md")


def main():
    print("=" * 60)
    print("Generating Test Images for Phase 2")
    print("=" * 60)
    print()

    # Create all test image sets
    create_translation_frames()      # Basic: frame1.png, frame2.png
    create_arc_motion_frames()       # Arc motion test
    create_rotation_frame()          # Rotation test
    create_squash_stretch_frames()   # Squash/stretch test
    create_scale_change_frames()     # Scale/depth test
    create_readme()                  # Documentation

    print()
    print("=" * 60)
    print("Test Image Generation Complete!")
    print("=" * 60)
    print()
    print("Generated image pairs:")
    print("  1. frame1.png / frame2.png - Translation + color")
    print("  2. arc_frame1.png / arc_frame2.png - Arc motion")
    print("  3. rotation_frame1.png / rotation_frame2.png - Rotation")
    print("  4. squash_frame1.png / squash_frame2.png - Squash/stretch")
    print("  5. scale_frame1.png / scale_frame2.png - Scale change")
    print()
    print("Location: tests/test_images/")
    print("See tests/test_images/README.md for details")


if __name__ == "__main__":
    main()
