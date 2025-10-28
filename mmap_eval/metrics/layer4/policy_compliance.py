"""Policy compliance metric for Layer 4."""

from typing import Any, Dict, List

from mmap_eval.core.metric import BaseMetric, MetricResult, Severity


class PolicyCompliance(BaseMetric):
    """Measures compliance with business policies and rules.

    Evaluates whether agent decisions follow defined business policies
    (e.g., refund limits, approval rules, escalation criteria).
    """

    def __init__(
        self,
        policies: Dict[str, Any] = None,
        threshold: float = 1.0,
        severity: Severity = Severity.CRITICAL,
    ):
        """Initialize policy compliance metric.

        Args:
            policies: Dictionary of policy rules to check
            threshold: Minimum compliance rate (0-1)
            severity: Severity level if metric fails
        """
        self.policies = policies or {}

        super().__init__(
            name="Policy Compliance",
            layer=4,
            threshold=threshold,
            severity=severity,
            description="Measures compliance with business policies",
        )

    def evaluate(self, output: Any, ground_truth: Any, **kwargs: Any) -> MetricResult:
        """Evaluate policy compliance.

        Args:
            output: Agent output
            ground_truth: Ground truth containing expected policy compliance
            **kwargs: Additional arguments

        Returns:
            MetricResult with compliance score
        """
        try:
            # Extract policy compliance indicators
            policy_violations = self._check_policy_violations(output, ground_truth)

            if policy_violations:
                score = 0.0
                details = {
                    "violations": policy_violations,
                    "total_policies_checked": len(policy_violations),
                    "compliant": False,
                }
            else:
                score = 1.0
                details = {
                    "violations": [],
                    "compliant": True,
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
                remediation=None if passed else f"Fix policy violations: {', '.join(policy_violations)}",
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
                remediation=f"Fix error in policy compliance check: {str(e)}",
            )

    def _check_policy_violations(self, output: Any, ground_truth: Any) -> List[str]:
        """Check for policy violations.

        Args:
            output: Agent output
            ground_truth: Ground truth

        Returns:
            List of policy violations
        """
        violations = []

        # Extract policy compliance from ground truth
        if isinstance(ground_truth, dict):
            expected_policy_compliant = ground_truth.get("policy_compliant", True)

            if not expected_policy_compliant:
                # Check if output indicates policy violation
                if not self._has_policy_violation_indicator(output):
                    violations.append("Failed to detect policy violation")

            # Check specific policy rules
            policy_rules = ground_truth.get("policy_rules", {})
            for rule_name, expected_value in policy_rules.items():
                actual_value = self._extract_field(output, rule_name)
                if actual_value != expected_value:
                    violations.append(
                        f"{rule_name}: expected {expected_value}, got {actual_value}"
                    )

        return violations

    def _has_policy_violation_indicator(self, output: Any) -> bool:
        """Check if output indicates policy violation."""
        if isinstance(output, dict):
            return output.get("policy_violation", False) or output.get("error") == "policy_violation"
        return False

    def _extract_field(self, data: Any, field: str) -> Any:
        """Extract a field from data."""
        if isinstance(data, dict):
            return data.get(field)
        elif hasattr(data, field):
            return getattr(data, field)
        return None
