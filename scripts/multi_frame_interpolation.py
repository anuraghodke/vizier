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
import re
from pathlib import Path
from typing import List, Optional
import logging
import typer

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

# Create typer app
app = typer.Typer(help="Multi-frame interpolation tool for generating frames between keyframe images.")


def generate_output_directory(keyframe_folder: str, base_output_dir: str = "outputs") -> str:
    """
    Generate an auto-incrementing output directory name.

    Args:
        keyframe_folder: Path to the keyframe folder
        base_output_dir: Base directory for outputs (default: "outputs")

    Returns:
        Path like "outputs/bouncing_ball_001", "outputs/bouncing_ball_002", etc.

    Example:
        keyframe_folder = "tests/test_images/bouncing_ball"
        -> returns "outputs/bouncing_ball_001" (or next available number)
    """
    # Extract folder name from path
    folder_name = Path(keyframe_folder).name

    # Find existing numbered outputs for this folder
    base_path = Path(base_output_dir)
    base_path.mkdir(exist_ok=True, parents=True)

    # Find all directories matching the pattern: {folder_name}_###
    pattern = f"{folder_name}_*"
    existing = [d for d in base_path.glob(pattern) if d.is_dir()]

    # Extract numbers from existing directories
    numbers = []
    for d in existing:
        # Extract the number suffix (e.g., "bouncing_ball_003" -> 3)
        suffix = d.name[len(folder_name) + 1:]  # +1 for underscore
        if suffix.isdigit():
            numbers.append(int(suffix))

    # Find next available number
    next_num = 1 if not numbers else max(numbers) + 1

    # Format with zero padding (3 digits)
    output_name = f"{folder_name}_{next_num:03d}"
    output_path = base_path / output_name

    logger.info(f"Auto-generated output directory: {output_path}")

    return str(output_path)


def load_keyframes_from_folder(folder_path: str) -> List[str]:
    """
    Load and sort keyframe images from a folder.

    Expects files to be enumerated with trailing numbers (e.g., frame-1.png, frame-2.png).
    Supports common image formats: png, jpg, jpeg, webp.

    Args:
        folder_path: Path to folder containing keyframe images

    Returns:
        Sorted list of absolute paths to keyframe images

    Raises:
        ValueError: If folder doesn't exist or contains no valid images
    """
    folder = Path(folder_path)

    if not folder.exists():
        raise ValueError(f"Folder not found: {folder_path}")

    if not folder.is_dir():
        raise ValueError(f"Path is not a directory: {folder_path}")

    # Supported image extensions
    image_extensions = {'.png', '.jpg', '.jpeg', '.webp'}

    # Find all image files
    image_files = [
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]

    if not image_files:
        raise ValueError(f"No image files found in folder: {folder_path}")

    # Sort files by trailing number
    def extract_number(filepath: Path) -> int:
        """Extract the trailing number from filename for sorting."""
        # Remove extension and get the stem
        stem = filepath.stem
        # Find trailing number in the filename
        match = re.search(r'(\d+)$', stem)
        if match:
            return int(match.group(1))
        # If no trailing number, use 0 (will sort to beginning)
        logger.warning(f"No trailing number found in {filepath.name}, sorting to beginning")
        return 0

    # Sort by trailing number
    sorted_files = sorted(image_files, key=extract_number)

    logger.info(f"Found {len(sorted_files)} keyframes in {folder_path}:")
    for i, f in enumerate(sorted_files):
        logger.info(f"  {i+1}. {f.name}")

    return [str(f.absolute()) for f in sorted_files]


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
                # Skip the last frame (second keyframe) unless this is the last pair
                # The second keyframe will be the first frame of the next pair
                from PIL import Image
                is_last_pair = (pair_idx == len(keyframe_paths) - 2)
                frames_to_copy = segment_frames if is_last_pair else segment_frames[:-1]

                logger.info(f"  Copying {len(frames_to_copy)} frames to output (excluding duplicate keyframe)" if not is_last_pair else f"  Copying all {len(frames_to_copy)} frames to output (last pair)")

                for seg_frame_path in frames_to_copy:
                    img = Image.open(seg_frame_path)
                    frame_path = str(output_path / f"frame_{frame_counter:03d}.png")
                    img.save(frame_path)
                    all_frames.append(frame_path)
                    frame_counter += 1

            except Exception as e:
                logger.error(f"Failed to generate frames for pair {pair_idx + 1}: {e}")
                raise

    # Add the final keyframe if the last segment had 0 intermediate frames
    # (For segments with num_intermediate > 0, the final keyframe was already added above)
    if frame_counts[-1] == 0:
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

# Specify folder containing keyframe images (absolute or relative to project root)
# Images should be enumerated with trailing numbers (e.g., frame-1.png, frame-2.png)
KEYFRAME_FOLDER = "tests/test_images/bouncing_ball"

# Specify number of frames to generate between each consecutive pair
# Option 1: Use a single value (applies to all pairs)
FRAMES_BETWEEN = 1

# Option 2: Use an array to specify different counts for each pair
# Length must be (number of keyframes) - 1
# If set, this overrides FRAMES_BETWEEN
# Example: For 4 keyframes, [1, 5, 2] means:
#   - 1 frame between keyframes 1 and 2
#   - 5 frames between keyframes 2 and 3
#   - 2 frames between keyframes 3 and 4
FRAME_COUNTS = None

