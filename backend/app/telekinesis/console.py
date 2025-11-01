"""
Rich console configuration for Telekinesis system.

Provides beautiful, structured console output for agent execution,
state transitions, and progress monitoring using Rich.
"""

from rich.console import Console
from rich.theme import Theme
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from typing import Dict, Any, List, Optional

# Custom theme for Telekinesis agents
telekinesis_theme = Theme({
    "agent.analyzer": "bold cyan",
    "agent.principles": "bold magenta",
    "agent.planner": "bold yellow",
    "agent.generator": "bold green",
    "agent.validator": "bold blue",
    "agent.refiner": "bold red",
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "info": "cyan",
    "phase": "dim italic",
    "score": "bold white on blue",
})

# Global console instance
console = Console(theme=telekinesis_theme)


def print_agent_start(agent_name: str, iteration: int = 0) -> None:
    """Print formatted agent start message."""
    agent_key = f"agent.{agent_name.lower()}"
    iteration_text = f" [iteration {iteration}]" if iteration > 0 else ""

    console.print(f"\n[{agent_key}]═══ {agent_name.upper()} AGENT{iteration_text} ═══[/{agent_key}]")


def print_agent_complete(agent_name: str, details: Optional[str] = None) -> None:
    """Print formatted agent completion message."""
    agent_key = f"agent.{agent_name.lower()}"
    details_text = f": {details}" if details else ""

    console.print(f"[success]✓[/success] [{agent_key}]{agent_name.upper()}[/{agent_key}] completed{details_text}")


def print_analysis_summary(analysis: Dict[str, Any]) -> None:
    """Print formatted analysis summary."""
    table = Table(title="Analysis Summary", show_header=True, header_style="bold cyan")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Motion Type", str(analysis.get("motion_type", "unknown")))
    table.add_row("Primary Subject", str(analysis.get("primary_subject", "unknown")))
    table.add_row("Style", str(analysis.get("style", "unknown")))

    motion_mag = analysis.get("motion_magnitude", {})
    table.add_row("Translation", str(motion_mag.get("translation", 0)))
    table.add_row("Rotation", str(motion_mag.get("rotation", 0)))

    console.print(table)


def print_principles_summary(principles: Dict[str, Any]) -> None:
    """Print formatted animation principles summary."""
    table = Table(title="Animation Principles Applied", show_header=True, header_style="bold magenta")
    table.add_column("Principle", style="magenta")
    table.add_column("Confidence", style="cyan")
    table.add_column("Reason", style="white")

    for principle in principles.get("applicable_principles", []):
        name = principle.get("principle", "unknown")
        confidence = principle.get("confidence", 0.0)
        reason = principle.get("reason", "")

        confidence_bar = f"{confidence:.1%}"
        table.add_row(name, confidence_bar, reason)

    console.print(table)


def print_plan_summary(plan: Dict[str, Any]) -> None:
    """Print formatted generation plan summary."""
    panel_content = f"""
[bold]Frames:[/bold] {plan.get('num_frames', 0)}
[bold]Timing Curve:[/bold] {plan.get('timing_curve', 'unknown')}
[bold]Arc Type:[/bold] {plan.get('arc_type', 'none')}
[bold]ControlNet:[/bold] {plan.get('controlnet_strategy', 'none')} (strength: {plan.get('controlnet_strength', 0.0)})
[bold]Layered Motion:[/bold] {plan.get('layered_motion', False)}
    """.strip()

    console.print(Panel(panel_content, title="Generation Plan", border_style="yellow"))


def print_generation_progress(current: int, total: int) -> None:
    """Print generation progress."""
    progress_pct = (current / total * 100) if total > 0 else 0
    console.print(f"[green]Generating frames:[/green] {current}/{total} ({progress_pct:.1f}%)")


