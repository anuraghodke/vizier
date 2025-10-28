"""
Simple test script to verify FILM model can be loaded and used.
This will download the model from TensorFlow Hub automatically.
"""
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

print("TensorFlow version:", tf.__version__)
print("Testing FILM model setup...")

try:
    # Load FILM model from TensorFlow Hub
    print("Loading FILM model from TensorFlow Hub...")
    model = hub.load("https://tfhub.dev/google/film/1")
    print("✓ FILM model loaded successfully!")

    # Create dummy test images (256x256x3)
    print("\nCreating test images...")
    img1 = tf.random.uniform([1, 256, 256, 3], 0, 1, dtype=tf.float32)
    img2 = tf.random.uniform([1, 256, 256, 3], 0, 1, dtype=tf.float32)
    print(f"Image 1 shape: {img1.shape}")
    print(f"Image 2 shape: {img2.shape}")

    # Test interpolation
    print("\nTesting interpolation...")
    batch_dt = tf.constant([[0.5]], dtype=tf.float32)  # Middle frame at t=0.5

    # FILM expects a dictionary input with 'x0', 'x1', 'time'
    inputs = {
        'x0': img1,
        'x1': img2,
        'time': batch_dt
    }
    result = model(inputs)

    print(f"✓ Interpolated frame shape: {result['image'][0].shape}")
    print(f"✓ Output range: [{result['image'][0].numpy().min():.3f}, {result['image'][0].numpy().max():.3f}]")

    print("\n✅ FILM setup complete and working!")
    print("\nNote: Model has been cached by TensorFlow Hub.")
    print("Location: ~/.cache/tensorflow_hub/ or similar")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure you have installed:")
    print("  pip install tensorflow tensorflow-hub")