# Output directory for generated sequence
# Set to None to auto-generate based on input folder name (e.g., "outputs/bouncing_ball_001")
# Or specify a custom path like "outputs/my_custom_output"
OUTPUT_DIR = None

# Timing curve: "linear", "ease-in-out", "ease-in", "ease-out"
TIMING_CURVE = "ease-in-out"

# ============================================================================


@app.command()
def main(
    keyframe_folder: str = typer.Argument(
        ...,
        help="Folder containing keyframe images (enumerated with trailing numbers, e.g., frame-1.png, frame-2.png)"
    ),
    output_dir: Optional[str] = typer.Option(
        None,
        "--output-dir", "-o",
        help="Output directory for generated frames (default: auto-generated based on input folder)"
    ),
    frames_between: Optional[int] = typer.Option(
        None,
        "--frames-between", "-n",
        help="Number of frames to generate between each keyframe pair (default: 1)"
    ),
    frame_counts: Optional[List[int]] = typer.Option(
        None,
        "--frame-counts", "-c",
        help="Array of frame counts for each pair (e.g., -c 1 -c 5 -c 2). Overrides --frames-between."
    ),
    timing_curve: str = typer.Option(
        "linear",
        "--timing-curve", "-t",
        help="Timing curve for interpolation: linear, ease-in-out, ease-in, ease-out"
    ),
):
    """
    Generate interpolated frames between multiple keyframe images.

    Loads keyframe images from KEYFRAME_FOLDER (sorted by trailing number)
    and generates interpolated frames between each consecutive pair.

    Examples:
        # Uniform spacing (5 frames between each pair)
        python scripts/multi_frame_interpolation.py tests/test_images/bouncing_ball -n 5 -o outputs/bouncing_ball

        # Custom spacing for each pair
        python scripts/multi_frame_interpolation.py tests/test_images/bouncing_ball -c 1 -c 5 -c 2 -o outputs/bouncing_ball
    """
    # Convert relative folder path to absolute
    folder_path = keyframe_folder
    if not os.path.isabs(folder_path):
        folder_path = str(project_root / folder_path)

    try:
        # Load keyframes from folder
        logger.info("Loading keyframes from folder...")
        keyframe_paths = load_keyframes_from_folder(folder_path)

        # Determine output directory (auto-generate if not specified)
        if output_dir is None:
            output_dir = generate_output_directory(folder_path)
        else:
            logger.info(f"Using specified output directory: {output_dir}")

        # Determine frame counts
        if frame_counts is not None:
            # Use custom array
            counts = frame_counts
            logger.info(f"Using custom frame counts: {counts}")
        elif frames_between is not None:
            # Use uniform spacing
            counts = [frames_between] * (len(keyframe_paths) - 1)
            logger.info(f"Generating {frames_between} frame(s) between each keyframe pair")
        else:
            # Default to 1
            counts = [1] * (len(keyframe_paths) - 1)
            logger.info(f"Generating 1 frame between each keyframe pair (default)")

        # Run interpolation
        generated_frames = generate_multi_frame_sequence(
            keyframe_paths=keyframe_paths,
            frame_counts=counts,
            output_dir=output_dir,
            timing_curve=timing_curve
        )

        typer.echo("\nSuccess! Generated frames:")
        for frame in generated_frames:
            typer.echo(f"  {frame}")

    except Exception as e:
        logger.error(f"Interpolation failed: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    # If no CLI arguments provided, use configuration variables
    # Otherwise, use typer CLI
    if len(sys.argv) == 1:
        # Running with no arguments - use config variables
        folder_path = KEYFRAME_FOLDER
        if not os.path.isabs(folder_path):
            folder_path = str(project_root / folder_path)

        try:
            logger.info("Using configuration from script variables...")
            logger.info(f"  KEYFRAME_FOLDER: {KEYFRAME_FOLDER}")
            logger.info(f"  FRAMES_BETWEEN: {FRAMES_BETWEEN}")
            logger.info(f"  OUTPUT_DIR: {OUTPUT_DIR}")
            logger.info(f"  TIMING_CURVE: {TIMING_CURVE}")

            # Load keyframes from folder
            logger.info("\nLoading keyframes from folder...")
            keyframe_paths = load_keyframes_from_folder(folder_path)

            # Determine output directory (auto-generate if not specified)
            output_dir = OUTPUT_DIR
            if output_dir is None:
                output_dir = generate_output_directory(folder_path)
            else:
                logger.info(f"Using specified output directory: {output_dir}")

            # Determine frame counts
            if FRAME_COUNTS is not None:
                frame_counts = FRAME_COUNTS
                logger.info(f"Using custom frame counts: {frame_counts}")
            else:
                frame_counts = [FRAMES_BETWEEN] * (len(keyframe_paths) - 1)
                logger.info(f"Generating {FRAMES_BETWEEN} frame(s) between each keyframe pair")

            # Run interpolation
            generated_frames = generate_multi_frame_sequence(
                keyframe_paths=keyframe_paths,
                frame_counts=frame_counts,
                output_dir=output_dir,
                timing_curve=TIMING_CURVE
            )

            print("\nSuccess! Generated frames:")
            for frame in generated_frames:
                print(f"  {frame}")

        except Exception as e:
            logger.error(f"Interpolation failed: {e}")
            sys.exit(1)
    else:
        # Use typer CLI
        app()
