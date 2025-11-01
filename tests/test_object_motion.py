"""
Test object-based motion interpolation without needing Claude API.

This test verifies:
1. Object detection works (finds red and blue balls)
2. Position and color extraction works
3. Frame rendering produces actual motion (not fading)
"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.services.frame_generator_service import FrameGeneratorService
from PIL import Image
import numpy as np


def test_object_detection():
    """Test that we can detect objects in keyframes"""
    print("\n" + "=" * 60)
    print("TEST: Object Detection and Motion Interpolation")
    print("=" * 60)

    # Setup paths
    test_dir = Path(__file__).parent
    test_images_dir = test_dir / "test_images"
    keyframe1 = str(test_images_dir / "frame1.png")
    keyframe2 = str(test_images_dir / "frame2.png")

    print(f"\n[1/5] Loading keyframes...")
    print(f"  Frame 1: {keyframe1}")
    print(f"  Frame 2: {keyframe2}")

    # Create generator service
    generator = FrameGeneratorService(output_dir="outputs")

    # Load images
    kf1 = generator._load_image(keyframe1)
    kf2 = generator._load_image(keyframe2)
    print(f"  [DONE] Loaded {kf1.shape} and {kf2.shape}")

    # Detect objects
    print(f"\n[2/5] Detecting objects...")
    obj1 = generator._detect_object(kf1)
    obj2 = generator._detect_object(kf2)

    if obj1 is None or obj2 is None:
        print("  [ERROR] Failed to detect objects")
        return False

    print(f"  [DONE] Object 1 detected:")
    print(f"    Position: {obj1['centroid']}")
    print(f"    Color: RGB{obj1['color']}")
    print(f"    Bbox: {obj1['bbox']}")

    print(f"  [DONE] Object 2 detected:")
    print(f"    Position: {obj2['centroid']}")
    print(f"    Color: RGB{obj2['color']}")
    print(f"    Bbox: {obj2['bbox']}")

    # Verify objects are in different positions
    x1, y1 = obj1['centroid']
    x2, y2 = obj2['centroid']
    distance = ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5

    print(f"\n[3/5] Analyzing motion...")
    print(f"  Distance between objects: {distance:.1f} pixels")

    if distance < 10:
        print("  [WARNING] Objects are very close - expected them to be far apart")
        return False

    # Verify colors are different
    r1, g1, b1 = obj1['color']
    r2, g2, b2 = obj2['color']
    color_diff = abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)

    print(f"  Color difference: {color_diff}")
    if color_diff < 50:
        print("  [WARNING] Colors are very similar - expected red and blue")
        return False

    # Generate test frames
    print(f"\n[4/5] Generating interpolated frames...")
    output_dir = Path("outputs") / "object_motion_test"
    output_dir.mkdir(parents=True, exist_ok=True)

    test_frames = []
    for i, t in enumerate([0.0, 0.25, 0.5, 0.75, 1.0]):
        if t == 0.0:
            frame = kf1.copy()
        elif t == 1.0:
            frame = kf2.copy()
        else:
            frame = generator._render_object_frame(
                (kf1.shape[0], kf1.shape[1]),
                obj1, obj2, t
            )

        frame_path = output_dir / f"test_frame_{i}_t{t:.2f}.png"
        generator._save_image(frame, str(frame_path))
        test_frames.append(frame_path)
        print(f"  Generated: {frame_path.name}")

    print(f"  [DONE] Generated {len(test_frames)} frames")

    # Verify frames show motion (not fading)
    print(f"\n[5/5] Verifying motion (not fading)...")

    # Load middle frame
    middle_frame = np.array(Image.open(test_frames[2]))
    rgb = middle_frame[:, :, :3]
    alpha = middle_frame[:, :, 3]

    # Check for object at middle position
    expected_x = int((x1 + x2) / 2)
    expected_y = int((y1 + y2) / 2)

    # Sample a region around expected position
    sample_region = rgb[
        max(0, expected_y-20):min(rgb.shape[0], expected_y+20),
        max(0, expected_x-20):min(rgb.shape[1], expected_x+20)
    ]

    # Check if we have colored pixels there (not white)
    non_white = np.any(sample_region < 240, axis=2)
    colored_pixel_count = np.sum(non_white)

    print(f"  Expected middle position: ({expected_x}, {expected_y})")
    print(f"  Colored pixels in region: {colored_pixel_count}")

    if colored_pixel_count < 100:
        print("  [ERROR] No object found at middle position - likely fading issue")
        return False

    # Check that corners are white (not ghosted)
    corners = [
        rgb[0:50, 0:50],           # Top-left
        rgb[0:50, -50:],           # Top-right
        rgb[-50:, 0:50],           # Bottom-left
        rgb[-50:, -50:]            # Bottom-right
    ]

    for i, corner in enumerate(corners):
        white_pixels = np.all(corner > 240, axis=2)
        white_percentage = np.sum(white_pixels) / white_pixels.size * 100
        print(f"  Corner {i+1} white percentage: {white_percentage:.1f}%")

        if white_percentage < 80:
            print(f"  [WARNING] Corner {i+1} has ghosting artifacts")

    print("\n" + "=" * 60)
    print("[SUCCESS] Object-Based Motion Test Passed!")
    print("=" * 60)
    print("\nResults:")
    print("  - Objects detected correctly")
    print("  - Position and color extracted")
    print("  - Frames show MOTION (not fading)")
    print(f"  - Output: {output_dir}")
    print("\nVerify visually:")
    print(f"  open {output_dir}")
    print()

    return True


if __name__ == "__main__":
    success = test_object_detection()
    sys.exit(0 if success else 1)
