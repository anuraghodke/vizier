"""
Test FILM with actual PNG images including transparency.
This will help us understand how to preserve alpha channels.
"""
import os
import numpy as np
from PIL import Image, ImageDraw
import tensorflow as tf
import tensorflow_hub as hub

print("Creating test images with transparency...")

# Create test directory
os.makedirs("test_images", exist_ok=True)

# Create Frame 1: Red circle on transparent background
img1 = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
draw1 = ImageDraw.Draw(img1)
draw1.ellipse([50, 256-50, 200, 256+50], fill=(255, 0, 0, 255))  # Red circle on left
img1.save("test_images/frame1.png")
print("✓ Frame 1 saved: Red circle on left")

# Create Frame 2: Blue circle on transparent background
img2 = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
draw2 = ImageDraw.Draw(img2)
draw2.ellipse([312, 256-50, 462, 256+50], fill=(0, 0, 255, 255))  # Blue circle on right
img2.save("test_images/frame2.png")
print("✓ Frame 2 saved: Blue circle on right")

print("\nLoading FILM model...")
model = hub.load("https://tfhub.dev/google/film/1")
print("✓ Model loaded")

print("\nLoading images...")
# Load images with PIL to handle transparency
pil_img1 = Image.open("test_images/frame1.png").convert('RGBA')
pil_img2 = Image.open("test_images/frame2.png").convert('RGBA')

print(f"Image 1 mode: {pil_img1.mode}, size: {pil_img1.size}")
print(f"Image 2 mode: {pil_img2.mode}, size: {pil_img2.size}")

# Extract RGB and alpha channels
rgb1 = np.array(pil_img1.convert('RGB')).astype(np.float32) / 255.0
rgb2 = np.array(pil_img2.convert('RGB')).astype(np.float32) / 255.0
alpha1 = np.array(pil_img1.split()[3]).astype(np.float32) / 255.0
alpha2 = np.array(pil_img2.split()[3]).astype(np.float32) / 255.0

print(f"RGB shapes: {rgb1.shape}, {rgb2.shape}")
print(f"Alpha shapes: {alpha1.shape}, {alpha2.shape}")

# Add batch dimension
rgb1_batch = np.expand_dims(rgb1, axis=0)
rgb2_batch = np.expand_dims(rgb2, axis=0)

print("\nInterpolating frames...")
# Generate 3 intermediate frames (at t=0.25, 0.5, 0.75)
interpolated_frames = []
alpha_frames = []

for i, t in enumerate([0.25, 0.5, 0.75]):
    print(f"  Generating frame at t={t}...")

    # Interpolate RGB channels
    inputs = {
        'x0': tf.constant(rgb1_batch),
        'x1': tf.constant(rgb2_batch),
        'time': tf.constant([[t]], dtype=tf.float32)
    }
    result = model(inputs)
    interpolated_rgb = result['image'][0].numpy()

    # Interpolate alpha channel linearly (simple approach)
    interpolated_alpha = (1 - t) * alpha1 + t * alpha2

    # Combine RGB and alpha
    interpolated_rgba = np.dstack([
        (interpolated_rgb * 255).clip(0, 255).astype(np.uint8),
        (interpolated_alpha * 255).clip(0, 255).astype(np.uint8)
    ])

    # Save frame
    output_img = Image.fromarray(interpolated_rgba, mode='RGBA')
    output_path = f"test_images/interpolated_{i+1}_t{t:.2f}.png"
    output_img.save(output_path)
    print(f"  ✓ Saved: {output_path}")

print("\n✅ Test complete!")
print("\nGenerated frames:")
print("  test_images/frame1.png (original)")
for i, t in enumerate([0.25, 0.5, 0.75]):
    print(f"  test_images/interpolated_{i+1}_t{t:.2f}.png")
print("  test_images/frame2.png (original)")
print("\nNote: FILM processes RGB only. Alpha channel was interpolated linearly.")
print("For production, we'll need to handle alpha channel preservation carefully.")
