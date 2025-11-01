"""
LangGraph state machine for Telekinesis animation system.

This module builds the agent graph with conditional routing based on
quality scores and iteration counts.
"""

import logging
from typing import Literal
from langgraph.graph import StateGraph, END
from langsmith import traceable
from langsmith.run_helpers import get_current_run_tree
from .state import AnimationState
from .agents import (
    analyzer_agent,
    principles_agent,
    planner_agent,
    generator_agent,
    validator_agent,
    refiner_agent,
)

logger = logging.getLogger(__name__)


def route_from_validator(
    state: AnimationState,
) -> Literal["refine", "replan", "end"]:
    """
    Conditional routing from VALIDATOR agent.

    Decision logic:
    - If quality >= 8.0: Done (end)
    - If quality < 6.0 and iteration < 2: Re-plan (back to planner)
    - If quality >= 6.0 and iteration < 3: Refine (to refiner)
    - If iteration >= 3: Give up (end)

    Args:
        state: Current animation state

    Returns:
        Next node: "refine", "replan", or "end"
    """
    validation = state.get("validation", {})
    iteration = state.get("iteration_count", 0)
    quality = validation.get("overall_quality_score", 0.0)

    logger.info(
        f"Validator routing: quality={quality:.1f}, iteration={iteration}"
    )

    # Good enough - we're done
    if quality >= 8.0:
        logger.info("Quality score >= 8.0 - ending graph")
        return "end"

    # Poor quality and early iterations - try replanning
    if quality < 6.0 and iteration < 2:
        logger.info("Quality score < 6.0 - replanning")
        state["iteration_count"] = iteration + 1
        return "replan"

    # Medium quality and budget remains - refine
    if quality >= 6.0 and iteration < 3:
        logger.info("Quality score >= 6.0 - refining")
        state["iteration_count"] = iteration + 1
        return "refine"

    # Out of iterations - accept result
    logger.info(f"Max iterations reached ({iteration}) - ending graph")
    return "end"


def build_telekinesis_graph() -> StateGraph:
    """
    Build the Telekinesis agent graph.

    Graph structure:
    START → ANALYZER → PRINCIPLES → PLANNER → GENERATOR → VALIDATOR
                                        ↑                      ↓
                                        |                  (conditional)
                                        |                      ↓
                                        └──────← REFINER ←─────┘
                                                    ↓
                                                VALIDATOR → END

    Returns:
        Compiled StateGraph ready for execution
    """
    logger.info("Building Telekinesis graph")

    # Create graph
    workflow = StateGraph(AnimationState)

    # Add all agent nodes
    workflow.add_node("analyzer", analyzer_agent)
    workflow.add_node("principles", principles_agent)
    workflow.add_node("planner", planner_agent)
    workflow.add_node("generator", generator_agent)
    workflow.add_node("validator", validator_agent)
    workflow.add_node("refiner", refiner_agent)

    # Define linear flow for main path
    workflow.set_entry_point("analyzer")
    workflow.add_edge("analyzer", "principles")
    workflow.add_edge("principles", "planner")
    workflow.add_edge("planner", "generator")
    workflow.add_edge("generator", "validator")

    # Conditional routing from validator
    workflow.add_conditional_edges(
        "validator",
        route_from_validator,
        {
            "refine": "refiner",
            "replan": "planner",
            "end": END,
        },
    )

    # Refiner always goes back to validator for re-check
    workflow.add_edge("refiner", "validator")

    # Compile the graph
    compiled = workflow.compile()

    logger.info("Telekinesis graph built successfully")
    return compiled


@traceable(
    run_type="chain",
    name="Telekinesis",
    metadata={
        "component": "telekinesis",
        "pipeline": "animation_generation"
    }
)
def run_telekinesis_pipeline(
    graph,
    initial_state: AnimationState,
    stream: bool = False,
):
    """
    Execute the Telekinesis graph with tracing.

    This wrapper ensures all agent traces are grouped under a single
    parent trace for the entire pipeline execution.

    Args:
        graph: Compiled Telekinesis graph
        initial_state: Initial animation state
        stream: If True, returns a generator for streaming; if False, returns final state

    Returns:
        Final animation state (if stream=False) or generator (if stream=True)
    """
    job_id = initial_state.get('job_id', 'unknown')
    instruction = initial_state.get('instruction', 'N/A')

    # Add metadata to current run
    run_tree = get_current_run_tree()
    if run_tree:
        run_tree.extra = {
            "job_id": job_id,
            "instruction": instruction,
            "keyframe1": initial_state.get('keyframe1', ''),
            "keyframe2": initial_state.get('keyframe2', ''),
        }
        run_tree.tags = ["telekinesis", f"job:{job_id}"]

    logger.info(f"Starting Telekinesis pipeline for job: {job_id}")

    if stream:
        # Streaming mode: yield each step and return final state
        result = None
        for step_output in graph.stream(initial_state):
            result = step_output
            yield step_output
        logger.info(f"Telekinesis pipeline completed for job: {job_id}")
        return result
    else:
        # Blocking mode: return final state
        result = graph.invoke(initial_state)
        logger.info(f"Telekinesis pipeline completed for job: {job_id}")
        return result


def create_initial_state(
    keyframe1: str,
    keyframe2: str,
    instruction: str,
    job_id: str = "test_job",
) -> AnimationState:
    """
    Create initial state for graph execution.

    Args:
        keyframe1: Path to first keyframe
        keyframe2: Path to second keyframe
        instruction: Natural language instruction
        job_id: Optional job ID for tracking

    Returns:
        Initial AnimationState ready for graph execution
    """
    return AnimationState(
        # Input fields
        keyframe1=keyframe1,
        keyframe2=keyframe2,
        instruction=instruction,
        job_id=job_id,
        # Agent output fields (empty initially)
        analysis={},
        animation_principles={},
        plan={},
        frames=[],
        validation={},
        refined_frames=[],
        # Control flow fields
        iteration_count=0,
        messages=[],
        # Optional fields
        error="",
    )
