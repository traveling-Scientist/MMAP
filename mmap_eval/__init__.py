"""MMAP: Multi-Modal Agent Assessment Protocol.

A comprehensive evaluation framework for autonomous AI agents.
"""

__version__ = "0.1.0"

from mmap_eval.core.evaluator import AgentEvaluator
from mmap_eval.core.metric import BaseMetric, MetricResult
from mmap_eval.core.result import EvaluationResult, LayerResult

__all__ = [
    "AgentEvaluator",
    "BaseMetric",
    "MetricResult",
    "EvaluationResult",
    "LayerResult",
]
