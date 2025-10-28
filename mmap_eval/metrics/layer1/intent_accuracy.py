"""Intent accuracy metric for Layer 1."""

from typing import Any, Dict

from mmap_eval.core.metric import BaseMetric, MetricResult, Severity


class IntentAccuracy(BaseMetric):
    """Measures how accurately the agent identifies user intent.

    This metric evaluates whether the agent correctly classifies the intent
    of user inputs. It compares the predicted intent against the ground truth.

    Example:
        >>> metric = IntentAccuracy(threshold=0.90)
        >>> result = metric.evaluate(
        ...     output={"intent": "refund_request"},
        ...     ground_truth={"intent": "refund_request"}
        ... )
        >>> print(result.score)
        1.0
    """

    def __init__(
        self,
        threshold: float = 0.9,
        severity: Severity = Severity.CRITICAL,
    ):
        """Initialize intent accuracy metric.

        Args:
            threshold: Minimum accuracy threshold (0-1)
            severity: Severity level if metric fails
        """
        super().__init__(
            name="Intent Accuracy",
            layer=1,
            threshold=threshold,
            severity=severity,
            description="Measures accuracy of intent classification",
        )

    def evaluate(self, output: Any, ground_truth: Any, **kwargs: Any) -> MetricResult:
        """Evaluate intent accuracy.

        Args:
            output: Agent output containing "intent" field
            ground_truth: Ground truth containing "intent" field
            **kwargs: Additional arguments

        Returns:
            MetricResult with accuracy score
        """
        try:
            # Extract intents
            predicted_intent = self._extract_intent(output)
            true_intent = self._extract_intent(ground_truth)

            # Compare intents
            if predicted_intent is None or true_intent is None:
                score = 0.0
                details = {
                    "error": "Missing intent field",
                    "predicted": predicted_intent,
                    "expected": true_intent,
                }
            else:
                score = 1.0 if predicted_intent == true_intent else 0.0
                details = {
                    "predicted": predicted_intent,
                    "expected": true_intent,
                    "match": predicted_intent == true_intent,
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
                remediation=None if passed else "Review intent classification logic and training data",
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
                remediation=f"Fix error in intent evaluation: {str(e)}",
            )

    def _extract_intent(self, data: Any) -> Any:
        """Extract intent from data.

        Args:
            data: Data containing intent

        Returns:
            Intent value or None
        """
        if isinstance(data, dict):
            return data.get("intent")
        elif hasattr(data, "intent"):
            return data.intent
        return None
