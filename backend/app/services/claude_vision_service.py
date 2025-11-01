"""
Claude Vision service for analyzing keyframe images.
Used by ANALYZER agent to understand motion, style, and structure.
"""
import base64
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
from anthropic import Anthropic


class ClaudeVisionService:
    """
    Service for analyzing images using Claude's vision capabilities.
    Used in Phase 1 of Telekinesis for basic keyframe analysis.
    """

    # System prompt for animation analysis
    ANALYSIS_SYSTEM_PROMPT = """You are an expert animation analyzer helping to create intermediate frames between two keyframes.

Analyze the two provided keyframe images and provide detailed information about:

1. **Motion Type**: What kind of movement is happening between the frames?
   - translation (object moving from one position to another)
   - rotation (object rotating)
   - deformation (object changing shape)
   - transformation (object changing into something else)
   - scale (object getting bigger or smaller)
   - combination (multiple types)

2. **Primary Subject**: What is the main object or character that's moving?

3. **Motion Details**:
   - Approximate distance moved (in rough percentage of image width/height)
   - Direction of motion (up, down, left, right, diagonal, circular)
   - Whether the motion appears to follow an arc or straight line
   - Speed/energy of the motion (slow, medium, fast, explosive)

4. **Visual Style**:
   - line_art (clean lines, manga/comic style)
   - cel_shaded (flat colors with defined edges)
   - painted (brush strokes, artistic)
   - realistic (photographic or detailed)
   - sketch (rough, hand-drawn)
   - pixel_art (pixelated, retro game style)

5. **Animation Characteristics**:
   - What parts of the subject are moving vs staying still?
   - Is there any visible deformation (squash/stretch)?
   - Are there multiple objects or layers?
   - Any visible motion blur or speed lines?
   - Background present or transparent?

Respond in JSON format with this structure:
{
  "motion_type": "<string>",
  "primary_subject": "<description>",
  "motion_magnitude": {
    "distance_percent": <number 0-100>,
    "rotation_degrees": <number 0-360>
  },
  "motion_direction": {
    "description": "<string>",
    "arc_detected": <boolean>
  },
  "motion_energy": "<slow|medium|fast|explosive>",
  "style": "<string>",
  "parts_analysis": {
    "moving_parts": ["<list of parts>"],
    "static_parts": ["<list of parts>"]
  },
  "visual_characteristics": {
    "has_deformation": <boolean>,
    "has_motion_blur": <boolean>,
    "has_transparency": <boolean>,
    "num_objects": <number>,
    "has_background": <boolean>
  },
  "animation_suggestion": "<1-2 sentence suggestion about which animation principles might apply>"
}

Be specific and detailed. This analysis will be used to plan frame generation."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude Vision service with API key.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in environment variables or parameters"
            )
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5-20250929"

    def _encode_image(self, image_path: str) -> tuple[str, str]:
        """
        Encode image to base64 for Claude API.

        Args:
            image_path: Path to image file

        Returns:
            Tuple of (base64_data, media_type)

        Raises:
            FileNotFoundError: If image doesn't exist
            ValueError: If unsupported image format
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Determine media type from extension
        extension = path.suffix.lower()
        media_type_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif"
        }

        if extension not in media_type_map:
            raise ValueError(
                f"Unsupported image format: {extension}. "
                f"Supported: {list(media_type_map.keys())}"
            )

        media_type = media_type_map[extension]

        # Read and encode image
        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        return image_data, media_type

    def analyze_keyframes(
        self,
        keyframe1_path: str,
        keyframe2_path: str,
        instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze two keyframes to understand motion and style.

        Args:
            keyframe1_path: Path to first keyframe image
            keyframe2_path: Path to second keyframe image
            instruction: Optional user instruction for context

        Returns:
            Dictionary with analysis results matching AnimationState.analysis schema

        Raises:
            FileNotFoundError: If images don't exist
            ValueError: If images are invalid
            Exception: If API call fails
        """
        # Encode both images
        image1_data, media_type1 = self._encode_image(keyframe1_path)
        image2_data, media_type2 = self._encode_image(keyframe2_path)

        # Build message content with images
        message_content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type1,
                    "data": image1_data,
                }
            },
            {
                "type": "text",
                "text": "KEYFRAME 1 (starting position) shown above."
            },
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type2,
                    "data": image2_data,
                }
            },
            {
                "type": "text",
                "text": "KEYFRAME 2 (ending position) shown above."
            },
            {
                "type": "text",
                "text": (
                    f"Analyze the motion between these two keyframes.\n\n"
                    f"User instruction: {instruction or 'None provided'}\n\n"
                    f"Provide detailed analysis in JSON format as specified."
                )
            }
        ]

        try:
            # Call Claude Vision API with prompt caching on system prompt
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=[
                    {
                        "type": "text",
                        "text": self.ANALYSIS_SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"}
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": message_content
                    }
                ]
            )

            # Validate that prompt caching is working
            usage = response.usage
            if not hasattr(usage, 'cache_creation_input_tokens') and not hasattr(usage, 'cache_read_input_tokens'):
                raise Exception(
                    "Prompt caching is not enabled or not working. "
                    "Ensure you're using a model that supports prompt caching."
                )

            # Extract response text
            response_text = response.content[0].text.strip()

            # Parse JSON response
            try:
                analysis = json.loads(response_text)
            except json.JSONDecodeError as e:
                # Try to extract JSON if wrapped in markdown
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()
                    analysis = json.loads(response_text)
                else:
                    raise ValueError(f"Failed to parse Claude response as JSON: {e}")

            # Enhance with additional fields expected by AnimationState
            analysis["pose_data"] = {}  # MediaPipe will add this in Phase 2
            analysis["object_segments"] = []  # Segmentation in Phase 2
            analysis["color_palette"] = []  # Color extraction in Phase 2
            analysis["volume_analysis"] = {}  # Volume measurement in Phase 2
            analysis["_phase"] = 1
            analysis["_status"] = "claude_vision_analyzed"

            return analysis

        except Exception as e:
            raise Exception(f"Claude Vision analysis failed: {str(e)}")

    def quick_describe(self, image_path: str) -> str:
        """
        Get a quick text description of a single image.
        Useful for debugging and testing.

        Args:
            image_path: Path to image file

        Returns:
            Text description of the image
        """
        image_data, media_type = self._encode_image(image_path)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            }
                        },
                        {
                            "type": "text",
                            "text": "Describe this image in 2-3 sentences."
                        }
                    ]
                }
            ]
        )

        return response.content[0].text.strip()


# Singleton instance (optional, for convenience)
_vision_service_instance = None


def get_vision_service() -> ClaudeVisionService:
    """
    Get or create singleton Claude Vision service instance.

    Returns:
        ClaudeVisionService instance
    """
    global _vision_service_instance
    if _vision_service_instance is None:
        _vision_service_instance = ClaudeVisionService()
    return _vision_service_instance