def print_validation_summary(validation: Dict[str, Any]) -> None:
    """Print formatted validation summary with quality scores."""
    quality_score = validation.get("overall_quality_score", 0.0)

    # Quality score with color based on value
    if quality_score >= 8.0:
        score_style = "bold green"
    elif quality_score >= 6.0:
        score_style = "bold yellow"
    else:
        score_style = "bold red"

    console.print(f"\n[{score_style}]Overall Quality Score: {quality_score:.1f}/10[/{score_style}]")

    # Technical quality metrics
    tech_quality = validation.get("technical_quality", {})
    if tech_quality:
        table = Table(title="Technical Quality Metrics", show_header=True, header_style="bold blue")
        table.add_column("Metric", style="cyan")
        table.add_column("Score", style="white")

        for metric, score in tech_quality.items():
            metric_name = metric.replace("_", " ").title()
            score_pct = f"{score:.1%}" if isinstance(score, (int, float)) else str(score)
            table.add_row(metric_name, score_pct)

        console.print(table)

    # Issues
    issues = validation.get("issues", [])
    if issues:
        console.print("\n[warning]Issues Found:[/warning]")
        for issue in issues:
            console.print(f"  [yellow]•[/yellow] {issue}")

    # Fix suggestions
    suggestions = validation.get("fix_suggestions", [])
    if suggestions:
        console.print("\n[info]Fix Suggestions:[/info]")
        for suggestion in suggestions:
            console.print(f"  [cyan]→[/cyan] {suggestion}")


def print_refinement_summary(refined_count: int, issues_fixed: List[str]) -> None:
    """Print formatted refinement summary."""
    console.print(f"\n[success]Refined {refined_count} frames[/success]")

    if issues_fixed:
        console.print("\n[info]Issues Fixed:[/info]")
        for issue in issues_fixed:
            console.print(f"  [green]✓[/green] {issue}")


def print_phase_badge(phase: int) -> None:
    """Print phase indicator badge."""
    console.print(f"[phase]Phase {phase}[/phase]", end=" ")


def print_iteration_warning(iteration: int, max_iterations: int) -> None:
    """Print iteration warning."""
    console.print(f"\n[warning]⚠ Iteration {iteration}/{max_iterations}[/warning]")


def print_state_tree(state: Dict[str, Any]) -> None:
    """Print state tree visualization."""
    tree = Tree("[bold]Animation State[/bold]")

    # Add key state components
    if "analysis" in state:
        analysis_branch = tree.add("[cyan]Analysis[/cyan]")
        analysis = state["analysis"]
        analysis_branch.add(f"Motion Type: {analysis.get('motion_type', 'unknown')}")
        analysis_branch.add(f"Style: {analysis.get('style', 'unknown')}")

    if "animation_principles" in state:
        principles_branch = tree.add("[magenta]Principles[/magenta]")
        principles = state["animation_principles"]
        for p in principles.get("applicable_principles", [])[:3]:  # Show top 3
            principles_branch.add(f"{p.get('principle', 'unknown')} ({p.get('confidence', 0):.1%})")

    if "plan" in state:
        plan_branch = tree.add("[yellow]Plan[/yellow]")
        plan = state["plan"]
        plan_branch.add(f"Frames: {plan.get('num_frames', 0)}")
        plan_branch.add(f"Timing: {plan.get('timing_curve', 'unknown')}")

    if "frames" in state:
        frames_branch = tree.add("[green]Frames[/green]")
        frames = state["frames"]
        frames_branch.add(f"Generated: {len(frames)} frames")

    if "validation" in state:
        validation_branch = tree.add("[blue]Validation[/blue]")
        validation = state["validation"]
        validation_branch.add(f"Quality Score: {validation.get('overall_quality_score', 0):.1f}/10")

    console.print(tree)


def print_error(message: str, agent_name: Optional[str] = None) -> None:
    """Print formatted error message."""
    prefix = f"[{agent_name.upper()}] " if agent_name else ""
    console.print(f"[error]✗ {prefix}{message}[/error]")


def print_success(message: str) -> None:
    """Print formatted success message."""
    console.print(f"[success]✓ {message}[/success]")


def print_info(message: str) -> None:
    """Print formatted info message."""
    console.print(f"[info]ℹ {message}[/info]")


def create_progress_bar(description: str = "Processing") -> Progress:
    """Create a Rich progress bar for long-running operations."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    )
