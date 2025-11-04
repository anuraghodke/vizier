#!/usr/bin/env python3
"""
Multi-Frame Interpolation Script

Upload multiple keyframe images and specify the number of frames to generate
between each consecutive pair.

Example usage:
    # For 4 keyframes with [1, 2, 0] interpolation counts:
    # - 1 frame between keyframe 1 and 2
    # - 2 frames between keyframe 2 and 3
    # - 0 frames between keyframe 3 and 4

    python scripts/multi_frame_interpolation.py
"""

import sys
import os
from pathlib import Path
from typing import List
import logging

# Add parent directory to path for imports
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

from backend.app.services.frame_generator_service import FrameGeneratorService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_inputs(keyframe_paths: List[str], frame_counts: List[int]) -> None:
    """
    Validate input parameters.

    Args:
        keyframe_paths: List of paths to keyframe images
        frame_counts: List of frame counts between each pair

    Raises:
        ValueError: If validation fails
    """
    if len(keyframe_paths) < 2:
        raise ValueError(f"Need at least 2 keyframes, got {len(keyframe_paths)}")

    if len(frame_counts) != len(keyframe_paths) - 1:
        raise ValueError(
            f"frame_counts length ({len(frame_counts)}) must be "
            f"keyframe_paths length - 1 ({len(keyframe_paths) - 1})"
        )

    for i, path in enumerate(keyframe_paths):
        if not os.path.exists(path):
            raise ValueError(f"Keyframe {i+1} not found: {path}")

    for i, count in enumerate(frame_counts):
        if count < 0:
            raise ValueError(f"frame_counts[{i}] must be >= 0, got {count}")


