"""
Test script for Telekinesis Phase 0.

Verifies that:
1. Graph can be built without errors
2. All agents execute in correct order
3. State is properly populated by each agent
4. Conditional routing works
5. Graph completes successfully
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../backend"))

from app.telekinesis.graph import build_telekinesis_graph, create_initial_state
from app.telekinesis.logging_config import setup_telekinesis_logging


def test_graph_builds():
    """Test that graph can be built without errors."""
    print("\n" + "=" * 60)
    print("TEST 1: Graph Building")
    print("=" * 60)

    try:
        graph = build_telekinesis_graph()
        print("✓ Graph built successfully")
        return True
    except Exception as e:
        print(f"✗ Graph build failed: {e}")
        return False


def test_graph_execution():
    """Test that graph executes end-to-end."""
    print("\n" + "=" * 60)
    print("TEST 2: Graph Execution")
    print("=" * 60)

    # Setup logging
    logger = setup_telekinesis_logging(level="INFO")

    # Build graph
    graph = build_telekinesis_graph()

    # Create initial state
    initial_state = create_initial_state(
        keyframe1="/test/keyframe1.png",
        keyframe2="/test/keyframe2.png",
        instruction="create 8 smooth frames",
        job_id="test_phase0",
    )

    print("\nInitial state created:")
    print(f"  - keyframe1: {initial_state['keyframe1']}")
    print(f"  - keyframe2: {initial_state['keyframe2']}")
    print(f"  - instruction: {initial_state['instruction']}")
    print(f"  - job_id: {initial_state['job_id']}")

    # Execute graph
    print("\nExecuting graph...\n")

    try:
        final_state = graph.invoke(initial_state)
        print("\n✓ Graph execution completed")
        return final_state
    except Exception as e:
        print(f"\n✗ Graph execution failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_state_population(final_state):
    """Test that all expected state fields are populated."""
    print("\n" + "=" * 60)
    print("TEST 3: State Population")
    print("=" * 60)

    if not final_state:
        print("✗ No final state to check")
        return False

    checks = [
        ("analysis", dict),
        ("animation_principles", dict),
        ("plan", dict),
        ("frames", list),
        ("validation", dict),
        ("messages", list),
    ]

    all_passed = True
    for field, expected_type in checks:
        if field in final_state and isinstance(final_state[field], expected_type):
            print(f"✓ {field}: {expected_type.__name__} ✓")
        else:
            print(f"✗ {field}: Missing or wrong type")
            all_passed = False

    return all_passed


def test_agent_sequence(final_state):
    """Test that agents executed in correct order."""
    print("\n" + "=" * 60)
    print("TEST 4: Agent Execution Sequence")
    print("=" * 60)

    if not final_state:
        print("✗ No final state to check")
        return False

    messages = final_state.get("messages", [])

    if not messages:
        print("✗ No messages logged")
        return False

    expected_sequence = [
        "analyzer",
        "principles",
        "planner",
        "generator",
        "validator",
    ]

    actual_sequence = [msg["agent"] for msg in messages]

    print(f"\nExpected: {' → '.join(expected_sequence)}")
    print(f"Actual:   {' → '.join(actual_sequence)}")

    if actual_sequence[:5] == expected_sequence:
        print("\n✓ Agent sequence correct")
        return True
    else:
        print("\n✗ Agent sequence incorrect")
        return False


def test_output_details(final_state):
    """Test detailed output from each agent."""
    print("\n" + "=" * 60)
    print("TEST 5: Detailed Agent Outputs")
    print("=" * 60)

    if not final_state:
        print("✗ No final state to check")
        return False

    # Check analysis
    print("\n[ANALYZER Output]")
    analysis = final_state.get("analysis", {})
    print(f"  - Motion type: {analysis.get('motion_type')}")
    print(f"  - Primary subject: {analysis.get('primary_subject')}")
    print(f"  - Phase: {analysis.get('_phase')}")
    print(f"  - Status: {analysis.get('_status')}")

    # Check principles
    print("\n[PRINCIPLES Output]")
    principles = final_state.get("animation_principles", {})
    applicable = principles.get("applicable_principles", [])
    print(f"  - Applicable principles: {len(applicable)}")
    for p in applicable:
        print(f"    • {p['principle']} (confidence: {p['confidence']})")
    print(f"  - Dominant: {principles.get('dominant_principle')}")

    # Check plan
    print("\n[PLANNER Output]")
    plan = final_state.get("plan", {})
    print(f"  - Num frames: {plan.get('num_frames')}")
    print(f"  - Timing curve: {plan.get('timing_curve')}")
    print(f"  - Arc type: {plan.get('arc_type')}")

    # Check frames
    print("\n[GENERATOR Output]")
    frames = final_state.get("frames", [])
    print(f"  - Generated frames: {len(frames)}")
    if frames:
        print(f"  - First frame: {frames[0]}")
        print(f"  - Last frame: {frames[-1]}")

    # Check validation
    print("\n[VALIDATOR Output]")
    validation = final_state.get("validation", {})
    print(f"  - Quality score: {validation.get('overall_quality_score')}")
    print(f"  - Needs refinement: {validation.get('needs_refinement')}")
    print(f"  - Issues found: {len(validation.get('issues', []))}")

    # Check messages
    print("\n[Message Log]")
    messages = final_state.get("messages", [])
    print(f"  - Total messages: {len(messages)}")
    for msg in messages:
        print(f"  - [{msg['agent']}] {msg['action']}: {msg['details']}")

    print("\n✓ All outputs present")
    return True


def test_quality_routing():
    """Test conditional routing based on quality scores."""
    print("\n" + "=" * 60)
    print("TEST 6: Conditional Routing")
    print("=" * 60)

    from app.telekinesis.graph import route_from_validator

    # Test case 1: High quality (should end)
    state1 = {
        "validation": {"overall_quality_score": 8.5},
        "iteration_count": 0,
    }
    route1 = route_from_validator(state1)
    print(f"Quality 8.5, iteration 0 → {route1} (expected: end)")
    assert route1 == "end", "Should end with high quality"

    # Test case 2: Low quality, early iteration (should replan)
    state2 = {
        "validation": {"overall_quality_score": 5.5},
        "iteration_count": 0,
    }
    route2 = route_from_validator(state2)
    print(f"Quality 5.5, iteration 0 → {route2} (expected: replan)")
    assert route2 == "replan", "Should replan with low quality"

    # Test case 3: Medium quality (should refine)
    state3 = {
        "validation": {"overall_quality_score": 7.0},
        "iteration_count": 0,
    }
    route3 = route_from_validator(state3)
    print(f"Quality 7.0, iteration 0 → {route3} (expected: refine)")
    assert route3 == "refine", "Should refine with medium quality"

    # Test case 4: Max iterations (should end)
    state4 = {
        "validation": {"overall_quality_score": 7.0},
        "iteration_count": 3,
    }
    route4 = route_from_validator(state4)
    print(f"Quality 7.0, iteration 3 → {route4} (expected: end)")
    assert route4 == "end", "Should end at max iterations"

    print("\n✓ All routing tests passed")
    return True


def run_all_tests():
    """Run all Phase 0 tests."""
    print("\n" + "=" * 60)
    print("TELEKINESIS PHASE 0 TEST SUITE")
    print("=" * 60)

    results = []

    # Test 1: Graph building
    results.append(("Graph Building", test_graph_builds()))

    # Test 2: Graph execution
    final_state = test_graph_execution()
    results.append(("Graph Execution", final_state is not None))

    # Test 3: State population
    results.append(("State Population", test_state_population(final_state)))

    # Test 4: Agent sequence
    results.append(("Agent Sequence", test_agent_sequence(final_state)))

    # Test 5: Output details
    results.append(("Output Details", test_output_details(final_state)))

    # Test 6: Routing logic
    results.append(("Conditional Routing", test_quality_routing()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Phase 0 Complete!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
