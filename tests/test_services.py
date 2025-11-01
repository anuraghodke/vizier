"""
Unit tests for Claude services.
Tests core functionality of Phase 1 services.
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.claude_service import ClaudeService
from backend.app.models.schemas import AnimationParams


def test_claude_service():
    """Test Claude API instruction parsing"""
    print("\n" + "="*60)
    print("Testing Claude Service")
    print("="*60)

    try:
        # Initialize service
        print("\n1. Initializing Claude service...")
        claude = ClaudeService()
        print("   ✓ Claude service initialized")

        # Test cases
        test_instructions = [
            "create 8 bouncy frames",
            "generate 12 frames with smooth ease-in-out motion",
            "make 16 slow frames with elastic movement",
            "quick 4 frame animation",
            "create a very slow 20 frame linear animation"
        ]

        print(f"\n2. Testing {len(test_instructions)} instructions...")
        for i, instruction in enumerate(test_instructions, 1):
            print(f"\n   Test {i}: \"{instruction}\"")
            try:
                params = claude.parse_instruction(instruction)
                print(f"   ✓ Parsed successfully:")
                print(f"     - Frames: {params.num_frames}")
                print(f"     - Motion: {params.motion_type}")
                print(f"     - Speed: {params.speed}")
                print(f"     - Emphasis: {params.emphasis}")
            except Exception as e:
                print(f"   ✗ Failed: {e}")
                return False

        print("\n✅ Claude service tests PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Claude service tests FAILED: {e}")
        return False


def test_schemas():
    """Test Pydantic schemas validation"""
    print("\n" + "="*60)
    print("Testing Pydantic Schemas")
    print("="*60)

    try:
        print("\n1. Testing AnimationParams...")

        # Valid params
        params = AnimationParams(
            num_frames=8,
            motion_type="bounce",
            speed="normal",
            emphasis="Test animation"
        )
        print(f"   ✓ Valid params created: {params.num_frames} frames")

        # Test validation - too few frames
        try:
            AnimationParams(
                num_frames=2,  # Too few (min is 4)
                motion_type="linear",
                speed="normal",
                emphasis="Test"
            )
            print("   ✗ Should have rejected num_frames=2")
            return False
        except Exception:
            print("   ✓ Correctly rejected num_frames=2")

        # Test validation - too many frames
        try:
            AnimationParams(
                num_frames=50,  # Too many (max is 32)
                motion_type="linear",
                speed="normal",
                emphasis="Test"
            )
            print("   ✗ Should have rejected num_frames=50")
            return False
        except Exception:
            print("   ✓ Correctly rejected num_frames=50")

        # Test interpolation times validation
        params_with_times = AnimationParams(
            num_frames=4,
            motion_type="linear",
            speed="normal",
            emphasis="Test",
            interpolation_times=[0.0, 0.25, 0.5, 0.75, 1.0]
        )
        print(f"   ✓ Custom interpolation times accepted")

        print("\n✅ Schema tests PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Schema tests FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("PHASE 1 SERVICE TESTS")
    print("="*60)

    results = {
        "Schemas": test_schemas(),
        "Claude Service": test_claude_service()
    }

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")

    all_passed = all(results.values())
    print("="*60)
    if all_passed:
        print("\n🎉 ALL TESTS PASSED - Phase 1 Complete!")
    else:
        print("\n⚠️  SOME TESTS FAILED - Review errors above")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
