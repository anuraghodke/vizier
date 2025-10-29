#!/usr/bin/env python3
"""
Test script to validate RIFE's physics-based interpolation behavior.

This test verifies that RIFE produces motion-aware interpolation (objects move)
rather than simple crossfading (objects fade in/out).

Test Case: Red ball (left) → Blue ball (right)
Expected: Ball moves from left to right while changing color (purple in middle)
NOT Expected: Red ball fades out on left, blue ball fades in on right

This is a direct comparison to test_physics_interpolation.py which tests FILM.
"""

import os
import sys
import numpy as np
from PIL import Image, ImageDraw
import torch

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def create_ball_image(color, position, size=512, ball_radius=50):
    """
    Create an image with a solid colored ball at specified position.

    Args:
        color: RGB tuple (e.g., (255, 0, 0) for red)
        position: X coordinate for ball center
        size: Image size (square)
        ball_radius: Radius of the ball

    Returns:
        PIL Image with RGBA
    """
    # Create transparent background
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Draw solid ball at specified position (vertically centered)
    y_center = size // 2
    x_center = position

    # Draw circle
    left = x_center - ball_radius
    top = y_center - ball_radius
    right = x_center + ball_radius
    bottom = y_center + ball_radius

    draw.ellipse([left, top, right, bottom], fill=color + (255,))

    return img

def interpolate_with_rife(rife_service, rgb1, rgb2, alpha1, alpha2, t=0.5):
    """
    Interpolate between two frames using RIFE.

    Args:
        rife_service: RIFEService instance
        rgb1, rgb2: RGB arrays (H, W, 3)
        alpha1, alpha2: Alpha arrays (H, W)
        t: Interpolation time (0.0 to 1.0)

    Returns:
        PIL Image with RGBA
    """
    # Interpolate RGB with RIFE
    rgb_interp = rife_service._interpolate_single_frame(rgb1, rgb2, t)

    # Linearly interpolate alpha channel
    alpha_interp = (1 - t) * alpha1 + t * alpha2

    # Convert back to PIL
    rgb_uint8 = (rgb_interp * 255).astype(np.uint8)
    alpha_uint8 = (alpha_interp * 255).astype(np.uint8)

    # Combine RGBA
    rgba = np.dstack([rgb_uint8, alpha_uint8])

    return Image.fromarray(rgba, 'RGBA')

