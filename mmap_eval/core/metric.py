"""Base metric classes for MMAP evaluation."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Severity levels for metric failures."""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class MetricResult(BaseModel):
    """Result of a single metric evaluation.

    Attributes:
        metric_name: Name of the metric
        layer: Evaluation layer (1-5)
        score: Numeric score (0-1)
        threshold: Threshold for passing
        passed: Whether the metric passed
        severity: Severity if failed
        details: Additional details about the evaluation
        remediation: Suggested remediation steps
    """

    metric_name: str
    layer: int = Field(ge=1, le=5)
    score: float = Field(ge=0, le=1)
    threshold: float = Field(ge=0, le=1)
    passed: bool
    severity: Severity = Severity.INFO
    details: Dict[str, Any] = Field(default_factory=dict)
    remediation: Optional[str] = None

    def __str__(self) -> str:
        status = "✓ PASS" if self.passed else "✗ FAIL"
        return f"{self.metric_name}: {status} (score: {self.score:.2f}, threshold: {self.threshold:.2f})"


class BaseMetric(ABC):
    """Base class for all metrics.

    All metrics must inherit from this class and implement the evaluate method.
    """

    def __init__(
        self,
        name: str,
        layer: int,
        threshold: float = 0.9,
        severity: Severity = Severity.WARNING,
        description: Optional[str] = None,
    ):
        """Initialize the metric.

        Args:
            name: Name of the metric
            layer: Evaluation layer (1-5)
            threshold: Threshold for passing (0-1)
            severity: Severity level if metric fails
            description: Description of what the metric measures
        """
        if not 1 <= layer <= 5:
            raise ValueError(f"Layer must be between 1 and 5, got {layer}")
        if not 0 <= threshold <= 1:
            raise ValueError(f"Threshold must be between 0 and 1, got {threshold}")

        self.name = name
        self.layer = layer
        self.threshold = threshold
        self.severity = severity
        self.description = description or f"{name} metric"

    @abstractmethod
    def evaluate(self, output: Any, ground_truth: Any, **kwargs: Any) -> MetricResult:
        """Evaluate the metric.

        Args:
            output: Agent output to evaluate
            ground_truth: Ground truth for comparison
            **kwargs: Additional arguments

        Returns:
            MetricResult with score and details
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, layer={self.layer}, threshold={self.threshold})"