def generate_multi_frame_sequence(
    keyframe_paths: List[str],
    frame_counts: List[int],
    output_dir: str = "outputs/multi_frame_sequence",
    timing_curve: str = "linear"
) -> List[str]:
    """
    Generate interpolated frames between multiple keyframes.

    Args:
        keyframe_paths: List of n keyframe image paths
        frame_counts: List of n-1 integers specifying frames between each pair
        output_dir: Directory to save output frames
        timing_curve: Easing curve (linear, ease-in-out, ease-in, ease-out)

    Returns:
        List of all generated frame paths (including keyframes)

    Example:
        keyframe_paths = ["kf1.png", "kf2.png", "kf3.png", "kf4.png"]
        frame_counts = [1, 2, 0]

        Results in sequence:
        - kf1.png (frame_000.png)
        - interpolated frame (frame_001.png)
        - kf2.png (frame_002.png)
        - interpolated frame 1 (frame_003.png)
        - interpolated frame 2 (frame_004.png)
        - kf3.png (frame_005.png)
        - kf4.png (frame_006.png)
    """
    # Validate inputs
    validate_inputs(keyframe_paths, frame_counts)

    logger.info(f"Starting multi-frame interpolation:")
    logger.info(f"  Keyframes: {len(keyframe_paths)}")
    logger.info(f"  Frame counts: {frame_counts}")
    logger.info(f"  Output directory: {output_dir}")
    logger.info(f"  Timing curve: {timing_curve}")

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)

    # Initialize frame generator service
    service = FrameGeneratorService()

    # Track all frames in final sequence
    all_frames = []
    frame_counter = 0

    # Process each pair of consecutive keyframes
    for pair_idx in range(len(keyframe_paths) - 1):
        keyframe1 = keyframe_paths[pair_idx]
        keyframe2 = keyframe_paths[pair_idx + 1]
        num_intermediate = frame_counts[pair_idx]

        logger.info(
            f"\nProcessing pair {pair_idx + 1}/{len(keyframe_paths) - 1}: "
            f"{Path(keyframe1).name} -> {Path(keyframe2).name}"
        )
        logger.info(f"  Intermediate frames: {num_intermediate}")

        if num_intermediate == 0:
            # No interpolation, just add the first keyframe
            # (second keyframe will be added in next iteration or at end)
            logger.info(f"  Copying keyframe 1 only (0 intermediate frames)")

            # Copy first keyframe to output
            from PIL import Image
            img = Image.open(keyframe1)
            frame_path = str(output_path / f"frame_{frame_counter:03d}.png")
            img.save(frame_path)
            all_frames.append(frame_path)
            frame_counter += 1

        else:
            # Generate intermediate frames
            # Total frames = keyframe1 + intermediate + keyframe2
            total_frames_in_segment = num_intermediate + 2

            # Create frame schedule for this segment
            frame_schedule = []
            for i in range(total_frames_in_segment):
                t = i / (total_frames_in_segment - 1)
                frame_schedule.append({"t": t})

            # Create plan for generator
            plan = {
                "num_frames": total_frames_in_segment,
                "timing_curve": timing_curve,
                "frame_schedule": frame_schedule
            }

            # Generate frames for this pair
            temp_job_id = f"pair_{pair_idx}"
            try:
                segment_frames = service.generate_frames(
                    keyframe1_path=keyframe1,
                    keyframe2_path=keyframe2,
                    plan=plan,
                    job_id=temp_job_id
                )

                logger.info(f"  Generated {len(segment_frames)} frames for this segment")

                # Copy frames to main output directory with sequential numbering
                from PIL import Image
                for seg_frame_path in segment_frames:
                    img = Image.open(seg_frame_path)
                    frame_path = str(output_path / f"frame_{frame_counter:03d}.png")
                    img.save(frame_path)
                    all_frames.append(frame_path)
                    frame_counter += 1

            except Exception as e:
                logger.error(f"Failed to generate frames for pair {pair_idx + 1}: {e}")
                raise

    # Add the final keyframe (if not already added)
    # Check if we need to add the last keyframe
    # This happens when the last segment had num_intermediate > 0
    # (the last keyframe is already included in segment_frames)
    # OR when the last segment had num_intermediate == 0
    # (we need to add it manually)

    if frame_counts[-1] == 0:
        # Last segment had 0 intermediate frames, add final keyframe
        from PIL import Image
        img = Image.open(keyframe_paths[-1])
        frame_path = str(output_path / f"frame_{frame_counter:03d}.png")
        img.save(frame_path)
        all_frames.append(frame_path)
        frame_counter += 1

    logger.info(f"\n{'='*60}")
    logger.info(f"Multi-frame interpolation complete!")
    logger.info(f"Total frames generated: {len(all_frames)}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"{'='*60}\n")

    # Print frame list
    logger.info("Frame sequence:")
    for i, frame in enumerate(all_frames):
        logger.info(f"  {i}: {Path(frame).name}")

    return all_frames


# ============================================================================
# CONFIGURATION - EDIT THESE VARIABLES
# ============================================================================

# Specify your keyframe image paths (absolute or relative to project root)
KEYFRAME_PATHS = [
    "tests/test_images/frame1.png",
    "tests/test_images/frame2.png",
    # Add more keyframes here...
    # "tests/test_images/frame3.png",
    # "tests/test_images/frame4.png",
]

# Specify number of frames to generate between each consecutive pair
# Length must be len(KEYFRAME_PATHS) - 1
FRAME_COUNTS = [
    5,  # Number of frames between keyframe 1 and 2
    # Add more counts here corresponding to each pair...
    # 2,  # Number of frames between keyframe 2 and 3
    # 0,  # Number of frames between keyframe 3 and 4
]

# Output directory for generated sequence
OUTPUT_DIR = "outputs/my_interpolation_sequence"

# Timing curve: "linear", "ease-in-out", "ease-in", "ease-out"
TIMING_CURVE = "linear"

# ============================================================================


if __name__ == "__main__":
    """
    Run the multi-frame interpolation with the configured parameters.

    Edit the configuration variables above to specify your keyframes and
    interpolation settings.
    """

    # Convert relative paths to absolute paths
    absolute_keyframe_paths = []
    for path in KEYFRAME_PATHS:
        if not os.path.isabs(path):
            path = str(project_root / path)
        absolute_keyframe_paths.append(path)

    try:
        # Run interpolation
        generated_frames = generate_multi_frame_sequence(
            keyframe_paths=absolute_keyframe_paths,
            frame_counts=FRAME_COUNTS,
            output_dir=OUTPUT_DIR,
            timing_curve=TIMING_CURVE
        )

        print("\nSuccess! Generated frames:")
        for frame in generated_frames:
            print(f"  {frame}")

    except Exception as e:
        logger.error(f"Interpolation failed: {e}")
        sys.exit(1)