def analyze_interpolation_quality(frame1, frame2, interpolated):
    """
    Analyze if interpolation is physics-based (motion) or crossfade.

    Checks:
    1. Is there a single ball in the middle? (Good - motion)
    2. Are there two faint balls on left/right? (Bad - crossfade)
    3. Is the middle ball purple-ish? (Good - color interpolation)

    Args:
        frame1: PIL Image (red ball on left)
        frame2: PIL Image (blue ball on right)
        interpolated: PIL Image (interpolated frame)

    Returns:
        dict with analysis results
    """
    # Convert to numpy for analysis
    img_array = np.array(interpolated)

    # Split into thirds (left, middle, right)
    width = img_array.shape[1]
    left_third = img_array[:, :width//3, :]
    middle_third = img_array[:, width//3:2*width//3, :]
    right_third = img_array[:, 2*width//3:, :]

    # Count non-transparent pixels in each region (alpha > 128)
    left_pixels = np.sum(left_third[:, :, 3] > 128)
    middle_pixels = np.sum(middle_third[:, :, 3] > 128)
    right_pixels = np.sum(right_third[:, :, 3] > 128)

    total_pixels = left_pixels + middle_pixels + right_pixels

    # Calculate percentages
    left_pct = (left_pixels / total_pixels * 100) if total_pixels > 0 else 0
    middle_pct = (middle_pixels / total_pixels * 100) if total_pixels > 0 else 0
    right_pct = (right_pixels / total_pixels * 100) if total_pixels > 0 else 0

    # Analyze middle region color (where ball should be)
    middle_nonzero = middle_third[middle_third[:, :, 3] > 128]
    if len(middle_nonzero) > 0:
        avg_color = np.mean(middle_nonzero[:, :3], axis=0)
        avg_r, avg_g, avg_b = avg_color
    else:
        avg_r, avg_g, avg_b = 0, 0, 0

    # Determine if physics-based
    is_physics_based = middle_pct > 80  # Most pixels should be in middle
    is_crossfade = left_pct > 20 and right_pct > 20  # Pixels in both left/right = crossfade
    is_purple_ish = avg_r > 50 and avg_b > 50 and avg_g < 100  # Purple = red + blue

    return {
        'left_pct': left_pct,
        'middle_pct': middle_pct,
        'right_pct': right_pct,
        'avg_color': (avg_r, avg_g, avg_b),
        'is_physics_based': is_physics_based,
        'is_crossfade': is_crossfade,
        'is_purple_ish': is_purple_ish,
        'quality': 'GOOD' if is_physics_based and not is_crossfade else 'BAD'
    }

def main():
    print("=" * 60)
    print("RIFE Physics-Based Interpolation Test")
    print("=" * 60)
    print()

    # Create output directory
    output_dir = 'test_images/rife/physics_test'
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Create test images
    print("Step 1: Creating test images...")
    print("  - Red ball at x=128 (left)")
    print("  - Blue ball at x=384 (right)")
    print()

    frame1 = create_ball_image(color=(255, 0, 0), position=128)  # Red, left
    frame2 = create_ball_image(color=(0, 0, 255), position=384)  # Blue, right

    frame1.save(f'{output_dir}/frame1_red_left.png')
    frame2.save(f'{output_dir}/frame2_blue_right.png')

    # Step 2: Load RIFE model
    print("Step 2: Loading RIFE model...")
    from backend.app.services.rife_service import RIFEService
    rife_service = RIFEService()
    print("  Model loaded successfully")
    print()

    # Step 3: Preprocess images
    print("Step 3: Preprocessing images...")
    rgb1, alpha1 = rife_service.preprocess_image(f'{output_dir}/frame1_red_left.png')
    rgb2, alpha2 = rife_service.preprocess_image(f'{output_dir}/frame2_blue_right.png')
    print(f"  Frame 1 shape: {rgb1.shape}, alpha: {alpha1.shape}")
    print(f"  Frame 2 shape: {rgb2.shape}, alpha: {alpha2.shape}")
    print()

    # Step 4: Interpolate at t=0.5 (middle)
    print("Step 4: Running RIFE interpolation at t=0.5...")
    interpolated = interpolate_with_rife(rife_service, rgb1, rgb2, alpha1, alpha2, t=0.5)
    interpolated.save(f'{output_dir}/frame_interpolated_t0.5.png')
    print("  Interpolation complete")
    print()

    # Step 5: Analyze results
    print("Step 5: Analyzing interpolation quality...")
    analysis = analyze_interpolation_quality(frame1, frame2, interpolated)

    print("  Pixel Distribution:")
    print(f"    Left third:   {analysis['left_pct']:.1f}%")
    print(f"    Middle third: {analysis['middle_pct']:.1f}%")
    print(f"    Right third:  {analysis['right_pct']:.1f}%")
    print()

    print(f"  Average color in middle: RGB({analysis['avg_color'][0]:.0f}, {analysis['avg_color'][1]:.0f}, {analysis['avg_color'][2]:.0f})")
    print(f"  Is purple-ish? {analysis['is_purple_ish']}")
    print()

    print(f"  Is physics-based? {analysis['is_physics_based']}")
    print(f"  Is crossfade? {analysis['is_crossfade']}")
    print()

    print("=" * 60)
    print(f"RESULT: {analysis['quality']}")
    print("=" * 60)

    if analysis['quality'] == 'GOOD':
        print("✅ RIFE produces physics-based interpolation!")
        print("   The ball moved from left to right and changed color.")
    else:
        print("❌ RIFE produced crossfade, not motion.")
        print("   Similar to FILM's behavior.")

    print()
    print(f"Output saved to: {output_dir}/")
    print("  - frame1_red_left.png")
    print("  - frame2_blue_right.png")
    print("  - frame_interpolated_t0.5.png")
    print()

    # Step 6: Generate additional interpolation steps
    print("Step 6: Generating full sequence (0.0 to 1.0)...")
    for i, t in enumerate([0.0, 0.25, 0.5, 0.75, 1.0]):
        if t == 0.0:
            img = frame1
        elif t == 1.0:
            img = frame2
        else:
            img = interpolate_with_rife(rife_service, rgb1, rgb2, alpha1, alpha2, t=t)

        img.save(f'{output_dir}/sequence_frame_{i}_t{t:.2f}.png')
        print(f"  Frame {i} (t={t:.2f}) saved")

    print()
    print("Full sequence saved. Open these files to visually verify smooth motion.")

if __name__ == '__main__':
    main()
