"""
RIFE (Real-time Intermediate Flow Estimation) service for Telekinesis system.

Phase 3: Neural frame interpolation using rife-ncnn-vulkan
- High-quality intermediate frame generation
- CPU-compatible via ncnn/Vulkan
- Custom timing support for easing curves

Uses the rife-ncnn-vulkan-python-tntwise package which provides:
- macOS ARM64 (Apple Silicon) support
- Python 3.9-3.13 compatibility
- Simple PIL-based API
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# Try to import RIFE - will fail gracefully if not installed
_RIFE_AVAILABLE = False
_Rife = None

try:
    from rife_ncnn_vulkan_python import Rife
    _Rife = Rife
    _RIFE_AVAILABLE = True
    logger.info("RIFE ncnn-vulkan loaded successfully")
except ImportError as e:
    logger.warning(f"RIFE not available: {e}. Install with: pip install rife-ncnn-vulkan-python-tntwise")


class RifeService:
    """
    Service for high-quality frame interpolation using RIFE.

    RIFE (Real-time Intermediate Flow Estimation) generates smooth
    intermediate frames between two input frames using neural
    optical flow estimation.

    Key features:
    - Works on CPU via ncnn/Vulkan backend
    - Handles arbitrary interpolation positions (0.0-1.0)
    - Preserves image quality better than simple blending
    - ~2-5 seconds per frame on modern CPU
    """

    def __init__(self, gpu_id: int = -1, model: str = "rife-v4.6"):
        """
        Initialize RIFE service.

        Args:
            gpu_id: GPU device ID (-1 for CPU, 0+ for GPU)
            model: RIFE model to use (default: rife-v4.6)
        """
        self.gpu_id = gpu_id
        self.model = model
        self._rife = None
        self._initialization_failed = False

        if not _RIFE_AVAILABLE:
            logger.warning(
                "RIFE not installed. Frame generation will fall back to "
                "simple interpolation. Install with: "
                "pip install rife-ncnn-vulkan-python-tntwise"
            )

    def _ensure_initialized(self) -> bool:
        """
        Lazily initialize RIFE model on first use.

        Returns:
            True if RIFE is available and initialized
        """
        if not _RIFE_AVAILABLE or self._initialization_failed:
            return False

        if self._rife is None:
            try:
                # Check if model files exist before attempting initialization
                # This prevents segfaults from missing model files
                import site
                from pathlib import Path
                site_packages = site.getsitepackages()
                model_found = False
                for sp in site_packages:
                    model_path = Path(sp) / "rife_ncnn_vulkan_python" / "models"
                    if model_path.exists():
                        model_found = True
                        break

                if not model_found:
                    logger.error(
                        "RIFE models not found. Please reinstall with: "
                        "pip install --force-reinstall rife-ncnn-vulkan-python-tntwise"
                    )
                    self._initialization_failed = True
                    return False

                # Initialize RIFE with specified GPU and model
                # gpu_id=-1 uses CPU, gpu_id=0+ uses that GPU
                self._rife = _Rife(gpuid=self.gpu_id, model=self.model)
                logger.info(f"RIFE initialized (gpu_id={self.gpu_id}, model={self.model})")
            except Exception as e:
                logger.error(f"Failed to initialize RIFE: {e}")
                self._initialization_failed = True
                return False

        return True

    def is_available(self) -> bool:
        """Check if RIFE is available for use."""
        if not _RIFE_AVAILABLE:
            return False
        # Try to initialize to see if it actually works
        return self._ensure_initialized()

    def _ensure_rgb_has_color(self, frame: np.ndarray) -> np.ndarray:
        """
        Fix images where RGB is black but alpha defines the shape.

        PNG images with transparency often have RGB=(0,0,0) for all pixels,
        relying on alpha to define the visible shape. This causes RIFE to
        interpolate black colors. This method extracts actual colors and
        applies them to the visible regions.

        Args:
            frame: RGBA numpy array (H, W, 4)

        Returns:
            Frame with RGB channels populated with actual colors
        """
        if frame.shape[2] != 4:
            return frame  # Not RGBA, no fix needed

        rgb = frame[:, :, :3]
        alpha = frame[:, :, 3]

        # Check if this looks like a transparent PNG with black RGB
        visible_pixels = alpha > 10  # Pixels that are somewhat visible
        if not visible_pixels.any():
            return frame  # No visible pixels

        rgb_visible = rgb[visible_pixels]
        mean_intensity = rgb_visible.mean()

        # If RGB is very dark (mean < 20) but alpha shows a shape, fix it
        if mean_intensity < 20 and visible_pixels.sum() > 100:
            # Extract non-black colors if any exist
            non_black = (rgb_visible.sum(axis=1) > 30)
            if non_black.any():
                # Use the median color of non-black pixels
                target_color = np.median(rgb_visible[non_black], axis=0).astype(np.uint8)
                logger.info(f"RIFE: Detected color {target_color} from non-black pixels")
            else:
                # Default to white if no color information
                target_color = np.array([255, 255, 255], dtype=np.uint8)
                logger.warning("RIFE: No color data found, using white as default")

            # Apply color to visible regions
            result = frame.copy()
            result[visible_pixels, :3] = target_color
            logger.info(f"RIFE: Fixed {visible_pixels.sum()} pixels from black to color")
            return result

        return frame

    def interpolate(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray,
        t: float = 0.5
    ) -> np.ndarray:
        """
        Generate a single intermediate frame at position t.

        Args:
            frame1: First frame as RGBA numpy array (H, W, 4)
            frame2: Second frame as RGBA numpy array (H, W, 4)
            t: Interpolation position (0.0 = frame1, 1.0 = frame2)

        Returns:
            Interpolated frame as RGBA numpy array (H, W, 4)
        """
        # Handle edge cases
        if t <= 0.0:
            return frame1.copy()
        if t >= 1.0:
            return frame2.copy()

        if not self._ensure_initialized():
            # Fallback to simple alpha blending if RIFE unavailable
            logger.warning("RIFE unavailable, using alpha blend fallback")
            return self._alpha_blend(frame1, frame2, t)

        try:
            # Fix transparent PNGs with black RGB data
            frame1 = self._ensure_rgb_has_color(frame1)
            frame2 = self._ensure_rgb_has_color(frame2)

            # RIFE expects RGB PIL images, handle RGBA
            alpha1 = frame1[:, :, 3] if frame1.shape[2] == 4 else None
            alpha2 = frame2[:, :, 3] if frame2.shape[2] == 4 else None

            # Convert to RGB PIL images
            rgb1 = frame1[:, :, :3]
            rgb2 = frame2[:, :, :3]

            # Debug logging for color values
            logger.debug(f"RIFE input frame1 RGB shape: {rgb1.shape}, dtype: {rgb1.dtype}, "
                        f"mean: {rgb1.mean():.1f}, min: {rgb1.min()}, max: {rgb1.max()}")
            logger.debug(f"RIFE input frame2 RGB shape: {rgb2.shape}, dtype: {rgb2.dtype}, "
                        f"mean: {rgb2.mean():.1f}, min: {rgb2.min()}, max: {rgb2.max()}")

            pil1 = Image.fromarray(rgb1, mode="RGB")
            pil2 = Image.fromarray(rgb2, mode="RGB")

            # RIFE interpolation
            # Note: rife-ncnn-vulkan-python uses timestep parameter
            # The process method interpolates at t=0.5 by default
            # For arbitrary t, we need to use the timestep parameter

            # The RIFE API varies between versions
            # Try timestep parameter first, fall back to default
            try:
                result_pil = self._rife.process(pil1, pil2, timestep=t)
            except TypeError:
                # Older API without timestep - generate at 0.5 and blend
                if t == 0.5:
                    result_pil = self._rife.process(pil1, pil2)
                else:
                    # Generate midpoint and blend toward target
                    mid_pil = self._rife.process(pil1, pil2)
                    mid_array = np.array(mid_pil)

                    if t < 0.5:
                        # Blend between frame1 and midpoint
                        blend_t = t * 2  # Map 0-0.5 to 0-1
                        result_array = self._alpha_blend_rgb(rgb1, mid_array, blend_t)
                    else:
                        # Blend between midpoint and frame2
                        blend_t = (t - 0.5) * 2  # Map 0.5-1 to 0-1
                        result_array = self._alpha_blend_rgb(mid_array, rgb2, blend_t)

                    result_pil = Image.fromarray(result_array, mode="RGB")

            # Convert back to numpy
            result_rgb = np.array(result_pil)

            # Debug logging for RIFE output
            logger.debug(f"RIFE output RGB shape: {result_rgb.shape}, dtype: {result_rgb.dtype}, "
                        f"mean: {result_rgb.mean():.1f}, min: {result_rgb.min()}, max: {result_rgb.max()}")

            # Handle alpha channel
            if alpha1 is not None or alpha2 is not None:
                # Interpolate alpha channel linearly
                if alpha1 is None:
                    alpha1 = np.full(frame1.shape[:2], 255, dtype=np.uint8)
                if alpha2 is None:
                    alpha2 = np.full(frame2.shape[:2], 255, dtype=np.uint8)

                alpha_interp = (1 - t) * alpha1.astype(float) + t * alpha2.astype(float)
                alpha_interp = alpha_interp.astype(np.uint8)

                # Combine RGB and alpha
                result = np.dstack([result_rgb, alpha_interp])
            else:
                # Add full opacity alpha if input was RGB
                alpha_full = np.full(result_rgb.shape[:2], 255, dtype=np.uint8)
                result = np.dstack([result_rgb, alpha_full])

            return result

        except Exception as e:
            logger.error(f"RIFE interpolation failed: {e}")
            logger.warning("Falling back to alpha blend")
            return self._alpha_blend(frame1, frame2, t)

    def interpolate_sequence(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray,
        t_values: List[float]
    ) -> List[np.ndarray]:
        """
        Generate multiple intermediate frames at specified positions.

        Args:
            frame1: First keyframe as RGBA numpy array
            frame2: Second keyframe as RGBA numpy array
            t_values: List of interpolation positions (0.0-1.0)

        Returns:
            List of interpolated frames as RGBA numpy arrays
        """
        logger.info(f"RIFE: Generating {len(t_values)} frames")

        frames = []
        for i, t in enumerate(t_values):
            frame = self.interpolate(frame1, frame2, t)
            frames.append(frame)
            logger.debug(f"RIFE: Generated frame {i+1}/{len(t_values)} at t={t:.3f}")

        return frames

    def recursive_interpolate(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray,
        depth: int = 3
    ) -> List[np.ndarray]:
        """
        Generate frames via recursive doubling.

        This leverages RIFE's strength at generating midpoints:
        - depth=1: 3 frames (start, mid, end)
        - depth=2: 5 frames
        - depth=3: 9 frames
        - depth=4: 17 frames

        Args:
            frame1: First keyframe
            frame2: Second keyframe
            depth: Recursion depth (frames = 2^depth + 1)

        Returns:
            List of frames including start and end
        """
        if depth <= 0:
            return [frame1, frame2]

        # Generate midpoint
        mid = self.interpolate(frame1, frame2, 0.5)

        if depth == 1:
            return [frame1, mid, frame2]

        # Recurse on both halves
        left_frames = self.recursive_interpolate(frame1, mid, depth - 1)
        right_frames = self.recursive_interpolate(mid, frame2, depth - 1)

        # Combine (avoid duplicating midpoint)
        return left_frames + right_frames[1:]

    def _alpha_blend(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray,
        t: float
    ) -> np.ndarray:
        """
        Simple alpha blending fallback.

        Used when RIFE is unavailable or fails.
        """
        result = (1 - t) * frame1.astype(float) + t * frame2.astype(float)
        return result.astype(np.uint8)

    def _alpha_blend_rgb(
        self,
        rgb1: np.ndarray,
        rgb2: np.ndarray,
        t: float
    ) -> np.ndarray:
        """Alpha blend RGB arrays."""
        result = (1 - t) * rgb1.astype(float) + t * rgb2.astype(float)
        return result.astype(np.uint8)


# Singleton instance
_rife_service_instance: Optional[RifeService] = None


def get_rife_service(gpu_id: int = -1) -> RifeService:
    """
    Get or create singleton RIFE service instance.

    Args:
        gpu_id: GPU device ID (-1 for CPU)

    Returns:
        RifeService instance
    """
    global _rife_service_instance
    if _rife_service_instance is None:
        _rife_service_instance = RifeService(gpu_id=gpu_id)
    return _rife_service_instance
