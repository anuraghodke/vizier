"""
Validation service for Telekinesis system.

Phase 3: Claude Vision-based quality assessment
- Evaluates motion smoothness
- Checks arc path adherence
- Detects artifacts (ghosting, tearing)
- Assesses style consistency
"""

import base64
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from anthropic import Anthropic

logger = logging.getLogger(__name__)

# Validation system prompt
VALIDATION_SYSTEM_PROMPT = """You are an expert animation quality assessor. Your job is to evaluate
intermediate animation frames and assess their quality across multiple dimensions.

You will be shown:
1. The starting keyframe (first image)
2. Several intermediate frames from the animation
3. The ending keyframe (last image)

Your task is to evaluate the animation quality and return a structured JSON response.

Scoring Guidelines (0-10 scale):
- 10: Perfect, professional quality
- 8-9: Excellent, minor imperfections
- 6-7: Good, noticeable but acceptable issues
- 4-5: Fair, significant issues affecting quality
- 2-3: Poor, major problems
- 0-1: Unacceptable, severe issues

Evaluation Dimensions:

1. MOTION SMOOTHNESS (smoothness)
   - Do frames transition naturally?
   - Is there temporal coherence?
   - Any jarring jumps or stutters?

2. ARC ADHERENCE (arc_adherence)
   - Does motion follow natural curves?
   - For jumping/bouncing: Is there a parabolic path?
   - Is the path consistent with the motion type?

3. VOLUME CONSISTENCY (volume)
   - Do objects maintain their size?
   - Any unnatural growing/shrinking?
   - Is the shape preserved?

4. ARTIFACTS (artifacts) - Higher = fewer artifacts
   - Ghosting (multiple faint copies of objects)
   - Morphing artifacts (unnatural blending)
   - Tearing or distortion
   - Edge bleeding or halos

5. STYLE CONSISTENCY (style)
   - Does art style remain consistent?
   - Color palette preservation
   - Line quality (if applicable)

Always return valid JSON in this exact format:
{
    "score": <overall quality 0-10>,
    "smoothness": <0-10>,
    "arc_adherence": <0-10>,
    "volume": <0-10>,
    "artifacts": <0-10, higher means fewer artifacts>,
    "style": <0-10>,
    "issues": ["list of specific problems found"],
    "suggestions": ["list of potential fixes"]
}

Be honest and critical. Animation quality matters for the end user."""


