"""Transaction success metric for Layer 3."""

from typing import Any

from mmap_eval.core.metric import BaseMetric, MetricResult, Severity


class TransactionSuccess(BaseMetric):
    """Measures transaction/API call success rate.

    Evaluates whether agent API calls and transactions complete successfully
    without errors.
    """

    def __init__(
        self,
        threshold: float = 0.99,
        severity: Severity = Severity.CRITICAL,
    ):
        """Initialize transaction success metric.

        Args:
            threshold: Minimum success rate (0-1)
            severity: Severity level if metric fails
        """
        super().__init__(
            name="Transaction Success",
            layer=3,
            threshold=threshold,
            severity=severity,
            description="Measures API/transaction success rate",
        )

    def evaluate(self, output: Any, ground_truth: Any, **kwargs: Any) -> MetricResult:
        """Evaluate transaction success.

        Args:
            output: Agent output
            ground_truth: Ground truth (not directly used)
            **kwargs: Additional arguments

        Returns:
            MetricResult with success score
        """
        try:
            # Check for success indicators
            success = self._check_success(output)
            error = self._extract_error(output)

            score = 1.0 if success and error is None else 0.0

            details = {
                "success": success,
                "error": error,
                "status": "completed" if success else "failed",
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
                remediation=None if passed else f"Fix transaction failures: {error}",
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
                remediation=f"Fix error in transaction evaluation: {str(e)}",
            )

    def _check_success(self, output: Any) -> bool:
        """Check if transaction was successful."""
        if isinstance(output, dict):
            # Check for explicit success field
            if "success" in output:
                return bool(output["success"])
            # Check for status field
            if "status" in output:
                return output["status"] in ["success", "completed", "ok"]
            # Check for error field
            if "error" in output:
                return output["error"] is None
            # If none of above, assume success
            return True
        elif hasattr(output, "success"):
            return output.success
        # Default to True if no error indicators
        return True

    def _extract_error(self, output: Any) -> str:
        """Extract error message if present."""
        if isinstance(output, dict):
            return output.get("error")
        elif hasattr(output, "error"):
            return output.error
        return None
