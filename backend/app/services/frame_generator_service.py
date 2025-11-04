"""
Frame generation service for Telekinesis system.

Phase 1: Object-based motion interpolation
- Detects objects using color segmentation
- Interpolates object position and color
- Renders objects at intermediate states

Future phases will integrate:
- AnimateDiff for motion-aware generation
- ControlNet for structural guidance
- Deformation/squash-stretch
"""
import os
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw
from typing import List, Dict, Any, Optional, Tuple
import cv2
import logging

logger = logging.getLogger(__name__)


class FrameGeneratorService:
    """
    Service for generating intermediate frames between keyframes.

    Phase 1: Object-based motion interpolation
    - Detects moving objects
    - Interpolates position and color
    - Renders clean frames with objects in motion

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
        Save numpy array as PNG image with transparency preserved.

        Args:
            array: RGBA numpy array (0-255, uint8)
            output_path: Path to save image
        """
        # Ensure output directory exists
        Path(output_path).parent.mkdir(exist_ok=True, parents=True)

        # Convert to PIL and save with explicit PNG format to preserve transparency
        img = Image.fromarray(array, mode="RGBA")
        # Save as PNG - PIL automatically preserves RGBA transparency
        img.save(output_path, format="PNG", optimize=False)
        logger.debug(f"Saved frame: {output_path}")

    def _detect_object(self, image: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Detect primary moving object using color-based segmentation.

        Args:
            image: RGBA numpy array (H, W, 4)

        Returns:
            Dict with object properties:
                - mask: Binary mask of object (H, W)
                - centroid: (x, y) center position
                - color: (r, g, b) average color
                - bbox: (x1, y1, x2, y2) bounding box
                - contour: Largest contour points
                - width: Object width in pixels
                - height: Object height in pixels
                - scale: Baseline scale factor (1.0)
            or None if no object detected
        """
        # Convert to RGB for processing (ignore alpha initially)
        rgb = image[:, :, :3]
        alpha = image[:, :, 3]

        # Create mask based on non-transparent pixels
        # Threshold: alpha > 10 (mostly opaque)
        alpha_mask = alpha > 10

        # Also exclude near-white background pixels
        # White threshold: all channels > 240
        white_mask = np.all(rgb > 240, axis=2)

        # Object mask = opaque AND not white
        object_mask = alpha_mask & ~white_mask

        # Clean up mask with morphological operations
        kernel = np.ones((3, 3), np.uint8)
        object_mask = cv2.morphologyEx(
            object_mask.astype(np.uint8),
            cv2.MORPH_CLOSE,
            kernel
        )
        object_mask = cv2.morphologyEx(
            object_mask.astype(np.uint8),
            cv2.MORPH_OPEN,
            kernel
        )

        # Find contours
        contours, _ = cv2.findContours(
            object_mask.astype(np.uint8),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            logger.warning("No object detected in image")
            return None

        # Get largest contour
        largest_contour = max(contours, key=cv2.contourArea)

        # Calculate centroid
        M = cv2.moments(largest_contour)
        if M["m00"] == 0:
            return None

        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        # Get bounding box
        x1, y1, w, h = cv2.boundingRect(largest_contour)
        x2 = x1 + w
        y2 = y1 + h

        # Calculate average color of object pixels
        object_pixels = rgb[object_mask > 0]
        if len(object_pixels) == 0:
            avg_color = (0, 0, 0)
        else:
            avg_color = tuple(np.mean(object_pixels, axis=0).astype(int))

        return {
            "mask": object_mask > 0,
            "centroid": (cx, cy),
            "color": avg_color,
            "bbox": (x1, y1, x2, y2),
            "contour": largest_contour,
            "width": w,
            "height": h,
            "scale": 1.0
        }

    def _calculate_scale_factor(
        self,
        obj1: Dict[str, Any],
        obj2: Dict[str, Any]
    ) -> float:
        """
        Calculate relative scale factor between two objects.

        Uses average of width and height to compute scale ratio.

        Args:
            obj1: Object properties from keyframe 1
            obj2: Object properties from keyframe 2

        Returns:
            Scale ratio (obj2_size / obj1_size)
        """
        # Calculate average dimension for each object
        size1 = (obj1["width"] + obj1["height"]) / 2.0
        size2 = (obj2["width"] + obj2["height"]) / 2.0

        # Avoid division by zero
        if size1 == 0:
            return 1.0

        return size2 / size1

    def _render_object_frame(
        self,
        canvas_shape: Tuple[int, int],
        obj1: Dict[str, Any],
        obj2: Dict[str, Any],
        t: float
    ) -> np.ndarray:
        """
        Render a frame with object at interpolated position, color, and size.

        Shape remains constant (contour from obj1), but is uniformly scaled
        to match the size change between keyframes.

        Args:
            canvas_shape: (height, width) of output frame
            obj1: Object properties from keyframe 1
            obj2: Object properties from keyframe 2
            t: Interpolation parameter (0.0 = obj1, 1.0 = obj2)

        Returns:
            Rendered frame (RGBA)
        """
        height, width = canvas_shape

        # Create blank transparent canvas using PIL (preserve PNG transparency)
        # Use (0, 0, 0, 0) for fully transparent RGBA
        pil_canvas = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(pil_canvas)

        # Interpolate position
        x1, y1 = obj1["centroid"]
        x2, y2 = obj2["centroid"]

        interp_x = int((1 - t) * x1 + t * x2)
        interp_y = int((1 - t) * y1 + t * y2)

        # Interpolate color
        r1, g1, b1 = obj1["color"]
        r2, g2, b2 = obj2["color"]

        interp_r = int((1 - t) * r1 + t * r2)
        interp_g = int((1 - t) * g1 + t * g2)
        interp_b = int((1 - t) * b1 + t * b2)
        interp_color = (interp_r, interp_g, interp_b)

        # Get object shape from keyframe 1 (shape stays constant)
        contour = obj1["contour"]
        orig_x, orig_y = obj1["centroid"]

        # Calculate scale factor between keyframes
        scale_ratio = self._calculate_scale_factor(obj1, obj2)

        # Interpolate scale factor (1.0 at t=0, scale_ratio at t=1)
        interp_scale = (1 - t) * 1.0 + t * scale_ratio

        # Transform contour: scale first (around centroid), then translate
        # Step 1: Center contour at origin
        centered_contour = contour.copy().astype(np.float32)
        centered_contour[:, :, 0] -= orig_x
        centered_contour[:, :, 1] -= orig_y

        # Step 2: Apply uniform scale
        scaled_contour = centered_contour * interp_scale

        # Step 3: Translate to interpolated position
        final_contour = scaled_contour.copy()
        final_contour[:, :, 0] += interp_x
        final_contour[:, :, 1] += interp_y

        # Convert contour to list of tuples for PIL
        points = [(int(pt[0][0]), int(pt[0][1])) for pt in final_contour]

        # Draw filled polygon with interpolated color
        if len(points) >= 3:
            draw.polygon(points, fill=interp_color + (255,))

        # Convert back to numpy
        result = np.array(pil_canvas, dtype=np.uint8)

        return result

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

        Phase 1: Object-based motion interpolation
        - Detects objects in keyframes
        - Interpolates position and color
        - Renders objects in motion (not fading)

        Future: AnimateDiff generation with ControlNet guidance

        Args:
            keyframe1_path: Path to first keyframe
            keyframe2_path: Path to second keyframe
            plan: Generation plan from PLANNER agent
            job_id: Job ID for output directory

        Returns:
            List of generated frame paths
        """
        logger.info(f"GENERATOR: Starting object-based frame generation for job {job_id}")

        # Load keyframes
        try:
            kf1 = self._load_image(keyframe1_path)
            kf2 = self._load_image(keyframe2_path)
        except Exception as e:
            logger.error(f"Failed to load keyframes: {e}")
            raise ValueError(f"Could not load keyframe images: {e}")

        # Detect objects in keyframes
        logger.info("GENERATOR: Detecting objects in keyframes...")
        obj1 = self._detect_object(kf1)
        obj2 = self._detect_object(kf2)

        if obj1 is None or obj2 is None:
            logger.error("Failed to detect objects in one or both keyframes")
            raise ValueError("Could not detect moving objects in keyframes")

        logger.info(
            f"GENERATOR: Object 1 at {obj1['centroid']}, "
            f"size {obj1['width']}x{obj1['height']}, color {obj1['color']}"
        )
        logger.info(
            f"GENERATOR: Object 2 at {obj2['centroid']}, "
            f"size {obj2['width']}x{obj2['height']}, color {obj2['color']}"
        )

        # Calculate and log scale change
        scale_ratio = self._calculate_scale_factor(obj1, obj2)
        logger.info(
            f"GENERATOR: Scale change detected: {scale_ratio:.2f}x "
            f"({'growing' if scale_ratio > 1.0 else 'shrinking' if scale_ratio < 1.0 else 'constant'})"
        )

        # Extract plan parameters
        num_frames = plan.get("num_frames", 8)
        timing_curve = plan.get("timing_curve", "linear")
        frame_schedule = plan.get("frame_schedule", [])

        # Create output directory for this job
        job_output_dir = self.output_dir / job_id
        job_output_dir.mkdir(exist_ok=True, parents=True)

        generated_frames = []

        # Get canvas size from keyframe 1
        canvas_shape = (kf1.shape[0], kf1.shape[1])

        # Generate frames according to schedule
        for i, frame_info in enumerate(frame_schedule):
            # Get interpolation parameter
            t_linear = frame_info.get("t", i / (num_frames - 1) if num_frames > 1 else 0.0)

            # Apply easing curve
            t_eased = self._apply_easing(t_linear, timing_curve)

            # Generate frame with object at interpolated state
            if t_eased == 0.0:
                # First keyframe
                interpolated = kf1.copy()
            elif t_eased == 1.0:
                # Second keyframe
                interpolated = kf2.copy()
            else:
                # Render object at interpolated position and color
                interpolated = self._render_object_frame(
                    canvas_shape, obj1, obj2, t_eased
                )

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
            f"with {timing_curve} timing and object-based motion"
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
