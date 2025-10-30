"""
Telekinesis: Animation Principles-Driven Agent Loop

Multi-agent system that applies the 12 Principles of Animation to intelligently
interpolate between keyframe images using LangGraph.
"""

from .state import AnimationState
from .graph import build_telekinesis_graph

__all__ = ["AnimationState", "build_telekinesis_graph"]
