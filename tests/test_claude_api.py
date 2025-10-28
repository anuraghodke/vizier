"""
Test Claude API for parsing animation instructions.
This script tests natural language parsing into structured animation parameters.
"""
import os
import json
from anthropic import Anthropic

# Check for API key
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("❌ Error: ANTHROPIC_API_KEY not found in environment")
    print("\nPlease set your API key:")
    print("  export ANTHROPIC_API_KEY='sk-ant-api03-...'")
    print("\nOr create a .env file:")
    print("  cp .env.example .env")
    print("  # Edit .env and add your API key")
    exit(1)

print("✓ API key found")
print("\nInitializing Claude client...")
client = Anthropic(api_key=api_key)

# Test instructions
test_instructions = [
    "create 8 bouncy frames",
    "generate 12 frames with smooth ease-in-out motion",
    "make 6 frames with a slow start and fast finish",
    "create 16 frames with elastic motion like a spring",
    "generate 4 frames that move linearly"
]

# System prompt for parsing animation instructions
SYSTEM_PROMPT = """You are an animation parameter parser. Parse natural language animation instructions into structured JSON.

Extract these parameters:
- num_frames: integer (4-32) - number of intermediate frames to generate
- motion_type: one of ["linear", "ease-in", "ease-out", "ease-in-out", "bounce", "elastic"]
- speed: one of ["very-slow", "slow", "normal", "fast", "very-fast"]
- emphasis: brief description of the motion intention

Respond ONLY with valid JSON, no markdown formatting. Example:
{"num_frames": 8, "motion_type": "bounce", "speed": "normal", "emphasis": "bouncy spring-like motion"}"""

print("\nTesting Claude API with sample instructions:\n")

for i, instruction in enumerate(test_instructions, 1):
    print(f"Test {i}: \"{instruction}\"")

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=256,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": f"Parse this animation instruction: {instruction}"}
            ]
        )

        # Extract response
        response_text = message.content[0].text.strip()

        # Try to parse JSON (handle markdown code blocks if present)
        if response_text.startswith("```"):
            # Remove markdown code block formatting
            lines = response_text.split("\n")
            response_text = "\n".join([l for l in lines if not l.startswith("```")])

        params = json.loads(response_text)

        # Validate required fields
        required_fields = ["num_frames", "motion_type", "speed", "emphasis"]
        missing = [f for f in required_fields if f not in params]

        if missing:
            print(f"  ⚠️  Missing fields: {missing}")
        else:
            print(f"  ✓ Parsed successfully:")
            print(f"    - Frames: {params['num_frames']}")
            print(f"    - Motion: {params['motion_type']}")
            print(f"    - Speed: {params['speed']}")
            print(f"    - Emphasis: {params['emphasis']}")

    except json.JSONDecodeError as e:
        print(f"  ❌ JSON parse error: {e}")
        print(f"  Raw response: {response_text}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print()

print("✅ Claude API test complete!")
print("\nNote: The API key is working and Claude can parse animation instructions.")
print("In production, we'll add error handling, retries, and default fallbacks.")
