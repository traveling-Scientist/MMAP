"""Hallucination detection metric for Layer 2."""

from typing import Any, Set

from mmap_eval.core.metric import BaseMetric, MetricResult, Severity


class HallucinationDetection(BaseMetric):
    """Detects hallucinations in agent responses.

    Identifies when the agent generates information not supported by the input
    or makes claims not grounded in facts.
    """

    def __init__(
        self,
        threshold: float = 0.9,
        severity: Severity = Severity.CRITICAL,
    ):
        """Initialize hallucination detection metric.

        Args:
            threshold: Minimum threshold for non-hallucination (0-1)
            severity: Severity level if metric fails
        """
        super().__init__(
            name="Hallucination Detection",
            layer=2,
            threshold=threshold,
            severity=severity,
            description="Detects hallucinated or unsupported information",
        )

    def evaluate(self, output: Any, ground_truth: Any, **kwargs: Any) -> MetricResult:
        """Evaluate for hallucinations.

        Args:
            output: Agent output
            ground_truth: Ground truth containing "hallucination_expected" field
            **kwargs: Additional arguments

        Returns:
            MetricResult with hallucination score (1.0 = no hallucination)
        """
        try:
            # Check if ground truth indicates hallucination should not occur
            hallucination_expected = self._extract_hallucination_flag(ground_truth)
            response_text = self._extract_response(output)

            if response_text is None:
                score = 0.0
                details = {"error": "No response text found"}
            else:
                # Simple heuristic: check for common hallucination indicators
                has_hallucination = self._detect_hallucination(response_text, ground_truth)

                if hallucination_expected:
                    # Hallucination was expected, check if detected
                    score = 1.0 if has_hallucination else 0.0
                else:
                    # No hallucination expected
                    score = 0.0 if has_hallucination else 1.0

                details = {
                    "hallucination_detected": has_hallucination,
                    "hallucination_expected": hallucination_expected,
                    "response_length": len(response_text),
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
                remediation=None if passed else "Improve grounding and fact-checking in responses",
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
                remediation=f"Fix error in hallucination detection: {str(e)}",
            )

    def _extract_hallucination_flag(self, ground_truth: Any) -> bool:
        """Extract whether hallucination is expected."""
        if isinstance(ground_truth, dict):
            return ground_truth.get("hallucination_expected", False)
        return False

    def _extract_response(self, output: Any) -> str:
        """Extract response text from output."""
        if isinstance(output, str):
            return output
        elif isinstance(output, dict):
            return output.get("response", output.get("text", ""))
        elif hasattr(output, "response"):
            return output.response
        return ""

    def _detect_hallucination(self, response: str, ground_truth: Any) -> bool:
        """Detect potential hallucinations.

        This is a simple heuristic-based approach. In production, you'd want
        to use more sophisticated methods (LLM-as-judge, fact verification, etc.)
        """
        # Check for common hallucination indicators
        hallucination_keywords = [
            "i don't have access",
            "i cannot verify",
            "according to my knowledge",
            "as far as i know",
            "i believe",
            "probably",
            "might be",
        ]

        response_lower = response.lower()

        # Check if response contains hallucination indicators
        for keyword in hallucination_keywords:
            if keyword in response_lower:
                return True

        return False
