"""
Frame generation service for Telekinesis system.

Phase 1: Simple linear interpolation (blending)
Future phases will integrate:
- AnimateDiff for motion-aware generation
- ControlNet for structural guidance
- Deformation/squash-stretch
"""
import os
import numpy as np
from pathlib import Path
from PIL import Image
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class FrameGeneratorService:
    """
    Service for generating intermediate frames between keyframes.

    Phase 1: Uses simple alpha-blending interpolation
    Phase 2+: Will integrate AnimateDiff, ControlNet, etc.
    """

    def __init__(self, output_dir: str = "outputs"):
        """
        Initialize frame generator.

        Args:
            output_dir: Base directory for output frames
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def _load_image(self, image_path: str) -> np.ndarray:
        """
        Load image as RGBA numpy array.

        Args:
            image_path: Path to image file

        Returns:
            RGBA numpy array (0-255, uint8)
        """
        img = Image.open(image_path)

        # Convert to RGBA if not already
        if img.mode != "RGBA":
            if img.mode == "RGB":
                # Add full opacity alpha channel
                img = img.convert("RGBA")
            elif img.mode == "L":
                # Grayscale - convert to RGBA
                img = img.convert("RGBA")
            else:
                # Other modes - convert via RGB
                img = img.convert("RGB").convert("RGBA")

        return np.array(img, dtype=np.uint8)

    def _save_image(self, array: np.ndarray, output_path: str) -> None:
        """
        Save numpy array as PNG image.

        Args:
            array: RGBA numpy array (0-255, uint8)
            output_path: Path to save image
        """
        # Ensure output directory exists
        Path(output_path).parent.mkdir(exist_ok=True, parents=True)

        # Convert to PIL and save
        img = Image.fromarray(array, mode="RGBA")
        img.save(output_path, format="PNG")
        logger.debug(f"Saved frame: {output_path}")

    def _interpolate_linear(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray,
        t: float
    ) -> np.ndarray:
        """
        Simple linear interpolation between two frames.

        Args:
            frame1: First keyframe (RGBA)
            frame2: Second keyframe (RGBA)
            t: Interpolation parameter (0.0 = frame1, 1.0 = frame2)

        Returns:
            Interpolated frame (RGBA)
        """
        # Ensure same shape
        if frame1.shape != frame2.shape:
            # Resize frame2 to match frame1
            img2 = Image.fromarray(frame2, mode="RGBA")
            img2_resized = img2.resize(
                (frame1.shape[1], frame1.shape[0]),
                Image.Resampling.LANCZOS
            )
            frame2 = np.array(img2_resized, dtype=np.uint8)

        # Linear blend
        # Convert to float for interpolation
        f1 = frame1.astype(np.float32)
        f2 = frame2.astype(np.float32)

        # Interpolate
        interpolated = (1.0 - t) * f1 + t * f2

        # Clip and convert back to uint8
        interpolated = np.clip(interpolated, 0, 255).astype(np.uint8)

        return interpolated

    def _apply_easing(self, t: float, curve_type: str = "linear") -> float:
        """
        Apply easing function to interpolation parameter.

        Args:
            t: Linear parameter (0-1)
            curve_type: Type of easing curve

        Returns:
            Eased parameter (0-1)
        """
        if curve_type == "linear":
            return t
        elif curve_type == "ease-in-out":
            # Cubic ease-in-out
            if t < 0.5:
                return 4 * t * t * t
            else:
                p = 2 * t - 2
                return 1 + 0.5 * p * p * p
        elif curve_type == "ease-in":
            # Quadratic ease-in
            return t * t
        elif curve_type == "ease-out":
            # Quadratic ease-out
            return t * (2 - t)
        else:
            # Default to linear
            return t

    def generate_frames(
        self,
        keyframe1_path: str,
        keyframe2_path: str,
        plan: Dict[str, Any],
        job_id: str = "test_job"
    ) -> List[str]:
        """
        Generate intermediate frames based on plan.

        Phase 1: Simple linear interpolation with easing
        Future: AnimateDiff generation with ControlNet guidance

        Args:
            keyframe1_path: Path to first keyframe
            keyframe2_path: Path to second keyframe
            plan: Generation plan from PLANNER agent
            job_id: Job ID for output directory

        Returns:
            List of generated frame paths
        """
        logger.info(f"GENERATOR: Starting frame generation for job {job_id}")

        # Load keyframes
        try:
            kf1 = self._load_image(keyframe1_path)
            kf2 = self._load_image(keyframe2_path)
        except Exception as e:
            logger.error(f"Failed to load keyframes: {e}")
            raise ValueError(f"Could not load keyframe images: {e}")

        # Extract plan parameters
        num_frames = plan.get("num_frames", 8)
        timing_curve = plan.get("timing_curve", "linear")
        frame_schedule = plan.get("frame_schedule", [])

        # Create output directory for this job
        job_output_dir = self.output_dir / job_id
        job_output_dir.mkdir(exist_ok=True, parents=True)

        generated_frames = []

        # Generate frames according to schedule
        for i, frame_info in enumerate(frame_schedule):
            # Get interpolation parameter
            t_linear = frame_info.get("t", i / (num_frames - 1) if num_frames > 1 else 0.0)

            # Apply easing curve
            t_eased = self._apply_easing(t_linear, timing_curve)

            # Generate frame
            if t_eased == 0.0:
                # First keyframe
                interpolated = kf1.copy()
            elif t_eased == 1.0:
                # Second keyframe
                interpolated = kf2.copy()
            else:
                # Interpolate
                interpolated = self._interpolate_linear(kf1, kf2, t_eased)

            # Save frame
            frame_filename = f"frame_{i:03d}.png"
            frame_path = str(job_output_dir / frame_filename)
            self._save_image(interpolated, frame_path)

            generated_frames.append(frame_path)

            logger.debug(
                f"Generated frame {i+1}/{num_frames}: "
                f"t_linear={t_linear:.3f}, t_eased={t_eased:.3f}"
            )

        logger.info(
            f"GENERATOR: Completed {len(generated_frames)} frames "
            f"with {timing_curve} timing"
        )

        return generated_frames


# Singleton instance (optional, for convenience)
_generator_service_instance = None


def get_generator_service(output_dir: str = "outputs") -> FrameGeneratorService:
    """
    Get or create singleton frame generator service instance.

    Args:
        output_dir: Base directory for output frames

    Returns:
        FrameGeneratorService instance
    """
    global _generator_service_instance
    if _generator_service_instance is None:
        _generator_service_instance = FrameGeneratorService(output_dir=output_dir)
    return _generator_service_instance
