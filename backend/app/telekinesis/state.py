"""
AnimationState definition for Telekinesis agent loop.

This state is passed between agents and accumulates information
about the animation generation process.
"""

from typing import TypedDict, List, Dict, Any, Annotated
import operator


class AnimationState(TypedDict):
    """
    State container for the Telekinesis multi-agent animation system.

    This state is passed through the agent graph, with each agent reading
    from and writing to specific fields.
    """

    # ========== Input Fields ==========
    # Provided by user at the start

    keyframe1: str
    """Path to the first keyframe image"""

    keyframe2: str
    """Path to the second keyframe image"""

    instruction: str
    """Natural language instruction describing desired motion"""

    # ========== Agent Output Fields ==========
    # Populated by agents during execution

    analysis: Dict[str, Any]
    """
    Output from ANALYZER agent.
    Contains visual analysis, motion detection, object segmentation, etc.

    Example structure:
    {
        "motion_type": "rotation",
        "primary_subject": "character head",
        "parts_moved": ["head", "neck"],
        "motion_magnitude": {"rotation": 45, "translation": 20},
        "style": "line_art",
        "pose_data": {...},
        "volume_analysis": {...}
    }
    """

    animation_principles: Dict[str, Any]
    """
    Output from PRINCIPLES agent.
    Lists which of the 12 animation principles apply and their parameters.

    Example structure:
    {
        "applicable_principles": [
            {
                "principle": "arc",
                "confidence": 0.95,
                "reason": "Rotation detected",
                "parameters": {"arc_type": "circular", "arc_angle": 45}
            },
            ...
        ],
        "dominant_principle": "arc",
        "complexity_score": 0.7
    }
    """

    plan: Dict[str, Any]
    """
    Output from PLANNER agent.
    Detailed frame-by-frame generation plan.

    Example structure:
    {
        "num_frames": 8,
        "frame_schedule": [
            {
                "frame_index": 0,
                "t": 0.0,
                "arc_position": {"x": 100, "y": 200},
                "squash_stretch": {"x_scale": 1.0, "y_scale": 1.0}
            },
            ...
        ],
        "timing_curve": "ease-in-out",
        "controlnet_strategy": "pose",
        "volume_constraints": {...}
    }
    """

    frames: List[str]
    """
    Output from GENERATOR agent.
    List of paths to generated frame images.

    Example: ["/outputs/job123/frame_001.png", ...]
    """

    validation: Dict[str, Any]
    """
    Output from VALIDATOR agent.
    Quality assessment and issue detection.

    Example structure:
    {
        "overall_quality_score": 7.5,
        "principle_adherence": {
            "arc": {"score": 8.5, "notes": "Motion follows arc well"},
            ...
        },
        "technical_quality": {
            "volume_consistency": 0.92,
            "motion_smoothness": 0.95
        },
        "issues": [
            {
                "severity": "medium",
                "type": "volume_inconsistency",
                "frames": [3, 4],
                "description": "Object grows 15% in mid-motion"
            }
        ],
        "needs_refinement": False
    }
    """

    refined_frames: List[str]
    """
    Output from REFINER agent (if refinement occurs).
    List of paths to refined frame images.

    Example: ["/outputs/job123/refined_frame_001.png", ...]
    """

    # ========== Control Flow Fields ==========

    iteration_count: int
    """
    Number of refinement iterations performed.
    Used to prevent infinite loops (max 3 iterations).
    """

    messages: Annotated[List[Dict[str, Any]], operator.add]
    """
    Log of agent actions and decisions.
    Uses operator.add so each agent can append messages.

    Example entry:
    {
        "agent": "analyzer",
        "timestamp": "2025-10-29T12:34:56",
        "action": "completed_analysis",
        "details": {...}
    }
    """

    # ========== Optional Fields ==========

    job_id: str
    """Optional: Job ID for tracking and file organization"""

    error: str
    """Optional: Error message if something goes wrong"""
