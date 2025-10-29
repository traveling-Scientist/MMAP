"""Entity extraction accuracy metric for Layer 1."""

from typing import Any, Dict, Set

from mmap_eval.core.metric import BaseMetric, MetricResult, Severity


class EntityExtractionAccuracy(BaseMetric):
    """Measures accuracy of entity extraction from user inputs.

    This metric evaluates whether the agent correctly extracts named entities
    (e.g., dates, amounts, product names) from user inputs.

    Example:
        >>> metric = EntityExtractionAccuracy(threshold=0.85)
        >>> result = metric.evaluate(
        ...     output={"entities": {"amount": 50, "product": "laptop"}},
        ...     ground_truth={"entities": {"amount": 50, "product": "laptop"}}
        ... )
    """

    def __init__(
        self,
        threshold: float = 0.85,
        severity: Severity = Severity.WARNING,
    ):
        """Initialize entity extraction accuracy metric.

        Args:
            threshold: Minimum accuracy threshold (0-1)
            severity: Severity level if metric fails
        """
        super().__init__(
            name="Entity Extraction Accuracy",
            layer=1,
            threshold=threshold,
            severity=severity,
            description="Measures accuracy of entity extraction",
        )

    def evaluate(self, output: Any, ground_truth: Any, **kwargs: Any) -> MetricResult:
        """Evaluate entity extraction accuracy.

        Args:
            output: Agent output containing "entities" field
            ground_truth: Ground truth containing "entities" field
            **kwargs: Additional arguments

        Returns:
            MetricResult with F1 score
        """
        try:
            # Extract entities
            predicted_entities = self._extract_entities(output)
            true_entities = self._extract_entities(ground_truth)

            if predicted_entities is None or true_entities is None:
                score = 0.0
                details = {"error": "Missing entities field"}
            else:
                # Calculate F1 score
                score, precision, recall = self._calculate_f1(
                    predicted_entities, true_entities
                )
                details = {
                    "predicted": predicted_entities,
                    "expected": true_entities,
                    "precision": precision,
                    "recall": recall,
                    "f1_score": score,
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
                remediation=None if passed else "Review entity extraction logic and improve NER model",
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
                remediation=f"Fix error in entity extraction evaluation: {str(e)}",
            )

    def _extract_entities(self, data: Any) -> Any:
        """Extract entities from data."""
        if isinstance(data, dict):
            return data.get("entities", {})
        elif hasattr(data, "entities"):
            return data.entities
        return None

    def _calculate_f1(
        self, predicted: Dict[str, Any], true: Dict[str, Any]
    ) -> tuple[float, float, float]:
        """Calculate F1 score for entity extraction.

        Args:
            predicted: Predicted entities
            true: True entities

        Returns:
            Tuple of (f1_score, precision, recall)
        """
        if not true:
            return 1.0 if not predicted else 0.0, 1.0, 1.0

        # Convert to sets of (key, value) pairs for comparison
        pred_items = set(predicted.items())
        true_items = set(true.items())

        # Calculate precision and recall
        true_positives = len(pred_items & true_items)
        false_positives = len(pred_items - true_items)
        false_negatives = len(true_items - pred_items)

        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0

        # Calculate F1
        if precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2 * (precision * recall) / (precision + recall)

        return f1, precision, recall
