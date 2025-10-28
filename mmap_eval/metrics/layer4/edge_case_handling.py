"""Edge case handling metric for Layer 4."""

from typing import Any

from mmap_eval.core.metric import BaseMetric, MetricResult, Severity


class EdgeCaseHandling(BaseMetric):
    """Measures handling of edge cases and boundary conditions.

    Evaluates whether agent correctly handles edge cases, unusual inputs,
    and boundary conditions.
    """

    def __init__(
        self,
        threshold: float = 0.9,
        severity: Severity = Severity.WARNING,
    ):
        """Initialize edge case handling metric.

        Args:
            threshold: Minimum handling rate (0-1)
            severity: Severity level if metric fails
        """
        super().__init__(
            name="Edge Case Handling",
            layer=4,
            threshold=threshold,
            severity=severity,
            description="Measures handling of edge cases and boundary conditions",
        )

    def evaluate(self, output: Any, ground_truth: Any, **kwargs: Any) -> MetricResult:
        """Evaluate edge case handling.

        Args:
            output: Agent output
            ground_truth: Ground truth
            **kwargs: Additional arguments (may contain test_case with tags)

        Returns:
            MetricResult with edge case handling score
        """
        try:
            # Check if this is an edge case
            test_case = kwargs.get("test_case")
            is_edge_case = self._is_edge_case(test_case)

            if not is_edge_case:
                # Not an edge case, return perfect score
                score = 1.0
                details = {
                    "is_edge_case": False,
                    "handled": True,
                }
            else:
                # Verify edge case was handled correctly
                handled_correctly = self._check_edge_case_handling(output, ground_truth)
                score = 1.0 if handled_correctly else 0.0

                details = {
                    "is_edge_case": True,
                    "handled": handled_correctly,
                    "edge_case_type": self._get_edge_case_type(test_case),
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
                remediation=None if passed else "Improve edge case detection and handling logic",
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
                remediation=f"Fix error in edge case evaluation: {str(e)}",
            )

    def _is_edge_case(self, test_case: Any) -> bool:
        """Check if test case is tagged as edge case."""
        if test_case is None:
            return False

        if hasattr(test_case, "tags"):
            return "edge_case" in test_case.tags

        return False

    def _get_edge_case_type(self, test_case: Any) -> str:
        """Get edge case type from tags."""
        if test_case and hasattr(test_case, "tags"):
            for tag in test_case.tags:
                if tag.startswith("edge_"):
                    return tag
        return "unknown"

    def _check_edge_case_handling(self, output: Any, ground_truth: Any) -> bool:
        """Check if edge case was handled correctly."""
        # Extract expected and actual handling
        if isinstance(ground_truth, dict):
            expected_decision = ground_truth.get("decision")
            expected_handling = ground_truth.get("edge_case_handling")

            if isinstance(output, dict):
                actual_decision = output.get("decision")

                # Check if decision matches or if proper error handling occurred
                if expected_decision:
                    return actual_decision == expected_decision

                # Check for proper error handling
                if expected_handling == "graceful_degradation":
                    return output.get("error") is None and output.get("fallback") is not None

                if expected_handling == "escalation":
                    return output.get("escalated", False) is True

        # Default: assume handled if no error
        return self._extract_error(output) is None

    def _extract_error(self, output: Any) -> Any:
        """Extract error from output."""
        if isinstance(output, dict):
            return output.get("error")
        elif hasattr(output, "error"):
            return output.error
        return None
