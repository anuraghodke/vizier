#!/usr/bin/env python3
"""
Test RIFE with solid background to see if it produces better motion.

Hypothesis: RIFE (like FILM) may treat transparent backgrounds as "nothing", so objects
appearing in different locations look like separate objects fading in/out.

With a solid background, RIFE should see the scene as continuous and track
the object's motion properly.

Direct comparison to test_physics_with_background.py which tests FILM.
"""

import os
import sys
import numpy as np
from PIL import Image, ImageDraw
import torch

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def create_ball_with_background(color, position, size=512, ball_radius=50, bg_color=(255, 255, 255)):
    """Create image with colored ball on solid background."""
    img = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(img)

    y_center = size // 2
    x_center = position

    left = x_center - ball_radius
    top = y_center - ball_radius
    right = x_center + ball_radius
    bottom = y_center + ball_radius

    draw.ellipse([left, top, right, bottom], fill=color)

    return img

def interpolate_with_rife(rife_service, rgb1, rgb2, t=0.5):
    """Interpolate between two frames using RIFE."""
    result = rife_service._interpolate_single_frame(rgb1, rgb2, t)
    rgb_uint8 = (result * 255).astype(np.uint8)
    return Image.fromarray(rgb_uint8, 'RGB')

def analyze_interpolation(img):
    """Analyze where the ball is in the interpolated image."""
    img_array = np.array(img)

    # Split into thirds
    width = img_array.shape[1]
    left_third = img_array[:, :width//3, :]
    middle_third = img_array[:, width//3:2*width//3, :]
    right_third = img_array[:, 2*width//3:, :]

    # Count non-white pixels (assume background is white)
    def count_non_white(region):
        # Pixel is non-white if any channel is < 250
        non_white = np.any(region < 250, axis=2)
        return np.sum(non_white)

    left_pixels = count_non_white(left_third)
    middle_pixels = count_non_white(middle_third)
    right_pixels = count_non_white(right_third)

    total = left_pixels + middle_pixels + right_pixels

    if total > 0:
        left_pct = (left_pixels / total * 100)
        middle_pct = (middle_pixels / total * 100)
        right_pct = (right_pixels / total * 100)
    else:
        left_pct = middle_pct = right_pct = 0

    # Get average color in middle third (where ball should be)
    middle_non_white = middle_third[np.any(middle_third < 250, axis=2)]
    if len(middle_non_white) > 0:
        avg_color = np.mean(middle_non_white, axis=0)
    else:
        avg_color = np.array([255, 255, 255])

    # Physics-based: most pixels in middle, purple-ish color
    is_physics = middle_pct > 70
    is_crossfade = left_pct > 20 and right_pct > 20
    is_purple_ish = avg_color[0] > 80 and avg_color[2] > 80 and avg_color[1] < 150

    return {
        'left_pct': left_pct,
        'middle_pct': middle_pct,
        'right_pct': right_pct,
        'avg_color': tuple(avg_color),
        'is_physics': is_physics,
        'is_crossfade': is_crossfade,
        'is_purple_ish': is_purple_ish,
        'quality': 'GOOD - Physics-based!' if is_physics and not is_crossfade else 'BAD - Crossfade'
    }

def main():
    print("=" * 70)
    print("RIFE Test: White Background (Should Enable Motion Tracking)")
    print("=" * 70)
    print()

    output_dir = 'test_images/rife/physics_with_background'
    os.makedirs(output_dir, exist_ok=True)

    # Test 1: White background
    print("Test 1: White Background")
    print("-" * 70)

    frame1 = create_ball_with_background(color=(255, 0, 0), position=128, bg_color=(255, 255, 255))
    frame2 = create_ball_with_background(color=(0, 0, 255), position=384, bg_color=(255, 255, 255))

    frame1.save(f'{output_dir}/white_bg_frame1.png')
    frame2.save(f'{output_dir}/white_bg_frame2.png')

    print("Loading RIFE model...")
    from backend.app.services.rife_service import RIFEService
    rife_service = RIFEService()
    print("Model loaded")
    print()

    rgb1, _ = rife_service.preprocess_image(f'{output_dir}/white_bg_frame1.png')
    rgb2, _ = rife_service.preprocess_image(f'{output_dir}/white_bg_frame2.png')

    print("Interpolating at t=0.5...")
    interpolated = interpolate_with_rife(rife_service, rgb1, rgb2, t=0.5)
    interpolated.save(f'{output_dir}/white_bg_interpolated.png')

    analysis = analyze_interpolation(interpolated)

    print(f"  Left:   {analysis['left_pct']:.1f}%")
    print(f"  Middle: {analysis['middle_pct']:.1f}%")
    print(f"  Right:  {analysis['right_pct']:.1f}%")
    print(f"  Color:  RGB{tuple(int(c) for c in analysis['avg_color'])}")
    print(f"  Result: {analysis['quality']}")
    print()

    # Test 2: Gray background
    print("Test 2: Gray Background")
    print("-" * 70)

    frame1_gray = create_ball_with_background(color=(255, 0, 0), position=128, bg_color=(128, 128, 128))
    frame2_gray = create_ball_with_background(color=(0, 0, 255), position=384, bg_color=(128, 128, 128))

    frame1_gray.save(f'{output_dir}/gray_bg_frame1.png')
    frame2_gray.save(f'{output_dir}/gray_bg_frame2.png')

    rgb1_gray, _ = rife_service.preprocess_image(f'{output_dir}/gray_bg_frame1.png')
    rgb2_gray, _ = rife_service.preprocess_image(f'{output_dir}/gray_bg_frame2.png')

    print("Interpolating at t=0.5...")
    interpolated_gray = interpolate_with_rife(rife_service, rgb1_gray, rgb2_gray, t=0.5)
    interpolated_gray.save(f'{output_dir}/gray_bg_interpolated.png')

    analysis_gray = analyze_interpolation(interpolated_gray)

    print(f"  Left:   {analysis_gray['left_pct']:.1f}%")
    print(f"  Middle: {analysis_gray['middle_pct']:.1f}%")
    print(f"  Right:  {analysis_gray['right_pct']:.1f}%")
    print(f"  Color:  RGB{tuple(int(c) for c in analysis_gray['avg_color'])}")
    print(f"  Result: {analysis_gray['quality']}")
    print()

    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    if analysis['is_physics']:
        print("✅ WHITE BACKGROUND: Physics-based motion detected!")
        print("   RIFE successfully tracked the ball's motion.")
    else:
        print("❌ WHITE BACKGROUND: Still producing crossfade.")
        print("   RIFE is not tracking motion even with solid background.")

    print()

    if analysis_gray['is_physics']:
        print("✅ GRAY BACKGROUND: Physics-based motion detected!")
    else:
        print("❌ GRAY BACKGROUND: Still producing crossfade.")

    print()
    print(f"Images saved to: {output_dir}/")

if __name__ == '__main__':
    main()
