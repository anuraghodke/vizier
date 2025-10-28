#!/usr/bin/env python3
"""
Test FILM with same-colored ball moving (no color change).

This isolates MOTION from COLOR CHANGE to see if FILM can track
a single object moving across the frame.
"""

import os
import numpy as np
from PIL import Image, ImageDraw
import tensorflow as tf
import tensorflow_hub as hub

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

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

def interpolate_with_film(model, rgb1, rgb2, t=0.5):
    """Interpolate between two frames using FILM."""
    rgb1_batch = tf.convert_to_tensor(np.array(rgb1)[tf.newaxis, ...].astype(np.float32) / 255.0)
    rgb2_batch = tf.convert_to_tensor(np.array(rgb2)[tf.newaxis, ...].astype(np.float32) / 255.0)
    time_batch = tf.convert_to_tensor([[t]], dtype=tf.float32)

    result = model({
        'x0': rgb1_batch,
        'x1': rgb2_batch,
        'time': time_batch
    })

    rgb_interp = result['image'][0].numpy()
    rgb_interp = np.clip(rgb_interp, 0.0, 1.0)
    rgb_uint8 = (rgb_interp * 255).astype(np.uint8)

    return Image.fromarray(rgb_uint8, 'RGB')

def analyze_center_of_mass(img, bg_color=(255, 255, 255)):
    """Find center of mass of non-background pixels."""
    img_array = np.array(img)

    # Mask for non-background pixels
    bg_threshold = 20  # Pixels within 20 of background color
    diff = np.abs(img_array.astype(int) - np.array(bg_color).astype(int))
    is_object = np.sum(diff, axis=2) > bg_threshold

    if not np.any(is_object):
        return None, 0

    # Find center of mass
    y_coords, x_coords = np.where(is_object)
    center_x = np.mean(x_coords)
    center_y = np.mean(y_coords)
    num_pixels = len(x_coords)

    return (center_x, center_y), num_pixels

def main():
    print("=" * 70)
    print("FILM Test: Same Color Motion (Isolate Motion from Color Change)")
    print("=" * 70)
    print()

    output_dir = 'test_images/same_color_motion'
    os.makedirs(output_dir, exist_ok=True)

    print("Loading FILM model...")
    model = hub.load('https://tfhub.dev/google/film/1')
    print("Model loaded")
    print()

    # Test 1: Red ball moving (same color)
    print("Test 1: RED ball moving from left to right")
    print("-" * 70)

    frame1_red = create_ball_with_background(color=(255, 0, 0), position=128)
    frame2_red = create_ball_with_background(color=(255, 0, 0), position=384)

    frame1_red.save(f'{output_dir}/red_left.png')
    frame2_red.save(f'{output_dir}/red_right.png')

    print("Interpolating...")
    interpolated_red = interpolate_with_film(model, frame1_red, frame2_red, t=0.5)
    interpolated_red.save(f'{output_dir}/red_interpolated.png')

    center_red, pixels_red = analyze_center_of_mass(interpolated_red)
    expected_center = 256  # Middle of 512px image

    if center_red:
        print(f"  Ball center: x={center_red[0]:.1f}, y={center_red[1]:.1f}")
        print(f"  Expected x: {expected_center}")
        print(f"  Deviation: {abs(center_red[0] - expected_center):.1f}px")
        print(f"  Total pixels: {pixels_red}")

        if abs(center_red[0] - expected_center) < 50:
            print(f"  ✅ GOOD: Ball is centered (physics-based motion)")
        else:
            print(f"  ❌ BAD: Ball is not centered (likely crossfade)")
    print()

    # Test 2: Blue ball moving (same color)
    print("Test 2: BLUE ball moving from left to right")
    print("-" * 70)

    frame1_blue = create_ball_with_background(color=(0, 0, 255), position=128)
    frame2_blue = create_ball_with_background(color=(0, 0, 255), position=384)

    frame1_blue.save(f'{output_dir}/blue_left.png')
    frame2_blue.save(f'{output_dir}/blue_right.png')

    print("Interpolating...")
    interpolated_blue = interpolate_with_film(model, frame1_blue, frame2_blue, t=0.5)
    interpolated_blue.save(f'{output_dir}/blue_interpolated.png')

    center_blue, pixels_blue = analyze_center_of_mass(interpolated_blue)

    if center_blue:
        print(f"  Ball center: x={center_blue[0]:.1f}, y={center_blue[1]:.1f}")
        print(f"  Expected x: {expected_center}")
        print(f"  Deviation: {abs(center_blue[0] - expected_center):.1f}px")
        print(f"  Total pixels: {pixels_blue}")

        if abs(center_blue[0] - expected_center) < 50:
            print(f"  ✅ GOOD: Ball is centered (physics-based motion)")
        else:
            print(f"  ❌ BAD: Ball is not centered (likely crossfade)")
    print()

    # Test 3: For comparison - Red to Blue (color change)
    print("Test 3: RED to BLUE (position AND color change)")
    print("-" * 70)

    print("Interpolating...")
    interpolated_mixed = interpolate_with_film(model, frame1_red, frame2_blue, t=0.5)
    interpolated_mixed.save(f'{output_dir}/red_to_blue_interpolated.png')

    center_mixed, pixels_mixed = analyze_center_of_mass(interpolated_mixed)

    if center_mixed:
        print(f"  Ball center: x={center_mixed[0]:.1f}, y={center_mixed[1]:.1f}")
        print(f"  Expected x: {expected_center}")
        print(f"  Deviation: {abs(center_mixed[0] - expected_center):.1f}px")
        print(f"  Total pixels: {pixels_mixed}")

        if abs(center_mixed[0] - expected_center) < 50:
            print(f"  ✅ GOOD: Ball is centered")
        else:
            print(f"  ❌ BAD: Ball is not centered")
    print()

    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print("If same-color motion produces a centered ball, then FILM CAN track motion")
    print("but struggles when position + color change simultaneously.")
    print()
    print(f"Images saved to: {output_dir}/")

if __name__ == '__main__':
    main()
