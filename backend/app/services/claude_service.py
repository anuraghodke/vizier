"""
Claude API service for parsing natural language animation instructions.
Converts user instructions into structured AnimationParams.
"""
import json
import os
from typing import Dict, Any, Optional
from anthropic import Anthropic
from ..models.schemas import AnimationParams


class ClaudeService:
    """
    Service for interacting with Claude API to parse animation instructions.
    """

    # System prompt for Claude to parse animation instructions
    SYSTEM_PROMPT = """You are an animation parameter parser for a 2D frame interpolation tool.
Parse natural language animation instructions into structured JSON parameters.

Extract these parameters:
- num_frames: integer between 4 and 32 (number of intermediate frames)
- motion_type: one of ["linear", "ease-in", "ease-out", "ease-in-out", "bounce", "elastic"]
- speed: one of ["very-slow", "slow", "normal", "fast", "very-fast"]
- emphasis: brief description of the animation style or intent (1-2 sentences)

Guidelines:
- Default motion_type is "ease-in-out" if not specified
- Default speed is "normal" if not specified
- Infer num_frames from context (e.g., "smooth" suggests more frames, "quick" suggests fewer)
- If exact frame count not given, use reasonable defaults: slow=16, normal=8, fast=4

Respond ONLY with valid JSON matching this structure (no markdown, no explanations):
{
  "num_frames": <int>,
  "motion_type": "<string>",
  "speed": "<string>",
  "emphasis": "<string>"
}"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude service with API key.

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

    def parse_instruction(self, instruction: str) -> AnimationParams:
        """
        Parse natural language animation instruction into structured parameters.

        Args:
            instruction: Natural language description (e.g., "create 8 bouncy frames")

        Returns:
            AnimationParams object with parsed parameters

        Raises:
            ValueError: If instruction is invalid or parsing fails
            Exception: If API call fails
        """
        if not instruction or len(instruction.strip()) < 5:
            raise ValueError("Instruction must be at least 5 characters long")

        if len(instruction) > 500:
            raise ValueError("Instruction must be less than 500 characters")

        try:
            # Call Claude API with prompt caching on system prompt
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
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
                        "content": instruction
                    }
                ]
            )

            # Validate that prompt caching is working
            usage = message.usage
            if not hasattr(usage, 'cache_creation_input_tokens') and not hasattr(usage, 'cache_read_input_tokens'):
                raise Exception(
                    "Prompt caching is not enabled or not working. "
                    "Ensure you're using a model that supports prompt caching."
                )

            # Extract response text
            response_text = message.content[0].text.strip()

            # Parse JSON response
            try:
                params_dict = json.loads(response_text)
            except json.JSONDecodeError as e:
                # Try to extract JSON if wrapped in markdown
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()
                    params_dict = json.loads(response_text)
                else:
                    raise ValueError(f"Failed to parse Claude response as JSON: {e}")

            # Validate and create AnimationParams
            params = AnimationParams(**params_dict)
            return params

        except Exception as e:
            raise Exception(f"Claude API parsing failed: {str(e)}")

    def parse_instruction_raw(self, instruction: str) -> Dict[str, Any]:
        """
        Parse instruction and return raw dictionary (useful for debugging).

        Args:
            instruction: Natural language description

        Returns:
            Dictionary with parsed parameters
        """
        params = self.parse_instruction(instruction)
        return params.model_dump()


# Singleton instance (optional, for convenience)
_claude_service_instance = None


def get_claude_service() -> ClaudeService:
    """
    Get or create singleton Claude service instance.

    Returns:
        ClaudeService instance
    """
    global _claude_service_instance
    if _claude_service_instance is None:
        _claude_service_instance = ClaudeService()
    return _claude_service_instance
