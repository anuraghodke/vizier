"""
Agent functions for Telekinesis system.

Phase 0: Minimal stubs with placeholder data
Phase 1: ANALYZER uses Claude Vision, GENERATOR uses AnimateDiff (basic)
"""

import logging
from datetime import datetime
from typing import Dict, Any
from langsmith import traceable
from .state import AnimationState
from .console import (
    print_agent_start,
    print_agent_complete,
    print_analysis_summary,
    print_principles_summary,
    print_plan_summary,
    print_generation_progress,
    print_validation_summary,
    print_refinement_summary,
    print_phase_badge,
)

logger = logging.getLogger(__name__)


@traceable(run_type="agent", name="Analyzer Agent")
def analyzer_agent(state: AnimationState) -> AnimationState:
    """
    ANALYZER AGENT - Phase 1 Implementation

    Purpose: Analyze keyframes to understand motion, style, and structure.

    Phase 1: Claude Vision analysis of keyframes
    Future phases will add:
    - MediaPipe pose detection
    - OpenCV segmentation
    - Advanced motion magnitude calculation
    """
    iteration = state.get("iteration_count", 0)
    print_agent_start("analyzer", iteration)
    print_phase_badge(0)

    keyframe1 = state.get("keyframe1", "")
    keyframe2 = state.get("keyframe2", "")
    instruction = state.get("instruction", "")

    try:
        # Import vision service
        from ..services.claude_vision_service import get_vision_service

        # Analyze keyframes with Claude Vision
        vision_service = get_vision_service()
        analysis = vision_service.analyze_keyframes(
            keyframe1_path=keyframe1,
            keyframe2_path=keyframe2,
            instruction=instruction
        )

        logger.info(
            f"ANALYZER: Motion type={analysis.get('motion_type')}, "
            f"Style={analysis.get('style')}"
        )

    except Exception as e:
        # Fallback to placeholder if vision analysis fails
        logger.error(f"ANALYZER vision analysis failed: {e}")
        logger.warning("ANALYZER falling back to placeholder analysis")

        analysis = {
            "motion_type": "unknown",
            "primary_subject": "detected_object",
            "motion_magnitude": {"distance_percent": 0, "rotation_degrees": 0},
            "motion_direction": {"description": "unknown", "arc_detected": False},
            "motion_energy": "medium",
            "style": "unknown",
            "parts_analysis": {"moving_parts": [], "static_parts": []},
            "visual_characteristics": {
                "has_deformation": False,
                "has_motion_blur": False,
                "has_transparency": True,
                "num_objects": 1,
                "has_background": False
            },
            "pose_data": {},
            "object_segments": [],
            "color_palette": [],
            "volume_analysis": {},
            "animation_suggestion": "Error during analysis",
            "_phase": 1,
            "_status": "fallback",
            "_error": str(e)
        }

    state["analysis"] = analysis

    # Append message to existing messages
    messages = state.get("messages", []).copy()
    messages.append({
        "agent": "analyzer",
        "timestamp": datetime.now().isoformat(),
        "action": "completed_analysis",
        "details": f"Phase 1 - Claude Vision analysis: {analysis.get('motion_type', 'unknown')}"
    })
    state["messages"] = messages

    print_analysis_summary(analysis)
    print_agent_complete("analyzer", "placeholder analysis generated")
    return state


