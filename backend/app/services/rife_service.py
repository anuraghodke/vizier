"""
RIFE (Real-Time Intermediate Flow Estimation) service.
Handles image preprocessing, interpolation, and transparency preservation.
"""
import os
import sys
import numpy as np
import torch
from torch.nn import functional as F
from PIL import Image
from typing import Tuple, List, Optional
import math

# Add RIFE model path to sys.path
RIFE_MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../../models/rife")
sys.path.insert(0, RIFE_MODEL_PATH)

from ..models.schemas import AnimationParams


class RIFEService:
    """
    Service for frame interpolation using RIFE model.
    Handles transparency preservation and image preprocessing.
    """

    def __init__(self, model_dir: str = None):
        """
        Initialize RIFE service and load model.

        Args:
            model_dir: Path to RIFE train_log directory (default: auto-detect)
        """
        if model_dir is None:
            model_dir = os.path.join(RIFE_MODEL_PATH, "train_log")

        self.model_dir = model_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        torch.set_grad_enabled(False)
        self._load_model()

    def _load_model(self):
        """Load RIFE model from train_log directory"""
        try:
            # Try loading different RIFE versions
            try:
                from train_log.RIFE_HDv3 import Model
                self.model = Model()
                self.model.load_model(self.model_dir, -1)
                print("Loaded RIFE v3.x HD model")
            except Exception as e:
                print(f"Could not load v3: {e}")
                try:
                    from model.RIFE_HDv2 import Model
                    self.model = Model()
                    self.model.load_model(self.model_dir, -1)
                    print("Loaded RIFE v2.x HD model")
                except Exception as e2:
                    print(f"Could not load v2: {e2}")
                    from model.RIFE_HD import Model
                    self.model = Model()
                    self.model.load_model(self.model_dir, -1)
                    print("Loaded RIFE v1.x HD model")

            if not hasattr(self.model, 'version'):
                self.model.version = 0

            self.model.eval()
            self.model.device()

        except Exception as e:
            raise Exception(f"Failed to load RIFE model: {str(e)}")

    def preprocess_image(
        self,
        image_path: str,
        max_dimension: int = 1024
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Preprocess image for RIFE model.

        Steps:
        1. Load image and validate PNG format
        2. Separate RGB and alpha channels
        3. Resize if needed (keeping aspect ratio)
        4. Ensure dimensions divisible by 64 (RIFE requirement)
        5. Normalize to [0, 1] range

        Args:
            image_path: Path to PNG image
            max_dimension: Maximum width or height (resized if larger)

        Returns:
            Tuple of (rgb_array, alpha_array)
            - rgb_array: (H, W, 3) float32 in range [0, 1]
            - alpha_array: (H, W) float32 in range [0, 1], or None if no alpha

        Raises:
            ValueError: If image format is invalid or processing fails
        """
        try:
            # Load image
            img = Image.open(image_path)

            # Validate PNG format
            if img.format != "PNG":
                raise ValueError(f"Image must be PNG format, got {img.format}")

            # Convert to RGBA if needed
            if img.mode != "RGBA":
                if img.mode == "RGB":
                    img = img.convert("RGBA")
                else:
                    raise ValueError(f"Unsupported image mode: {img.mode}")

            # Get original dimensions
            width, height = img.size

            # Resize if too large (maintain aspect ratio)
            if width > max_dimension or height > max_dimension:
                scale = max_dimension / max(width, height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                width, height = new_width, new_height

            # Ensure dimensions divisible by 64 (RIFE requirement)
            # Round up to nearest multiple of 64
            width_padded = ((width - 1) // 64 + 1) * 64
            height_padded = ((height - 1) // 64 + 1) * 64

            # Resize to padded dimensions if needed
            if img.size != (width_padded, height_padded):
                img = img.resize((width_padded, height_padded), Image.Resampling.LANCZOS)

            # Convert to numpy array
            img_array = np.array(img).astype(np.float32) / 255.0

            # Separate RGB and alpha
            rgb = img_array[:, :, :3]
            alpha = img_array[:, :, 3] if img_array.shape[2] == 4 else None

            return rgb, alpha

        except Exception as e:
            raise ValueError(f"Image preprocessing failed: {str(e)}")

    def _interpolate_single_frame(
        self,
        rgb1: np.ndarray,
        rgb2: np.ndarray,
        t: float
    ) -> np.ndarray:
        """
        Interpolate a single frame at time t using RIFE model.

        Args:
            rgb1: First RGB image (H, W, 3) in range [0, 1]
            rgb2: Second RGB image (H, W, 3) in range [0, 1]
            t: Time value between 0.0 and 1.0

        Returns:
            Interpolated RGB image (H, W, 3) in range [0, 1]
        """
        # Convert to torch tensors (RIFE expects [B, C, H, W])
        img0 = torch.tensor(rgb1.transpose(2, 0, 1)).unsqueeze(0).to(self.device)
        img1 = torch.tensor(rgb2.transpose(2, 0, 1)).unsqueeze(0).to(self.device)

        # Run RIFE interpolation
        # Check if model supports time parameter (v3.9+)
        if hasattr(self.model, 'version') and self.model.version >= 3.9:
            interpolated = self.model.inference(img0, img1, t)
        else:
            # Older versions don't support arbitrary t, only t=0.5
            # For other t values, we'd need to do recursive interpolation
            if abs(t - 0.5) < 0.01:  # Close enough to 0.5
                interpolated = self.model.inference(img0, img1)
            else:
                # Fallback: use linear interpolation for non-0.5 values
                # This is a limitation of older RIFE versions
                interpolated = self.model.inference(img0, img1)
                # TODO: Implement recursive interpolation for arbitrary t

        # Convert back to numpy (H, W, C)
        result = interpolated[0].cpu().numpy().transpose(1, 2, 0)

        # Clip to valid range
        result = np.clip(result, 0.0, 1.0)

        return result

    def _interpolate_alpha(
        self,
        alpha1: np.ndarray,
        alpha2: np.ndarray,
        t: float
    ) -> np.ndarray:
        """
        Interpolate alpha channel linearly.

        Args:
            alpha1: First alpha channel (H, W)
            alpha2: Second alpha channel (H, W)
            t: Time value between 0.0 and 1.0

        Returns:
            Interpolated alpha channel (H, W)
        """
        return (1 - t) * alpha1 + t * alpha2

    def _compute_interpolation_times(
        self,
        params: AnimationParams
    ) -> List[float]:
        """
        Compute interpolation times based on motion type and speed.

        Args:
            params: Animation parameters with motion_type and num_frames

        Returns:
            List of time values between 0.0 and 1.0
        """
        # Use custom times if provided
        if params.interpolation_times:
            return params.interpolation_times

        # Generate linear time values
        n = params.num_frames + 2  # Include start and end frames
        times = [i / (n - 1) for i in range(n)]

        # Apply easing function based on motion type
        if params.motion_type == "linear":
            pass  # Already linear
        elif params.motion_type == "ease-in":
            times = [self._ease_in(t) for t in times]
        elif params.motion_type == "ease-out":
            times = [self._ease_out(t) for t in times]
        elif params.motion_type == "ease-in-out":
            times = [self._ease_in_out(t) for t in times]
        elif params.motion_type == "bounce":
            times = [self._bounce(t) for t in times]
        elif params.motion_type == "elastic":
            times = [self._elastic(t) for t in times]

        return times

    @staticmethod
    def _ease_in(t: float) -> float:
        """Ease-in (quadratic)"""
        return t * t

    @staticmethod
    def _ease_out(t: float) -> float:
        """Ease-out (quadratic)"""
        return t * (2 - t)

    @staticmethod
    def _ease_in_out(t: float) -> float:
        """Ease-in-out (quadratic)"""
        if t < 0.5:
            return 2 * t * t
        else:
            return -1 + (4 - 2 * t) * t

    @staticmethod
    def _bounce(t: float) -> float:
        """Bounce easing (simplified)"""
        if t < 0.5:
            return 2 * t * t
        else:
            t = 1 - t
            return 1 - 2 * t * t

    @staticmethod
    def _elastic(t: float) -> float:
        """Elastic easing (simplified)"""
        if t == 0 or t == 1:
            return t
        p = 0.3
        s = p / 4
        return math.pow(2, -10 * t) * math.sin((t - s) * (2 * math.pi) / p) + 1

    def interpolate(
        self,
        frame1_path: str,
        frame2_path: str,
        params: AnimationParams
    ) -> List[Image.Image]:
        """
        Generate intermediate frames between two keyframes.

        Args:
            frame1_path: Path to first PNG keyframe
            frame2_path: Path to second PNG keyframe
            params: Animation parameters

        Returns:
            List of PIL Images (including keyframes at start and end)

        Raises:
            ValueError: If images have different dimensions or invalid format
        """
        # Preprocess both images
        rgb1, alpha1 = self.preprocess_image(frame1_path)
        rgb2, alpha2 = self.preprocess_image(frame2_path)

        # Validate dimensions match
        if rgb1.shape != rgb2.shape:
            raise ValueError(
                f"Images must have same dimensions. "
                f"Got {rgb1.shape} and {rgb2.shape}"
            )

        # Check if both have alpha or both don't
        has_alpha = alpha1 is not None and alpha2 is not None
        if (alpha1 is None) != (alpha2 is None):
            # One has alpha, one doesn't - add opaque alpha to the one without
            if alpha1 is None:
                alpha1 = np.ones(rgb1.shape[:2], dtype=np.float32)
            if alpha2 is None:
                alpha2 = np.ones(rgb2.shape[:2], dtype=np.float32)
            has_alpha = True

        # Compute interpolation times
        times = self._compute_interpolation_times(params)

        # Generate frames
        frames = []
        for i, t in enumerate(times):
            if t == 0.0:
                # Use first keyframe directly
                rgb = rgb1
                alpha = alpha1
            elif t == 1.0:
                # Use second keyframe directly
                rgb = rgb2
                alpha = alpha2
            else:
                # Interpolate RGB with RIFE
                rgb = self._interpolate_single_frame(rgb1, rgb2, t)

                # Interpolate alpha linearly if present
                if has_alpha:
                    alpha = self._interpolate_alpha(alpha1, alpha2, t)
                else:
                    alpha = None

            # Convert to PIL Image
            rgb_uint8 = (rgb * 255).astype(np.uint8)
            if has_alpha:
                alpha_uint8 = (alpha * 255).astype(np.uint8)
                rgba = np.dstack([rgb_uint8, alpha_uint8])
                img = Image.fromarray(rgba, mode='RGBA')
            else:
                img = Image.fromarray(rgb_uint8, mode='RGB')

            frames.append(img)

        return frames

    def save_frames(
        self,
        frames: List[Image.Image],
        output_dir: str,
        prefix: str = "frame"
    ) -> List[str]:
        """
        Save frames to disk with sequential naming.

        Args:
            frames: List of PIL Images
            output_dir: Directory to save frames
            prefix: Filename prefix (default: "frame")

        Returns:
            List of saved filenames

        Raises:
            IOError: If saving fails
        """
        import os

        # Create output directory if needed
        os.makedirs(output_dir, exist_ok=True)

        filenames = []
        for i, frame in enumerate(frames):
            filename = f"{prefix}_{i+1:03d}.png"
            filepath = os.path.join(output_dir, filename)
            frame.save(filepath, format='PNG')
            filenames.append(filename)

        return filenames


# Singleton instance
_rife_service_instance = None


def get_rife_service() -> RIFEService:
    """
    Get or create singleton RIFE service instance.

    Returns:
        RIFEService instance
    """
    global _rife_service_instance
    if _rife_service_instance is None:
        _rife_service_instance = RIFEService()
    return _rife_service_instance