class ValidationService:
    """
    Service for validating animation frame quality using Claude Vision.

    Provides quality scores across multiple dimensions and actionable
    feedback for the REFINER agent.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize validation service.

        Args:
            api_key: Anthropic API key (uses env var if not provided)
        """
        import os
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self._client = None

    def _get_client(self) -> Anthropic:
        """Get or create Anthropic client."""
        if self._client is None:
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY not set")
            self._client = Anthropic(api_key=self.api_key)
        return self._client

    def _encode_image(self, image_path: str) -> Dict[str, Any]:
        """
        Encode image file for Claude API.

        Args:
            image_path: Path to image file

        Returns:
            Dict with image source for API
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Determine media type
        suffix = path.suffix.lower()
        media_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        media_type = media_types.get(suffix, "image/png")

        # Read and encode
        with open(path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("utf-8")

        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": data
            }
        }

    def _sample_frames(
        self,
        frames: List[str],
        max_samples: int = 5
    ) -> List[str]:
        """
        Sample frames for validation to reduce API costs.

        Selects first, last, middle, and evenly distributed frames.

        Args:
            frames: List of all frame paths
            max_samples: Maximum frames to sample

        Returns:
            List of sampled frame paths
        """
        if len(frames) <= max_samples:
            return frames

        n = len(frames)
        indices = [
            0,  # First
            n // 4,  # 25%
            n // 2,  # Middle
            3 * n // 4,  # 75%
            n - 1  # Last
        ]

        # Remove duplicates and sort
        indices = sorted(set(indices))

        return [frames[i] for i in indices if i < n]

    def validate_frames(
        self,
        frames: List[str],
        keyframe1: str,
        keyframe2: str,
        plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate animation frames using Claude Vision.

        Args:
            frames: List of generated frame paths
            keyframe1: Path to first keyframe
            keyframe2: Path to second keyframe
            plan: Generation plan (for context)

        Returns:
            Validation result dict with scores and feedback
        """
        logger.info(f"VALIDATOR: Assessing quality of {len(frames)} frames")

        # Sample frames to reduce cost
        sample_frames = self._sample_frames(frames, max_samples=5)
        logger.info(f"VALIDATOR: Sampling {len(sample_frames)} frames for validation")

        try:
            # Build image content
            image_content = []

            # Add keyframe 1 with label
            image_content.append({
                "type": "text",
                "text": "Starting keyframe:"
            })
            image_content.append(self._encode_image(keyframe1))

            # Add sampled intermediate frames
            image_content.append({
                "type": "text",
                "text": f"Intermediate frames ({len(sample_frames)} samples):"
            })
            for i, frame_path in enumerate(sample_frames):
                image_content.append(self._encode_image(frame_path))

            # Add keyframe 2 with label
            image_content.append({
                "type": "text",
                "text": "Ending keyframe:"
            })
            image_content.append(self._encode_image(keyframe2))

            # Add evaluation request
            arc_type = plan.get("arc_type", "none")
            timing_curve = plan.get("timing_curve", "linear")
            num_frames = plan.get("num_frames", len(frames))

            image_content.append({
                "type": "text",
                "text": f"""
Please evaluate this animation sequence.

Animation parameters:
- Total frames: {num_frames}
- Arc type: {arc_type}
- Timing curve: {timing_curve}

Evaluate the quality and return your assessment as JSON.
"""
            })

            # Call Claude
            client = self._get_client()
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1024,
                system=[{
                    "type": "text",
                    "text": VALIDATION_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"}
                }],
                messages=[{
                    "role": "user",
                    "content": image_content
                }]
            )

            # Parse response
            response_text = response.content[0].text

            # Extract JSON from response
            validation = self._parse_validation_response(response_text)

            logger.info(
                f"VALIDATOR: Quality score {validation['score']:.1f}/10, "
                f"smoothness={validation['smoothness']:.1f}, "
                f"artifacts={validation['artifacts']:.1f}"
            )

            return validation

        except Exception as e:
            logger.error(f"VALIDATOR: Claude Vision validation failed: {e}")
            logger.warning("VALIDATOR: Returning fallback validation")

            # Return fallback validation
            return {
                "score": 7.0,
                "smoothness": 7.0,
                "arc_adherence": 7.0,
                "volume": 7.0,
                "artifacts": 7.0,
                "style": 7.0,
                "issues": [f"Validation failed: {str(e)}"],
                "suggestions": ["Manual review recommended"],
                "_status": "fallback",
                "_error": str(e)
            }

    def _parse_validation_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Claude's validation response.

        Handles both raw JSON and markdown-wrapped JSON.

        Args:
            response_text: Raw response from Claude

        Returns:
            Parsed validation dict
        """
        # Try to find JSON in response
        text = response_text.strip()

        # Remove markdown code blocks if present
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            text = text[start:end].strip()

        # Parse JSON
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON object in text
            import re
            match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                raise ValueError(f"Could not parse validation response: {text[:200]}")

        # Validate and normalize
        result = {
            "score": float(data.get("score", 7.0)),
            "smoothness": float(data.get("smoothness", 7.0)),
            "arc_adherence": float(data.get("arc_adherence", 7.0)),
            "volume": float(data.get("volume", 7.0)),
            "artifacts": float(data.get("artifacts", 7.0)),
            "style": float(data.get("style", 7.0)),
            "issues": data.get("issues", []),
            "suggestions": data.get("suggestions", [])
        }

        # Clamp scores to valid range
        for key in ["score", "smoothness", "arc_adherence", "volume", "artifacts", "style"]:
            result[key] = max(0.0, min(10.0, result[key]))

        return result


# Singleton instance
_validation_service_instance: Optional[ValidationService] = None


def get_validation_service() -> ValidationService:
    """
    Get or create singleton validation service instance.

    Returns:
        ValidationService instance
    """
    global _validation_service_instance
    if _validation_service_instance is None:
        _validation_service_instance = ValidationService()
    return _validation_service_instance
