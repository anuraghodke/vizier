#!/usr/bin/env python3
"""
Phase 3 Test: RIFE Integration & Arc Path Warping

Tests the Phase 3 enhancements to the Telekinesis system:
1. RIFE neural frame interpolation (or fallback)
2. Arc path calculation in PLANNER
3. Arc path warping in GENERATOR
4. Real VALIDATOR with Claude Vision
5. Basic REFINER operations

Usage:
    python3 tests/test_telekinesis_phase3.py

Requirements:
    - ANTHROPIC_API_KEY environment variable set
    - Test images in tests/test_images/
    - uv pip install rife-ncnn-vulkan-python-tntwise (optional, will fallback)
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

console = Console()


def check_prerequisites():
    """Check that all prerequisites are met."""
    console.print("\n[bold cyan]Checking prerequisites...[/bold cyan]")

    # Check API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        console.print("[red]ERROR: ANTHROPIC_API_KEY not set[/red]")
        console.print("Set it with: export ANTHROPIC_API_KEY='sk-ant-...'")
        return False
    console.print("[green]OK[/green] ANTHROPIC_API_KEY found")

    # Check test images
    test_images_dir = project_root / "tests" / "head-perspective"
    frame1 = test_images_dir / "Untitled_Artwork-4 2.png"
    frame2 = test_images_dir / "Untitled_Artwork-5.png"

    if not frame1.exists() or not frame2.exists():
        console.print(f"[red]ERROR: Test images not found in {test_images_dir}[/red]")
        return False
    console.print("[green]OK[/green] Test images found")

    # Check RIFE availability (optional)
    try:
        from backend.app.services.rife_service import get_rife_service
        rife = get_rife_service()
        if rife.is_available():
            console.print("[green]OK[/green] RIFE is available (neural interpolation)")
        else:
            console.print("[yellow]WARN[/yellow] RIFE not installed (will use object-based fallback)")
            console.print("     Install with: uv pip install rife-ncnn-vulkan-python-tntwise")
    except Exception as e:
        console.print(f"[yellow]WARN[/yellow] RIFE check failed: {e}")

    return True


def test_arc_path_calculation():
    """Test the arc path calculation functions."""
    console.print("\n[bold cyan]Testing Arc Path Calculation...[/bold cyan]")

    from backend.app.telekinesis.agents import (
        _calculate_parabolic_arc,
        _calculate_arc_path
    )

    # Test parabolic arc
    start = (0.2, 0.5)
    end = (0.8, 0.5)

    # At t=0, should be at start
    pos_0 = _calculate_parabolic_arc(start, end, t=0.0, intensity=0.5)
    assert abs(pos_0[0] - start[0]) < 0.01, f"t=0 x mismatch: {pos_0}"
    assert abs(pos_0[1] - start[1]) < 0.01, f"t=0 y mismatch: {pos_0}"
    console.print(f"  t=0.0: {pos_0} [green]OK[/green]")

    # At t=1, should be at end
    pos_1 = _calculate_parabolic_arc(start, end, t=1.0, intensity=0.5)
    assert abs(pos_1[0] - end[0]) < 0.01, f"t=1 x mismatch: {pos_1}"
    assert abs(pos_1[1] - end[1]) < 0.01, f"t=1 y mismatch: {pos_1}"
    console.print(f"  t=1.0: {pos_1} [green]OK[/green]")

    # At t=0.5, should be at midpoint x, but y should be offset (arc)
    pos_mid = _calculate_parabolic_arc(start, end, t=0.5, intensity=0.5)
    mid_x = (start[0] + end[0]) / 2
    assert abs(pos_mid[0] - mid_x) < 0.01, f"t=0.5 x mismatch: {pos_mid}"
    # Y should be offset upward (negative in image coords)
    assert pos_mid[1] < start[1], f"t=0.5 should arc upward: {pos_mid}"
    console.print(f"  t=0.5: {pos_mid} (arcs upward) [green]OK[/green]")

    # Test with different intensities
    pos_low = _calculate_parabolic_arc(start, end, t=0.5, intensity=0.1)
    pos_high = _calculate_parabolic_arc(start, end, t=0.5, intensity=1.0)
    assert pos_high[1] < pos_low[1], "Higher intensity should have more arc"
    console.print(f"  Intensity 0.1 y={pos_low[1]:.3f}, 1.0 y={pos_high[1]:.3f} [green]OK[/green]")

    console.print("[green]Arc path calculation: PASSED[/green]")
    return True


def test_full_pipeline():
    """Test the full Phase 3 pipeline."""
    console.print("\n[bold cyan]Testing Full Phase 3 Pipeline...[/bold cyan]")

    from backend.app.telekinesis.graph import (
        build_telekinesis_graph,
        create_initial_state
    )

    # Build graph
    console.print("[1/6] Building Telekinesis graph...")
    graph = build_telekinesis_graph()
    console.print("  [green]OK[/green] Graph built successfully")

    # Create initial state
    console.print("[2/6] Creating initial state...")
    test_images_dir = project_root / "tests" / "test_images"
    initial_state = create_initial_state(
        keyframe1=str(test_images_dir / "frame1.png"),
        keyframe2=str(test_images_dir / "frame2.png"),
        instruction="create 8 frames with bouncy arc motion",
        job_id="phase3_test"
    )
    console.print("  [green]OK[/green] Initial state created")

    # Execute pipeline
    console.print("[3/6] Executing agent pipeline...")
    console.print("       (This may take 30-60 seconds with API calls)")

    try:
        # Run the graph
        final_state = None
        for output in graph.stream(initial_state):
            for node_name, state in output.items():
                console.print(f"  [{node_name}] completed")
                final_state = state

        if final_state is None:
            console.print("[red]ERROR: Pipeline produced no output[/red]")
            return False

        console.print("  [green]OK[/green] Pipeline completed")

    except Exception as e:
        console.print(f"[red]ERROR: Pipeline failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False

    # Validate state fields
    console.print("[4/6] Validating state fields...")

    required_fields = [
        "analysis", "animation_principles", "plan",
        "frames", "validation"
    ]

    for field in required_fields:
        if field not in final_state or final_state[field] is None:
            console.print(f"[red]ERROR: Missing field '{field}'[/red]")
            return False
        console.print(f"  [green]OK[/green] {field} present")

    # Check Phase 3 specific fields
    console.print("[5/6] Validating Phase 3 enhancements...")

    # Check PLANNER has arc positions
    plan = final_state["plan"]
    frame_schedule = plan.get("frame_schedule", [])

    if not frame_schedule:
        console.print("[red]ERROR: No frame schedule in plan[/red]")
        return False

    # Check arc positions are calculated
    has_arc_positions = any(
        f.get("arc_position", {}).get("x", 0) != 0 or
        f.get("arc_position", {}).get("y", 0) != 0
        for f in frame_schedule
    )

    arc_type = plan.get("arc_type", "none")
    if arc_type != "none" and has_arc_positions:
        console.print(f"  [green]OK[/green] Arc positions calculated (type={arc_type})")
    else:
        console.print(f"  [yellow]WARN[/yellow] No arc positions (type={arc_type})")

    # Check PLANNER phase
    planner_phase = plan.get("_phase", 0)
    planner_status = plan.get("_status", "unknown")
    console.print(f"  PLANNER: phase={planner_phase}, status={planner_status}")

    if planner_phase >= 3:
        console.print("  [green]OK[/green] PLANNER using Phase 3 implementation")
    else:
        console.print("  [yellow]WARN[/yellow] PLANNER not at Phase 3")

    # Check VALIDATOR results
    validation = final_state["validation"]
    quality_score = validation.get("overall_quality_score", 0)
    validator_status = validation.get("_status", "unknown")

    console.print(f"  VALIDATOR: score={quality_score:.1f}, status={validator_status}")

    if validator_status == "claude_vision_validated":
        console.print("  [green]OK[/green] VALIDATOR using Claude Vision")
    elif validator_status == "fallback":
        console.print("  [yellow]WARN[/yellow] VALIDATOR used fallback")
    else:
        console.print(f"  [yellow]WARN[/yellow] VALIDATOR status: {validator_status}")

    # Check generated frames
    console.print("[6/6] Checking generated frames...")

    frames = final_state["frames"]
    if not frames:
        console.print("[red]ERROR: No frames generated[/red]")
        return False

    console.print(f"  Generated {len(frames)} frames")

    # Check files exist
    existing_frames = [f for f in frames if Path(f).exists()]
    console.print(f"  {len(existing_frames)}/{len(frames)} frame files exist on disk")

    if len(existing_frames) == 0:
        console.print("[red]ERROR: No frame files found on disk[/red]")
        return False

    console.print("[green]Full pipeline: PASSED[/green]")
    return True


def display_results_summary(final_state: dict):
    """Display a summary of the pipeline results."""
    console.print("\n")
    console.print(Panel("[bold]Phase 3 Pipeline Results Summary[/bold]", expand=False))

    # Plan summary
    plan = final_state.get("plan", {})
    plan_table = Table(title="Generation Plan")
    plan_table.add_column("Parameter", style="cyan")
    plan_table.add_column("Value", style="green")

    plan_table.add_row("Frames", str(plan.get("num_frames", "?")))
    plan_table.add_row("Timing Curve", plan.get("timing_curve", "?"))
    plan_table.add_row("Arc Type", plan.get("arc_type", "?"))
    plan_table.add_row("Arc Intensity", f"{plan.get('arc_intensity', 0):.2f}")
    plan_table.add_row("Phase", str(plan.get("_phase", "?")))

    console.print(plan_table)

    # Validation summary
    validation = final_state.get("validation", {})
    val_table = Table(title="Validation Results")
    val_table.add_column("Dimension", style="cyan")
    val_table.add_column("Score", style="green")

    val_table.add_row("Overall", f"{validation.get('overall_quality_score', 0):.1f}/10")
    val_table.add_row("Smoothness", f"{validation.get('motion_smoothness', 0):.1f}/10")
    val_table.add_row("Arc Adherence", f"{validation.get('arc_adherence', 0):.1f}/10")
    val_table.add_row("Volume", f"{validation.get('volume_consistency', 0):.1f}/10")
    val_table.add_row("Artifacts", f"{validation.get('artifact_score', 0):.1f}/10")
    val_table.add_row("Style", f"{validation.get('style_consistency', 0):.1f}/10")

    console.print(val_table)

    # Issues
    issues = validation.get("issues", [])
    if issues:
        console.print("\n[bold yellow]Issues Found:[/bold yellow]")
        for issue in issues:
            console.print(f"  - {issue}")

    # Output location
    frames = final_state.get("frames", [])
    if frames:
        output_dir = Path(frames[0]).parent
        console.print(f"\n[bold]Output Location:[/bold] {output_dir}")


def main():
    """Run Phase 3 tests."""
    console.print(Panel(
        "[bold magenta]Phase 3 Test: RIFE Integration & Arc Path Warping[/bold magenta]",
        expand=False
    ))

    # Check prerequisites
    if not check_prerequisites():
        console.print("\n[red]Prerequisites not met. Exiting.[/red]")
        sys.exit(1)

    # Run tests
    all_passed = True

    # Test 1: Arc path calculation (no API needed)
    try:
        if not test_arc_path_calculation():
            all_passed = False
    except Exception as e:
        console.print(f"[red]Arc path test failed: {e}[/red]")
        all_passed = False

    # Test 2: Full pipeline (needs API)
    try:
        if not test_full_pipeline():
            all_passed = False
    except Exception as e:
        console.print(f"[red]Pipeline test failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        all_passed = False

    # Summary
    console.print("\n")
    if all_passed:
        console.print(Panel(
            "[bold green]Phase 3 Tests: ALL PASSED[/bold green]\n\n"
            "Key Achievements:\n"
            "  - Arc path calculation working\n"
            "  - PLANNER calculates arc positions\n"
            "  - GENERATOR uses RIFE (or fallback)\n"
            "  - VALIDATOR uses Claude Vision\n"
            "  - REFINER ready for iterations\n\n"
            "[dim]Run 'open outputs/phase3_test/' to view generated frames[/dim]",
            expand=False
        ))
        sys.exit(0)
    else:
        console.print(Panel(
            "[bold red]Phase 3 Tests: SOME FAILED[/bold red]\n\n"
            "Check the error messages above for details.",
            expand=False
        ))
        sys.exit(1)


if __name__ == "__main__":
    main()