@traceable(run_type="agent", name="Principles Agent")
def principles_agent(state: AnimationState) -> AnimationState:
    """
    PRINCIPLES AGENT - Phase 0 Stub

    Purpose: Determine which of the 12 animation principles apply.

    Phase 0: Returns hardcoded principles.
    Future phases will add:
    - Claude reasoning about applicable principles
    - Confidence scoring
    - Parameter extraction from analysis
    """
    iteration = state.get("iteration_count", 0)
    print_agent_start("principles", iteration)
    print_phase_badge(0)

    analysis = state.get("analysis", {})
    logger.info("Identifying applicable animation principles...")

    # Placeholder: Always suggest arc and slow_in_slow_out
    animation_principles = {
        "applicable_principles": [
            {
                "principle": "arc",
                "confidence": 0.8,
                "reason": "Phase 0 stub - default principle",
                "parameters": {"arc_type": "circular"}
            },
            {
                "principle": "slow_in_slow_out",
                "confidence": 0.8,
                "reason": "Phase 0 stub - default principle",
                "parameters": {"ease_type": "ease-in-out"}
            },
            {
                "principle": "timing",
                "confidence": 1.0,
                "reason": "Always applicable",
                "parameters": {"speed_category": "normal"}
            }
        ],
        "dominant_principle": "arc",
        "complexity_score": 0.5,
        "_phase": 0,
        "_status": "stub"
    }

    state["animation_principles"] = animation_principles

    # Append message to existing messages
    messages = state.get("messages", []).copy()
    messages.append({
        "agent": "principles",
        "timestamp": datetime.now().isoformat(),
        "action": "identified_principles",
        "details": "Phase 0 stub - hardcoded principles returned"
    })
    state["messages"] = messages

    print_principles_summary(animation_principles)
    print_agent_complete("principles", "3 principles identified")
    return state


@traceable(run_type="agent", name="Planner Agent")
def planner_agent(state: AnimationState) -> AnimationState:
    """
    PLANNER AGENT - Phase 0 Stub

    Purpose: Create detailed frame-by-frame generation plan.

    Phase 0: Returns simple linear interpolation plan.
    Future phases will add:
    - Arc path calculation
    - Timing curve generation
    - Deformation schedules
    - Motion layer planning
    """
    iteration = state.get("iteration_count", 0)
    print_agent_start("planner", iteration)
    print_phase_badge(0)

    analysis = state.get("analysis", {})
    animation_principles = state.get("animation_principles", {})
    instruction = state.get("instruction", "")

    logger.info("Creating frame-by-frame generation plan...")

    # Placeholder: Simple 8-frame linear plan
    num_frames = 8
    frame_schedule = []

    for i in range(num_frames):
        t = i / (num_frames - 1) if num_frames > 1 else 0.0
        frame_schedule.append({
            "frame_index": i,
            "t": t,
            "arc_position": {"x": 0, "y": 0},
            "squash_stretch": {"x_scale": 1.0, "y_scale": 1.0},
            "parts_positions": {}
        })

    plan = {
        "num_frames": num_frames,
        "frame_schedule": frame_schedule,
        "timing_curve": "linear",
        "custom_easing": [],
        "arc_type": "none",
        "controlnet_strategy": "none",
        "controlnet_strength": 0.0,
        "deformation_schedule": {},
        "layered_motion": False,
        "motion_layers": [],
        "volume_constraints": {},
        "_phase": 0,
        "_status": "stub"
    }

    state["plan"] = plan

    # Append message to existing messages
    messages = state.get("messages", []).copy()
    messages.append({
        "agent": "planner",
        "timestamp": datetime.now().isoformat(),
        "action": "created_plan",
        "details": f"Phase 0 stub - simple {num_frames}-frame linear plan"
    })
    state["messages"] = messages

    print_plan_summary(plan)
    print_agent_complete("planner", f"{num_frames}-frame plan created")
    return state


@traceable(run_type="agent", name="Generator Agent")
def generator_agent(state: AnimationState) -> AnimationState:
    """
    GENERATOR AGENT - Phase 1 Implementation

    Purpose: Generate intermediate frames based on plan.

    Phase 1: Simple linear interpolation with easing
    Future phases will add:
    - AnimateDiff integration
    - ControlNet guidance
    - Deformation application
    - Layer compositing
    """
    iteration = state.get("iteration_count", 0)
    print_agent_start("generator", iteration)
    print_phase_badge(0)

    plan = state.get("plan", {})
    keyframe1 = state.get("keyframe1", "")
    keyframe2 = state.get("keyframe2", "")
    job_id = state.get("job_id", "test_job")

    try:
        # Import frame generator service
        from ..services.frame_generator_service import get_generator_service

        # Generate frames
        generator = get_generator_service(output_dir="outputs")
        frames = generator.generate_frames(
            keyframe1_path=keyframe1,
            keyframe2_path=keyframe2,
            plan=plan,
            job_id=job_id
        )

        logger.info(f"GENERATOR: Generated {len(frames)} frames successfully")

    except Exception as e:
        # Fallback to placeholder paths if generation fails
        logger.error(f"GENERATOR frame generation failed: {e}")
        logger.warning("GENERATOR falling back to placeholder paths")

        num_frames = plan.get("num_frames", 8)
        frames = [f"outputs/{job_id}/frame_{i:03d}.png" for i in range(num_frames)]

        # Add error to state
        state["error"] = f"Frame generation failed: {str(e)}"

    state["frames"] = frames

    # Append message to existing messages
    messages = state.get("messages", []).copy()
    messages.append({
        "agent": "generator",
        "timestamp": datetime.now().isoformat(),
        "action": "generated_frames",
        "details": f"Phase 1 - Generated {len(frames)} frames via interpolation"
    })
    state["messages"] = messages

    logger.info(f"GENERATOR agent completed - {len(frames)} frames")
    return state


