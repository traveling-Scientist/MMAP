"""Decision accuracy metric for Layer 2."""

from typing import Any

from mmap_eval.core.metric import BaseMetric, MetricResult, Severity


class DecisionAccuracy(BaseMetric):
    """Measures accuracy of agent decisions.

    Evaluates whether the agent makes correct decisions based on the input
    and context (e.g., approve/deny, escalate, take action).
    """

    def __init__(
        self,
        threshold: float = 0.95,
        severity: Severity = Severity.CRITICAL,
    ):
        """Initialize decision accuracy metric.

        Args:
            threshold: Minimum accuracy threshold (0-1)
            severity: Severity level if metric fails
        """
        super().__init__(
            name="Decision Accuracy",
            layer=2,
            threshold=threshold,
            severity=severity,
            description="Measures accuracy of agent decisions",
        )

    def evaluate(self, output: Any, ground_truth: Any, **kwargs: Any) -> MetricResult:
        """Evaluate decision accuracy.

        Args:
            output: Agent output containing "decision" field
            ground_truth: Ground truth containing "decision" field
            **kwargs: Additional arguments

        Returns:
            MetricResult with accuracy score
        """
        try:
            predicted_decision = self._extract_decision(output)
            true_decision = self._extract_decision(ground_truth)

            if predicted_decision is None or true_decision is None:
                score = 0.0
                details = {
                    "error": "Missing decision field",
                    "predicted": predicted_decision,
                    "expected": true_decision,
                }
            else:
                score = 1.0 if predicted_decision == true_decision else 0.0
                details = {
                    "predicted": predicted_decision,
                    "expected": true_decision,
                    "match": predicted_decision == true_decision,
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
                remediation=None if passed else "Review decision-making logic and model training",
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
                remediation=f"Fix error in decision evaluation: {str(e)}",
            )

    def _extract_decision(self, data: Any) -> Any:
        """Extract decision from data."""
        if isinstance(data, dict):
            return data.get("decision")
        elif hasattr(data, "decision"):
            return data.decision
        return None
