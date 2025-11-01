"""
Phase 1 Test Script for Telekinesis System

Tests the minimal viable pipeline:
- ANALYZER: Claude Vision analysis
- PRINCIPLES: Hardcoded (no changes from Phase 0)
- PLANNER: Simple linear plan (no changes from Phase 0)
- GENERATOR: Frame interpolation
- VALIDATOR: Stub (always passes)

Expected outcome: Real frames generated with blurry/morphed quality
"""
import os
import sys
import traceback
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client

# Load environment variables (including LangSmith tracing config)
load_dotenv()

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from backend.app.telekinesis.graph import build_telekinesis_graph, run_telekinesis_pipeline
from backend.app.telekinesis.state import AnimationState


def test_phase1_pipeline():
    """Test complete Phase 1 pipeline with real images"""
    print("\n" + "=" * 60)
    print("PHASE 1 TEST: Telekinesis Minimal Viable Pipeline")
    print("=" * 60)

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n[ERROR] ANTHROPIC_API_KEY not set in environment")
        print("Please set it with: export ANTHROPIC_API_KEY='your-key-here'")
        return False

    # Setup test paths
    test_dir = Path(__file__).parent
    test_images_dir = test_dir / "test_images"

    keyframe1 = str(test_images_dir / "frame1.png")
    keyframe2 = str(test_images_dir / "frame2.png")

    # Verify test images exist
    if not Path(keyframe1).exists() or not Path(keyframe2).exists():
        print(f"\n[ERROR] Test images not found:")
        print(f"  {keyframe1}: {Path(keyframe1).exists()}")
        print(f"  {keyframe2}: {Path(keyframe2).exists()}")
        return False

    print(f"\n[SETUP] Using test images:")
    print(f"  Keyframe 1: {keyframe1}")
    print(f"  Keyframe 2: {keyframe2}")

    # Build graph
    print("\n[1/6] Building Telekinesis graph...")
    try:
        graph = build_telekinesis_graph()
        print("  [DONE] Graph built successfully")
    except Exception as e:
        print(f"  [ERROR] Failed to build graph: {e}")
        return False

    # Create initial state
    print("\n[2/6] Creating initial state...")
    initial_state: AnimationState = {
        "keyframe1": keyframe1,
        "keyframe2": keyframe2,
        "instruction": "create 8 smooth frames",
        "job_id": "phase1_test",
        "iteration_count": 0,
        "messages": [],
        "analysis": {},
        "animation_principles": {},
        "plan": {},
        "frames": [],
        "validation": {},
        "refined_frames": []
    }
    print("  [DONE] Initial state created")

    # Execute graph
    print("\n[3/6] Executing agent pipeline...")
    print("  This will take ~10-30 seconds (Claude Vision API calls + frame generation)")
    print()

    try:
        result = None
        agent_count = 0

        for step_output in run_telekinesis_pipeline(graph, initial_state, stream=True):
            agent_count += 1
            agent_name = list(step_output.keys())[0]
            agent_state = step_output[agent_name]

            print(f"  [{agent_count}] {agent_name.upper()} agent completed")

            # Show some details
            if agent_name == "analyzer" and "analysis" in agent_state:
                analysis = agent_state["analysis"]
                print(f"      Motion: {analysis.get('motion_type', 'unknown')}")
                print(f"      Style: {analysis.get('style', 'unknown')}")
                print(f"      Energy: {analysis.get('motion_energy', 'unknown')}")

            elif agent_name == "principles" and "animation_principles" in agent_state:
                principles = agent_state["animation_principles"]
                applicable = principles.get("applicable_principles", [])
                print(f"      Principles: {len(applicable)} identified")
                for p in applicable[:2]:  # Show first 2
                    print(f"        - {p.get('principle', 'unknown')}")

            elif agent_name == "planner" and "plan" in agent_state:
                plan = agent_state["plan"]
                print(f"      Frames planned: {plan.get('num_frames', 0)}")
                print(f"      Timing: {plan.get('timing_curve', 'unknown')}")

            elif agent_name == "generator" and "frames" in agent_state:
                frames = agent_state["frames"]
                print(f"      Frames generated: {len(frames)}")
                if frames:
                    # Check if first frame actually exists
                    first_frame_exists = Path(frames[0]).exists()
                    print(f"      Files created: {first_frame_exists}")

            elif agent_name == "validator" and "validation" in agent_state:
                validation = agent_state["validation"]
                score = validation.get("overall_quality_score", 0)
                print(f"      Quality score: {score}/10")

            result = agent_state

        print(f"\n  [DONE] Pipeline completed ({agent_count} agents executed)")

    except Exception as e:
        print(f"\n  [ERROR] Pipeline execution failed: {e}")
        traceback.print_exc()
        return False

    # Validate results
    print("\n[4/6] Validating results...")

    # Check analysis
    if "analysis" not in result or not result["analysis"]:
        print("  [ERROR] No analysis found in result")
        return False
    else:
        analysis = result["analysis"]
        print(f"  [DONE] Analysis complete:")
        print(f"    Motion type: {analysis.get('motion_type', 'unknown')}")
        print(f"    Subject: {analysis.get('primary_subject', 'unknown')}")

    # Check principles
    if "animation_principles" not in result or not result["animation_principles"]:
        print("  [ERROR] No animation principles found")
        return False
    else:
        principles = result["animation_principles"]
        applicable = principles.get("applicable_principles", [])
        print(f"  [DONE] Principles identified: {len(applicable)}")

    # Check plan
    if "plan" not in result or not result["plan"]:
        print("  [ERROR] No plan found")
        return False
    else:
        plan = result["plan"]
        print(f"  [DONE] Plan created: {plan.get('num_frames', 0)} frames")

    # Check frames
    if "frames" not in result or not result["frames"]:
        print("  [ERROR] No frames generated")
        return False
    else:
        frames = result["frames"]
        print(f"  [DONE] Frames generated: {len(frames)}")

        # Check if files actually exist
        existing_frames = [f for f in frames if Path(f).exists()]
        print(f"    Files on disk: {len(existing_frames)}/{len(frames)}")

        if len(existing_frames) == 0:
            print("  [ERROR] No frame files found on disk")
            return False

    # Check validation
    if "validation" not in result or not result["validation"]:
        print("  [ERROR] No validation found")
        return False
    else:
        validation = result["validation"]
        score = validation.get("overall_quality_score", 0)
        print(f"  [DONE] Validation complete: {score}/10")

    # Show message log
    print("\n[5/6] Agent message log:")
    messages = result.get("messages", [])
    for i, msg in enumerate(messages, 1):
        agent = msg.get("agent", "unknown")
        action = msg.get("action", "unknown")
        details = msg.get("details", "")
        print(f"  [{i}] {agent}: {action}")
        if details:
            print(f"      {details}")

    # Show output location
    print("\n[6/6] Output summary:")
    frames = result.get("frames", [])
    if frames:
        output_dir = Path(frames[0]).parent
        print(f"  Output directory: {output_dir}")
        print(f"  Total frames: {len(frames)}")
        print(f"  Frame paths:")
        for frame in frames[:3]:  # Show first 3
            exists = "[EXISTS]" if Path(frame).exists() else "[MISSING]"
            print(f"    {exists} {frame}")
        if len(frames) > 3:
            print(f"    ... and {len(frames) - 3} more")

    print("\n" + "=" * 60)
    print("[SUCCESS] Phase 1 Pipeline Test Passed!")
    print("=" * 60)
    print("\nPhase 1 Status:")
    print("  [DONE] ANALYZER: Claude Vision analysis working")
    print("  [DONE] PRINCIPLES: Hardcoded principles (as expected)")
    print("  [DONE] PLANNER: Simple linear planning (as expected)")
    print("  [DONE] GENERATOR: Frame interpolation working")
    print("  [DONE] VALIDATOR: Stub validator (as expected)")
    print("\nNext steps:")
    print("  - Review generated frames in output directory")
    print("  - Quality will be blurry/morphed (expected for Phase 1)")
    print("  - Phase 2 will add real principle detection")
    print("  - Phase 3 will add ControlNet for better structure")
    print()

    return True


if __name__ == "__main__":
    try:
        success = test_phase1_pipeline()
        sys.exit(0 if success else 1)
    finally:
        # Flush LangSmith traces before exit
        try:
            client = Client()
            print("\n[Flushing LangSmith traces...]")
            client.flush()
            print("[LangSmith traces flushed successfully]")
        except Exception as e:
            print(f"[Warning: Failed to flush LangSmith traces: {e}]")
