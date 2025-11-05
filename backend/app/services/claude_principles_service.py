"""
Claude Principles Service - Phase 2 Implementation

Uses Claude API to analyze motion and detect which of the 12 animation principles
should apply to the given motion. References the Animation Principles Knowledge Base
to make intelligent decisions.

This service is the intelligence layer that transforms raw motion analysis into
actionable animation theory.
"""
import json
import os
import logging
from typing import Dict, Any, Optional, List
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class ClaudePrinciplesService:
    """
    Service for detecting applicable animation principles using Claude API.

    Phase 2: Intelligent principle detection based on motion analysis
    """

    # System prompt that references the Animation Principles Knowledge Base
    SYSTEM_PROMPT = """You are an expert animation director analyzing motion to determine which of the 12 Principles of Animation apply.

Your task: Given motion analysis data and user instructions, identify which animation principles should be applied and with what parameters.

## The 12 Principles of Animation (Quick Reference)

1. **Squash and Stretch** - Objects deform during motion (bouncing ball compresses on impact)
2. **Anticipation** - Preparatory movement before main action (crouch before jump)
3. **Staging** - Clear presentation of action (readable silhouettes, uncluttered composition)
4. **Straight Ahead Action vs Pose to Pose** - Animation approach (we use pose-to-pose)
5. **Follow Through and Overlapping Action** - Different parts move at different rates (hair trails behind head)
6. **Slow In and Slow Out** - Ease-in and ease-out for natural acceleration (more frames at extremes)
7. **Arc** - Most natural motion follows arcs, not straight lines (arm swing follows arc)
8. **Secondary Action** - Supporting action that emphasizes main action (tail wag while walking)
9. **Timing** - Number of frames determines speed and weight (heavy=slow, light=fast)
10. **Exaggeration** - Push reality for dramatic effect (balance realism with appeal)
11. **Solid Drawing** - Forms have volume, weight, balance in 3D space
12. **Appeal** - Characters/objects should be pleasing and readable

## Detection Guidelines

**Squash and Stretch**: Apply when
- Object is flexible (not rigid metal/stone)
- Bouncing, impacting, or rapid acceleration
- Motion energy is "fast" or "explosive"
- DO NOT apply to rigid objects

**Anticipation**: Apply when
- Large sudden movement (>100px or >45° rotation)
- Motion magnitude is high
- User mentions "jump", "throw", "sudden"
- NOTE: With only 2 keyframes, may be IMPLIED rather than explicit

**Staging**: Apply when
- Multiple objects in scene
- Complex composition
- Important to direct viewer attention
- Background present

**Pose to Pose**: ALWAYS applies (our fundamental approach)

**Follow Through and Overlapping Action**: Apply when
- Object has flexible parts (hair, clothing, tail)
- Character with appendages
- Parts analysis shows multiple moving parts

**Slow In and Slow Out**: Apply when
- Motion energy is "slow" or "medium"
- Heavy object (large size, solid material)
- Natural easing needed
- USER DEFAULT for most motions

**Arc**: Apply when
- Rotation detected (>10 degrees)
- Natural swinging motion
- Body parts moving (arms, legs, head)
- arc_detected is True in motion_direction
- USER DEFAULT for organic motion

**Secondary Action**: Apply when
- Multiple parts moving at different rates
- Supporting elements present (facial expression during walk)

**Timing**: ALWAYS applies (determines speed/frame distribution)

**Exaggeration**: Apply when
- User instruction suggests emphasis ("very", "extremely", "dramatic")
- Style is "cartoon" or "stylized"
- Motion needs enhancement for appeal

**Solid Drawing**: ALWAYS applies (maintain volume and structure)

**Appeal**: ALWAYS applies (strive for pleasing motion)

## Output Format

Respond with valid JSON only (no markdown, no explanations):

{
  "applicable_principles": [
    {
      "principle": "<name>",
      "confidence": <0.0-1.0>,
      "reason": "<1-2 sentence explanation>",
      "parameters": {
        // Principle-specific parameters
      }
    }
  ],
  "dominant_principle": "<primary principle guiding this motion>",
  "complexity_score": <0.0-1.0>
}

## Parameter Examples

**Squash and Stretch**:
```json
{
  "squash_factor": 0.7,
  "stretch_factor": 1.3,
  "axis": "vertical",
  "rigidity": 0.3
}
```

**Anticipation**:
```json
{
  "anticipation_amount": 0.3,
  "anticipation_direction": "opposite"
}
```

**Slow In and Slow Out**:
```json
{
  "ease_in": 0.3,
  "ease_out": 0.5,
  "ease_type": "ease-in-out"
}
```

**Arc**:
```json
{
  "arc_type": "elliptical",
  "apex_position": 0.4,
  "arc_intensity": 0.8
}
```

**Follow Through**:
```json
{
  "parts": ["hair", "clothing"],
  "delay_frames": 2,
  "damping": 0.7
}
```

**Timing**:
```json
{
  "speed_category": "normal",
  "frame_distribution": "even",
  "weight_feeling": "medium"
}
```

## Confidence Scoring

- 0.9-1.0: Definitely applies (clear evidence)
- 0.7-0.9: Probably applies (strong indicators)
- 0.5-0.7: Possibly applies (some evidence)
- <0.5: Do not include (insufficient evidence)

## Important Notes

1. Only include principles with confidence >= 0.5
2. Every motion should have at least 3 principles: timing, solid drawing, appeal
3. dominant_principle is the one most critical for this specific motion
4. complexity_score: 0=simple (ball rolling), 1=complex (character parkour)
5. Be conservative with squash/stretch - only for flexible objects
6. Arc motion is common - assume arc unless clearly linear translation
"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude Principles service.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in environment variables"
            )
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5-20250929"

    def detect_principles(
        self,
        analysis: Dict[str, Any],
        instruction: str
    ) -> Dict[str, Any]:
        """
        Detect which animation principles apply to the given motion.

        Args:
            analysis: Motion analysis from ANALYZER agent containing:
                - motion_type: translation, rotation, deformation, etc.
                - motion_magnitude: distance, rotation degrees
                - motion_direction: angle, arc_detected
                - motion_energy: slow, medium, fast, explosive
                - style: line_art, cel_shaded, etc.
                - parts_analysis: moving_parts, static_parts
                - visual_characteristics: has_deformation, num_objects, etc.
            instruction: User's natural language instruction

        Returns:
            Dictionary containing:
                - applicable_principles: List of principles with confidence and parameters
                - dominant_principle: Primary guiding principle
                - complexity_score: 0-1 complexity rating

        Raises:
            Exception: If API call fails or response is invalid
        """
        logger.info("Detecting animation principles with Claude...")

        # Build user prompt with analysis data
        user_prompt = self._build_detection_prompt(analysis, instruction)

        try:
            # Call Claude API with prompt caching on system prompt
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=[
                    {
                        "type": "text",
                        "text": self.SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"}
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )

            # Validate prompt caching is working
            usage = message.usage
            if not hasattr(usage, 'cache_creation_input_tokens') and not hasattr(usage, 'cache_read_input_tokens'):
                logger.warning("Prompt caching may not be enabled - check API configuration")
            else:
                cache_status = "created" if hasattr(usage, 'cache_creation_input_tokens') else "hit"
                logger.info(f"Prompt cache {cache_status} - system prompt cached")

            # Extract text content
            response_text = message.content[0].text

            # Parse JSON response
            principles_data = self._parse_response(response_text)

            # Validate response structure
            self._validate_principles_data(principles_data)

            # Log results
            num_principles = len(principles_data.get("applicable_principles", []))
            dominant = principles_data.get("dominant_principle", "unknown")
            logger.info(
                f"Detected {num_principles} principles, "
                f"dominant: {dominant}"
            )

            return principles_data

        except Exception as e:
            logger.error(f"Principle detection failed: {e}")
            raise

    def _build_detection_prompt(
        self,
        analysis: Dict[str, Any],
        instruction: str
    ) -> str:
        """Build user prompt with analysis data."""

        # Extract key analysis data
        motion_type = analysis.get("motion_type", "unknown")
        motion_magnitude = analysis.get("motion_magnitude", {})
        motion_direction = analysis.get("motion_direction", {})
        motion_energy = analysis.get("motion_energy", "medium")
        style = analysis.get("style", "unknown")
        parts = analysis.get("parts_analysis", {})
        visual = analysis.get("visual_characteristics", {})

        prompt = f"""Analyze this motion and determine which animation principles apply:

## User Instruction
"{instruction}"

## Motion Analysis

**Motion Type**: {motion_type}

**Motion Magnitude**:
- Distance: {motion_magnitude.get('distance_percent', 0)}% of frame
- Rotation: {motion_magnitude.get('rotation_degrees', 0)}°

**Motion Direction**:
- Description: {motion_direction.get('description', 'unknown')}
- Arc Detected: {motion_direction.get('arc_detected', False)}

**Motion Energy**: {motion_energy}

**Style**: {style}

**Parts Analysis**:
- Moving parts: {', '.join(parts.get('moving_parts', [])) or 'none detected'}
- Static parts: {', '.join(parts.get('static_parts', [])) or 'none detected'}

**Visual Characteristics**:
- Has deformation: {visual.get('has_deformation', False)}
- Has motion blur: {visual.get('has_motion_blur', False)}
- Number of objects: {visual.get('num_objects', 1)}
- Has background: {visual.get('has_background', False)}
- Has transparency: {visual.get('has_transparency', True)}

## Task

Based on this analysis, identify which animation principles should apply.
Consider:
1. Is this organic motion (use arc) or mechanical (may be linear)?
2. Is the object flexible (use squash/stretch) or rigid?
3. Does motion need easing (slow in/out)?
4. Are there multiple parts that could overlap?
5. What timing approach fits the energy level?

