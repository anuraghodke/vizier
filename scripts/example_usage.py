#!/usr/bin/env python3
"""
Example usage of multi_frame_interpolation script.

This demonstrates different use cases for the multi-frame interpolation.
"""

import sys
from pathlib import Path

# Add parent directory to path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

from scripts.multi_frame_interpolation import generate_multi_frame_sequence

# ============================================================================
# EXAMPLE 1: Simple two-frame interpolation
# ============================================================================

def example_1_simple():
    """Generate 5 frames between 2 keyframes."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Simple interpolation (2 keyframes, 5 intermediate)")
    print("="*60)

    keyframes = [
        str(project_root / "tests/test_images/frame1.png"),
        str(project_root / "tests/test_images/frame2.png"),
    ]

    frame_counts = [5]  # 5 frames between the two keyframes

    generate_multi_frame_sequence(
        keyframe_paths=keyframes,
        frame_counts=frame_counts,
        output_dir="outputs/example_1_simple",
        timing_curve="linear"
    )


# ============================================================================
# EXAMPLE 2: Multi-keyframe with varying interpolation
# ============================================================================

def example_2_varying():
    """
    Demonstrate varying interpolation counts.

    This would use 4 keyframes with [1, 2, 0]:
    - 1 frame between keyframe 1 and 2
    - 2 frames between keyframe 2 and 3
    - 0 frames between keyframe 3 and 4
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Varying interpolation (4 keyframes)")
    print("="*60)

    # NOTE: This example would need 4 test images to work
    # For now, we'll just demonstrate the concept
    print("\nThis example requires 4 keyframe images.")
    print("To run this, create 4 keyframes and use:")
    print("""
    keyframes = [
        "path/to/keyframe1.png",
        "path/to/keyframe2.png",
        "path/to/keyframe3.png",
        "path/to/keyframe4.png",
    ]

    frame_counts = [1, 2, 0]

    generate_multi_frame_sequence(
        keyframe_paths=keyframes,
        frame_counts=frame_counts,
        output_dir="outputs/example_2_varying",
        timing_curve="ease-in-out"
    )
    """)


# ============================================================================
# EXAMPLE 3: Dense interpolation with easing
# ============================================================================

def example_3_dense():
    """Generate many frames with easing curve."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Dense interpolation with ease-in-out")
    print("="*60)

    keyframes = [
        str(project_root / "tests/test_images/frame1.png"),
        str(project_root / "tests/test_images/frame2.png"),
    ]

    frame_counts = [20]  # 20 frames for smooth motion

    generate_multi_frame_sequence(
        keyframe_paths=keyframes,
        frame_counts=frame_counts,
        output_dir="outputs/example_3_dense",
        timing_curve="ease-in-out"
    )


# ============================================================================
# EXAMPLE 4: No interpolation (direct cut)
# ============================================================================

def example_4_no_interpolation():
    """Demonstrate using 0 frames for direct cuts."""
    print("\n" + "="*60)
    print("EXAMPLE 4: No interpolation (direct cuts)")
    print("="*60)

    keyframes = [
        str(project_root / "tests/test_images/frame1.png"),
        str(project_root / "tests/test_images/frame2.png"),
    ]

    frame_counts = [0]  # 0 frames = direct cut, no interpolation

    generate_multi_frame_sequence(
        keyframe_paths=keyframes,
        frame_counts=frame_counts,
        output_dir="outputs/example_4_no_interpolation",
        timing_curve="linear"
    )


# ============================================================================
# Main menu
# ============================================================================

if __name__ == "__main__":
    print("\nMulti-Frame Interpolation Examples")
    print("===================================\n")
    print("Select an example to run:")
    print("1. Simple interpolation (2 keyframes, 5 intermediate)")
    print("2. Varying interpolation (demonstrates concept)")
    print("3. Dense interpolation with easing (20 frames)")
    print("4. No interpolation (direct cuts)")
    print("5. Run all examples")
    print("0. Exit")

    choice = input("\nEnter your choice (0-5): ").strip()

    if choice == "1":
        example_1_simple()
    elif choice == "2":
        example_2_varying()
    elif choice == "3":
        example_3_dense()
    elif choice == "4":
        example_4_no_interpolation()
    elif choice == "5":
        example_1_simple()
        example_2_varying()
        example_3_dense()
        example_4_no_interpolation()
    elif choice == "0":
        print("Exiting.")
    else:
        print("Invalid choice.")
        sys.exit(1)

    print("\n" + "="*60)
    print("Examples complete!")
    print("="*60 + "\n")