@traceable(run_type="agent", name="Validator Agent")
def validator_agent(state: AnimationState) -> AnimationState:
    """
    VALIDATOR AGENT - Phase 0 Stub

    Purpose: Assess quality and check principle adherence.

    Phase 0: Returns perfect score (always passes).
    Future phases will add:
    - Claude Vision quality assessment
    - Volume consistency checking
    - Motion smoothness analysis
    - Principle adherence validation
    """
    iteration = state.get("iteration_count", 0)
    print_agent_start("validator", iteration)
    print_phase_badge(0)

    frames = state.get("frames", [])
    plan = state.get("plan", {})
    animation_principles = state.get("animation_principles", {})

    logger.info(f"Validating {len(frames)} frames...")

    # Placeholder: Always return high quality score
    validation = {
        "overall_quality_score": 8.0,
        "principle_adherence": {
            "arc": {"score": 8.0, "notes": "Phase 0 stub - not validated"},
            "slow_in_slow_out": {"score": 8.0, "notes": "Phase 0 stub - not validated"},
            "timing": {"score": 8.0, "notes": "Phase 0 stub - not validated"}
        },
        "technical_quality": {
            "volume_consistency": 1.0,
            "line_quality": 1.0,
            "motion_smoothness": 1.0,
            "style_match": 1.0,
            "no_artifacts": 1.0
        },
        "issues": [],
        "needs_refinement": False,
        "fix_suggestions": [],
        "_phase": 0,
        "_status": "stub"
    }

    state["validation"] = validation

    # Append message to existing messages
    messages = state.get("messages", []).copy()
    messages.append({
        "agent": "validator",
        "timestamp": datetime.now().isoformat(),
        "action": "validated_frames",
        "details": f"Phase 0 stub - quality score: {validation['overall_quality_score']}"
    })
    state["messages"] = messages

    print_validation_summary(validation)
    print_agent_complete("validator", "validation complete")
    return state


@traceable(run_type="agent", name="Refiner Agent")
def refiner_agent(state: AnimationState) -> AnimationState:
    """
    REFINER AGENT - Phase 0 Stub

    Purpose: Fix issues identified by validator.

    Phase 0: Not called (validator always passes).
    Future phases will add:
    - Ebsynth style transfer
    - Inpainting for problem regions
    - Temporal smoothing
    - Volume normalization
    """
    iteration = state.get("iteration_count", 0)
    print_agent_start("refiner", iteration)
    print_phase_badge(0)

    frames = state.get("frames", [])
    validation = state.get("validation", {})
    job_id = state.get("job_id", "test_job")

    logger.info(f"Refining {len(frames)} frames...")

    # Placeholder: Copy frames list to refined_frames
    refined_frames = [f.replace("frame_", "refined_frame_") for f in frames]
    issues_fixed = ["Phase 0 stub - no actual refinement performed"]

    state["refined_frames"] = refined_frames

    # Append message to existing messages
    messages = state.get("messages", []).copy()
    messages.append({
        "agent": "refiner",
        "timestamp": datetime.now().isoformat(),
        "action": "refined_frames",
        "details": "Phase 0 stub - frames copied without refinement"
    })
    state["messages"] = messages

    print_refinement_summary(len(refined_frames), issues_fixed)
    print_agent_complete("refiner", f"{len(refined_frames)} frames refined")
    return state