Return valid JSON with applicable principles, confidence scores, parameters, and reasoning.
"""
        return prompt

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's JSON response, handling markdown code blocks."""

        # Strip markdown code blocks if present
        text = response_text.strip()
        if text.startswith("```"):
            # Remove ```json or ``` at start
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            # Remove closing ```
            if text.endswith("```"):
                text = text[:-3]

        text = text.strip()

        try:
            data = json.loads(text)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {text[:500]}")
            raise ValueError(f"Invalid JSON response from Claude: {e}")

    def _validate_principles_data(self, data: Dict[str, Any]) -> None:
        """Validate that principles data has required structure."""

        required_fields = ["applicable_principles", "dominant_principle", "complexity_score"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Validate applicable_principles is a list
        if not isinstance(data["applicable_principles"], list):
            raise ValueError("applicable_principles must be a list")

        # Validate each principle has required fields
        for principle in data["applicable_principles"]:
            required_principle_fields = ["principle", "confidence", "reason", "parameters"]
            for field in required_principle_fields:
                if field not in principle:
                    raise ValueError(f"Principle missing required field: {field}")

            # Validate confidence is between 0 and 1
            confidence = principle["confidence"]
            if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                raise ValueError(f"Invalid confidence value: {confidence}")

        # Validate complexity_score
        complexity = data["complexity_score"]
        if not isinstance(complexity, (int, float)) or complexity < 0 or complexity > 1:
            raise ValueError(f"Invalid complexity_score: {complexity}")

        logger.info("Principles data validation passed")


# Singleton instance
_principles_service = None


def get_principles_service(api_key: Optional[str] = None) -> ClaudePrinciplesService:
    """
    Get singleton instance of ClaudePrinciplesService.

    Args:
        api_key: Optional API key (uses env var if not provided)

    Returns:
        ClaudePrinciplesService instance
    """
    global _principles_service
    if _principles_service is None:
        _principles_service = ClaudePrinciplesService(api_key=api_key)
    return _principles_service
