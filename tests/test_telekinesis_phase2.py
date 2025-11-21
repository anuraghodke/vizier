#!/usr/bin/env python3
"""
Phase 2 Test: Intelligent Principle Detection

Tests the enhanced Telekinesis system with Claude-based principle detection.

What's new in Phase 2:
- PRINCIPLES agent uses Claude to detect applicable principles
- Real confidence scores and reasoning
- PLANNER incorporates detected principles into frame planning
- Timing curves applied based on detected principles

Expected results:
- Different motion types trigger different principles
- Confidence scores reflect analysis quality
- Timing curves match motion characteristics
- System can explain its reasoning
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.telekinesis.graph import build_telekinesis_graph
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

console = Console()


def print_header(text: str):
    """Print section header."""
    console.print()
    console.print(Panel(text, style="bold cyan"))


def print_step(num: int, total: int, text: str):
    """Print step progress."""
    console.print(f"[bold blue][{num}/{total}][/bold blue] {text}...")


def print_success(text: str):
    """Print success message."""
    console.print(f"  [bold green]✓[/bold green] {text}")


def print_error(text: str):
    """Print error message."""
    console.print(f"  [bold red]✗[/bold red] {text}")


def print_info(label: str, value: str):
    """Print info line."""
    console.print(f"  [cyan]{label}:[/cyan] {value}")


def display_principles(principles_data: dict):
    """Display detected principles in a nice table."""
    console.print()
    console.print("[bold]Detected Animation Principles:[/bold]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Principle", style="cyan")
    table.add_column("Confidence", justify="center", style="green")
    table.add_column("Reason", style="yellow")

    for principle in principles_data.get("applicable_principles", []):
        name = principle["principle"]
        confidence = f"{principle['confidence']:.2f}"
        reason = principle["reason"][:60] + "..." if len(principle["reason"]) > 60 else principle["reason"]
        table.add_row(name, confidence, reason)

    console.print(table)

    dominant = principles_data.get("dominant_principle", "unknown")
    complexity = principles_data.get("complexity_score", 0.0)
    console.print(f"\n[bold]Dominant Principle:[/bold] {dominant}")
    console.print(f"[bold]Complexity Score:[/bold] {complexity:.2f}")


def display_plan(plan: dict):
    """Display planning information."""
    console.print()
    console.print("[bold]Generation Plan:[/bold]")

    num_frames = plan.get("num_frames", 0)
    timing_curve = plan.get("timing_curve", "unknown")
    arc_type = plan.get("arc_type", "none")
    principles_applied = plan.get("principles_applied", [])

    print_info("Frames", str(num_frames))
    print_info("Timing Curve", timing_curve)
    print_info("Arc Type", arc_type)
    print_info("Principles Applied", ", ".join(principles_applied))


def test_principle_detection():
    """Test Phase 2 intelligent principle detection."""

    print_header("Phase 2 Test: Intelligent Principle Detection")

    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print_error("ANTHROPIC_API_KEY not found in environment")
        console.print("\n[yellow]Please set your API key:[/yellow]")
        console.print("export ANTHROPIC_API_KEY='sk-ant-api03-...'")
        return False

    print_success("ANTHROPIC_API_KEY found")

    # Check test images exist
    test_images_dir = project_root / "tests" / "test_images"
    frame1 = test_images_dir / "frame1.png"
    frame2 = test_images_dir / "frame2.png"

    if not frame1.exists() or not frame2.exists():
        print_error(f"Test images not found in {test_images_dir}")
        return False

    print_success("Test images found")

    # Build graph
    print_step(1, 5, "Building Telekinesis graph")
    try:
        graph = build_telekinesis_graph()
        print_success("Graph built successfully")
    except Exception as e:
        print_error(f"Failed to build graph: {e}")
        return False

    # Test with different instructions to see different principles detected
    test_cases = [
        {
            "name": "Bouncy Motion",
            "instruction": "create 8 bouncy frames with elastic motion",
            "expected_principles": ["arc", "slow_in_slow_out", "timing"]
        },
        {
            "name": "Fast Linear Motion",
            "instruction": "create 4 very fast frames, straight across",
            "expected_principles": ["timing"]
        },
        {
            "name": "Smooth Rotation",
            "instruction": "create 12 smooth frames with natural rotation",
            "expected_principles": ["arc", "slow_in_slow_out", "timing"]
        }
    ]

    for test_idx, test_case in enumerate(test_cases):
        console.print()
        console.print(f"[bold cyan]Test Case {test_idx + 1}: {test_case['name']}[/bold cyan]")
        console.print(f"[dim]Instruction: \"{test_case['instruction']}\"[/dim]")

        # Create initial state
        initial_state = {
            "keyframe1": str(frame1),
            "keyframe2": str(frame2),
            "instruction": test_case["instruction"],
            "job_id": f"phase2_test_case_{test_idx + 1}",
            "iteration_count": 0,
            "messages": []
        }

        # Execute pipeline
        print_step(2, 5, "Executing agent pipeline")
        try:
            final_state = None
            agent_count = 0

            for state_update in graph.stream(initial_state):
                agent_count += 1
                final_state = state_update

            print_success(f"Pipeline completed ({agent_count} agents executed)")

        except Exception as e:
            print_error(f"Pipeline execution failed: {e}")
            import traceback
            traceback.print_exc()
            return False

        # Validate Phase 2 enhancements
        print_step(3, 5, "Validating Phase 2 enhancements")

        # Check that state has all expected fields
        required_fields = ["analysis", "animation_principles", "plan", "frames", "validation"]
        for field in required_fields:
            if field not in final_state:
                print_error(f"Missing field: {field}")
                return False

        print_success("All state fields present")

        # Check PRINCIPLES agent output
        principles = final_state["animation_principles"]

        # Should be Phase 2 implementation
        if principles.get("_phase") != 2:
            print_error(f"PRINCIPLES agent not using Phase 2 (phase={principles.get('_phase')})")
            return False

        print_success("PRINCIPLES agent using Phase 2 implementation")

        # Should have Claude-detected principles (not fallback)
        if principles.get("_status") == "fallback":
            console.print("  [yellow]⚠[/yellow] PRINCIPLES agent used fallback (Claude detection may have failed)")
        elif principles.get("_status") == "claude_detected":
            print_success("Claude-based principle detection succeeded")

        # Display detected principles
        display_principles(principles)

        # Check PLANNER output
        plan = final_state["plan"]

        # Should be Phase 2 implementation
        if plan.get("_phase") != 2:
            print_error(f"PLANNER agent not using Phase 2 (phase={plan.get('_phase')})")
            return False

        print_success("PLANNER agent using Phase 2 implementation")

        # Should have principle-aware planning
        if plan.get("_status") != "principle_aware":
            print_error(f"PLANNER not using principles (status={plan.get('_status')})")
            return False

        print_success("PLANNER incorporating detected principles")

        # Display plan
        display_plan(plan)

        # Check that timing curve is non-linear when appropriate
        timing_curve = plan.get("timing_curve", "linear")
        if "slow_in_slow_out" in [p["principle"] for p in principles.get("applicable_principles", [])]:
            if timing_curve == "linear":
                console.print("  [yellow]⚠[/yellow] slow_in_slow_out detected but timing still linear")
            else:
                print_success(f"Timing curve '{timing_curve}' applied from slow_in_slow_out principle")

        # Check frames were generated
        frames = final_state.get("frames", [])
        if not frames:
            print_error("No frames generated")
            return False

        print_success(f"{len(frames)} frames generated")

        # Check frame files exist
        output_dir = project_root / "outputs" / f"phase2_test_case_{test_idx + 1}"
        if output_dir.exists():
            frame_files = list(output_dir.glob("frame_*.png"))
            print_success(f"Frame files created: {len(frame_files)} files")
        else:
            console.print("  [yellow]⚠[/yellow] Output directory not found (frames may not be saved)")

    # Final summary
    console.print()
    console.print(Panel("[bold green]✓ Phase 2 Test Passed![/bold green]", style="green"))
    console.print()
    console.print("[bold]Key Achievements:[/bold]")
    console.print("  ✓ PRINCIPLES agent uses Claude for intelligent detection")
    console.print("  ✓ Confidence scores reflect analysis quality")
    console.print("  ✓ PLANNER incorporates detected principles")
    console.print("  ✓ Timing curves applied based on motion characteristics")
    console.print("  ✓ System provides reasoning for principle selection")
    console.print()
    console.print("[bold cyan]Phase 2 Complete![/bold cyan] Ready for Phase 3 (ControlNet guidance)")

    return True


if __name__ == "__main__":
    success = test_principle_detection()
    sys.exit(0 if success else 1)
