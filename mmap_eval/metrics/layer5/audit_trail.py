"""Audit trail metric for Layer 5."""

from typing import Any, List

from mmap_eval.core.metric import BaseMetric, MetricResult, Severity


class AuditTrail(BaseMetric):
    """Measures presence and quality of audit trails.

    Evaluates whether agent maintains proper audit trails for compliance
    and debugging purposes.
    """

    def __init__(
        self,
        required_fields: List[str] = None,
        threshold: float = 1.0,
        severity: Severity = Severity.CRITICAL,
    ):
        """Initialize audit trail metric.

        Args:
            required_fields: List of required audit trail fields
            threshold: Minimum completeness score (0-1)
            severity: Severity level if metric fails
        """
        self.required_fields = required_fields or [
            "timestamp",
            "action",
            "decision",
            "reason",
        ]

        super().__init__(
            name="Audit Trail",
            layer=5,
            threshold=threshold,
            severity=severity,
            description="Measures completeness of audit trails",
        )

    def evaluate(self, output: Any, ground_truth: Any, **kwargs: Any) -> MetricResult:
        """Evaluate audit trail completeness.

        Args:
            output: Agent output
            ground_truth: Ground truth (not directly used)
            **kwargs: Additional arguments

        Returns:
            MetricResult with audit trail score
        """
        try:
            # Check for audit trail in output
            audit_trail = self._extract_audit_trail(output)

            if audit_trail is None:
                score = 0.0
                details = {
                    "error": "No audit trail found",
                    "required_fields": self.required_fields,
                    "present_fields": [],
                }
            else:
                # Check for required fields
                present_fields = self._check_required_fields(audit_trail)
                score = len(present_fields) / len(self.required_fields)

                details = {
                    "required_fields": self.required_fields,
                    "present_fields": present_fields,
                    "missing_fields": [
                        f for f in self.required_fields if f not in present_fields
                    ],
                    "completeness": score,
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
                remediation=None if passed else f"Add missing audit fields: {details.get('missing_fields', [])}",
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
                remediation=f"Fix error in audit trail check: {str(e)}",
            )

    def _extract_audit_trail(self, output: Any) -> Any:
        """Extract audit trail from output."""
        if isinstance(output, dict):
            # Check for explicit audit trail
            if "audit_trail" in output:
                return output["audit_trail"]
            elif "audit" in output:
                return output["audit"]
            # Otherwise, use the output itself as audit trail
            return output
        elif hasattr(output, "audit_trail"):
            return output.audit_trail

        return output

    def _check_required_fields(self, audit_trail: Any) -> List[str]:
        """Check which required fields are present.

        Args:
            audit_trail: Audit trail data

        Returns:
            List of present required fields
        """
        present_fields = []

        for field in self.required_fields:
            if self._has_field(audit_trail, field):
                present_fields.append(field)

        return present_fields

    def _has_field(self, data: Any, field: str) -> bool:
        """Check if field exists in data."""
        if isinstance(data, dict):
            return field in data and data[field] is not None
        elif hasattr(data, field):
            return getattr(data, field) is not None

        return False
