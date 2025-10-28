"""API latency metric for Layer 3."""

import time
from typing import Any

from mmap_eval.core.metric import BaseMetric, MetricResult, Severity


class APILatency(BaseMetric):
    """Measures API response latency.

    Evaluates whether the agent responds within acceptable time limits.
    """

    def __init__(
        self,
        max_latency_ms: float = 2000.0,
        threshold: float = 0.95,
        severity: Severity = Severity.WARNING,
    ):
        """Initialize API latency metric.

        Args:
            max_latency_ms: Maximum acceptable latency in milliseconds
            threshold: Minimum pass rate (0-1)
            severity: Severity level if metric fails
        """
        self.max_latency_ms = max_latency_ms

        super().__init__(
            name="API Latency",
            layer=3,
            threshold=threshold,
            severity=severity,
            description=f"Measures API response time (max: {max_latency_ms}ms)",
        )

    def evaluate(self, output: Any, ground_truth: Any, **kwargs: Any) -> MetricResult:
        """Evaluate API latency.

        Args:
            output: Agent output (may contain latency_ms)
            ground_truth: Ground truth (not used for latency)
            **kwargs: Additional arguments (may contain start_time)

        Returns:
            MetricResult with latency score
        """
        try:
            # Try to extract latency from output
            latency_ms = self._extract_latency(output, kwargs)

            if latency_ms is None:
                score = 0.0
                details = {"error": "No latency information available"}
            else:
                # Score based on how far below max latency
                score = 1.0 if latency_ms <= self.max_latency_ms else self.max_latency_ms / latency_ms
                score = max(0.0, min(1.0, score))  # Clamp to [0, 1]

                details = {
                    "latency_ms": latency_ms,
                    "max_latency_ms": self.max_latency_ms,
                    "within_limit": latency_ms <= self.max_latency_ms,
                }

            passed = score >= self.threshold

            return MetricResult(
                metric_name=self.name,
                layer=self.layer,
                score=score,
                threshold=self.threshold,
                passed=passed,
                severity=self.severity,
                details=details,
                remediation=None if passed else "Optimize agent processing time and reduce API calls",
            )

        except Exception as e:
            return MetricResult(
                metric_name=self.name,
                layer=self.layer,
                score=0.0,
                threshold=self.threshold,
                passed=False,
                severity=Severity.CRITICAL,
                details={"error": str(e)},
                remediation=f"Fix error in latency measurement: {str(e)}",
            )

    def _extract_latency(self, output: Any, kwargs: dict) -> float:
        """Extract latency from output or kwargs."""
        # Check if output contains latency
        if isinstance(output, dict) and "latency_ms" in output:
            return output["latency_ms"]
        elif hasattr(output, "latency_ms"):
            return output.latency_ms

        # Check if kwargs contains timing information
        if "start_time" in kwargs and "end_time" in kwargs:
            return (kwargs["end_time"] - kwargs["start_time"]) * 1000

        # Try to measure from timing metadata
        if "execution_time_ms" in kwargs:
            return kwargs["execution_time_ms"]

        return None
