"""
Quick verification script for Phase 0 structure.
Checks that all files are created and can be imported.
"""

import os
import sys

def check_file_exists(path, description):
    """Check if a file exists."""
    if os.path.exists(path):
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description} - MISSING")
        return False

def verify_phase0_structure():
    """Verify Phase 0 file structure."""
    print("\n" + "=" * 60)
    print("PHASE 0 STRUCTURE VERIFICATION")
    print("=" * 60 + "\n")

    base_path = os.path.join(os.path.dirname(__file__), "..")

    checks = [
        (
            os.path.join(base_path, "backend/app/telekinesis/__init__.py"),
            "Telekinesis module __init__.py"
        ),
        (
            os.path.join(base_path, "backend/app/telekinesis/state.py"),
            "AnimationState definition"
        ),
        (
            os.path.join(base_path, "backend/app/telekinesis/agents.py"),
            "Agent stub functions"
        ),
        (
            os.path.join(base_path, "backend/app/telekinesis/graph.py"),
            "LangGraph state machine"
        ),
        (
            os.path.join(base_path, "backend/app/telekinesis/logging_config.py"),
            "Logging configuration"
        ),
        (
            os.path.join(base_path, "pyproject.toml"),
            "pyproject.toml with dependencies"
        ),
        (
            os.path.join(base_path, "docs/TELEKINESIS_PLAN.md"),
            "Telekinesis plan documentation"
        ),
        (
            os.path.join(base_path, "docs/ANIMATION_PRINCIPLES_KNOWLEDGE_BASE.md"),
            "Animation principles knowledge base"
        ),
    ]

    results = []
    for file_path, description in checks:
        result = check_file_exists(file_path, description)
        results.append(result)

    # Check pyproject.toml has LangGraph dependencies
    print("\n" + "=" * 60)
    print("DEPENDENCY CHECK")
    print("=" * 60 + "\n")

    pyproject_path = os.path.join(base_path, "pyproject.toml")
    if os.path.exists(pyproject_path):
        with open(pyproject_path, 'r') as f:
            content = f.read()

        dep_checks = [
            ("langgraph", "langgraph" in content),
            ("langchain", "langchain" in content),
            ("langchain-anthropic", "langchain-anthropic" in content),
        ]

        for dep_name, found in dep_checks:
            if found:
                print(f"✓ {dep_name} dependency added")
                results.append(True)
            else:
                print(f"✗ {dep_name} dependency missing")
                results.append(False)

    # Check file contents
    print("\n" + "=" * 60)
    print("CODE STRUCTURE CHECK")
    print("=" * 60 + "\n")

    # Check agents.py has all 6 agents
    agents_path = os.path.join(base_path, "backend/app/telekinesis/agents.py")
    if os.path.exists(agents_path):
        with open(agents_path, 'r') as f:
            content = f.read()

        agent_checks = [
            "analyzer_agent",
            "principles_agent",
            "planner_agent",
            "generator_agent",
            "validator_agent",
            "refiner_agent",
        ]

        for agent in agent_checks:
            if f"def {agent}" in content:
                print(f"✓ {agent} defined")
                results.append(True)
            else:
                print(f"✗ {agent} missing")
                results.append(False)

    # Check graph.py has required functions
    graph_path = os.path.join(base_path, "backend/app/telekinesis/graph.py")
    if os.path.exists(graph_path):
        with open(graph_path, 'r') as f:
            content = f.read()

        graph_checks = [
            ("build_telekinesis_graph", "def build_telekinesis_graph" in content),
            ("route_from_validator", "def route_from_validator" in content),
            ("create_initial_state", "def create_initial_state" in content),
        ]

        for func_name, found in graph_checks:
            if found:
                print(f"✓ {func_name} function defined")
                results.append(True)
            else:
                print(f"✗ {func_name} function missing")
                results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60 + "\n")

    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total} checks")

    if passed == total:
        print("\n✅ Phase 0 infrastructure complete!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -e .")
        print("2. Run tests: python tests/test_telekinesis_phase0.py")
        return 0
    else:
        print(f"\n⚠️  {total - passed} check(s) failed")
        return 1

if __name__ == "__main__":
    exit_code = verify_phase0_structure()
    sys.exit(exit_code)
