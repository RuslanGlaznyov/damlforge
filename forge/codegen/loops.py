"""Compatibility exports for loop IR normalization.

Loop analysis and normalization belong to the IR layer. This module remains
as a compatibility import for callers that used the old codegen location.
"""

from forge.ir.normalize import LoopAnalysis, LoopAnalyzer, LoopNamer, LoopPlan

__all__ = ["LoopAnalysis", "LoopAnalyzer", "LoopNamer", "LoopPlan"]
