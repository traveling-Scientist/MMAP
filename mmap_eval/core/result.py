"""Result aggregation and reporting."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from mmap_eval.core.metric import MetricResult, Severity


class LayerResult(BaseModel):
    """Results for a single evaluation layer.

    Attributes:
        layer_number: Layer number (1-5)
        layer_name: Name of the layer
        score: Overall score for the layer (0-1)
        status: Pass/fail status
        metrics: Individual metric results
        critical_issues: List of critical issues found
    """

    layer_number: int = Field(ge=1, le=5)
    layer_name: str
    score: float = Field(ge=0, le=1)
    status: str
    metrics: List[MetricResult]
    critical_issues: List[str] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Check if layer passed (all metrics passed)."""
        return all(m.passed for m in self.metrics)

    def get_failed_metrics(self) -> List[MetricResult]:
        """Get list of failed metrics."""
        return [m for m in self.metrics if not m.passed]

    def get_critical_failures(self) -> List[MetricResult]:
        """Get list of critical failures."""
        return [m for m in self.metrics if not m.passed and m.severity == Severity.CRITICAL]


class EvaluationResult(BaseModel):
    """Complete evaluation results.

    Attributes:
        evaluation_id: Unique evaluation identifier
        timestamp: When evaluation was run
        agent_id: Identifier for the agent being evaluated
        overall_score: Overall score across all layers (0-1)
        layers: Results for each layer
        critical_issues: All critical issues across layers
        test_cases_count: Number of test cases evaluated
        duration_seconds: Time taken for evaluation
        passed: Whether evaluation passed overall
    """

    evaluation_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    agent_id: Optional[str] = None
    overall_score: float = Field(ge=0, le=1)
    layers: List[LayerResult]
    critical_issues: List[str] = Field(default_factory=list)
    test_cases_count: int = 0
    duration_seconds: float = 0.0
    passed: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_json(self, file_path: Optional[Union[str, Path]] = None) -> str:
        """Export results to JSON.

        Args:
            file_path: Optional path to save JSON file

        Returns:
            JSON string
        """
        json_str = self.model_dump_json(indent=2)

        if file_path:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                f.write(json_str)

        return json_str

    @classmethod
    def from_json(cls, json_str: Union[str, Path]) -> "EvaluationResult":
        """Load results from JSON.

        Args:
            json_str: JSON string or path to JSON file

        Returns:
            EvaluationResult object
        """
        if Path(json_str).exists():
            with open(json_str, "r") as f:
                json_str = f.read()

        return cls.model_validate_json(json_str)

    def get_layer_by_number(self, layer_number: int) -> Optional[LayerResult]:
        """Get layer result by layer number."""
        for layer in self.layers:
            if layer.layer_number == layer_number:
                return layer
        return None

    def get_failed_layers(self) -> List[LayerResult]:
        """Get list of failed layers."""
        return [layer for layer in self.layers if not layer.passed]

    def summary(self) -> str:
        """Get a text summary of the evaluation."""
        status = "PASS" if self.passed else "FAIL"
        lines = [
            f"Evaluation {self.evaluation_id}",
            f"Status: {status}",
            f"Overall Score: {self.overall_score:.2f}",
            f"Test Cases: {self.test_cases_count}",
            f"Duration: {self.duration_seconds:.2f}s",
            "",
            "Layer Results:",
        ]

        for layer in self.layers:
            status_icon = "✓" if layer.passed else "✗"
            lines.append(
                f"  {status_icon} Layer {layer.layer_number} ({layer.layer_name}): "
                f"{layer.score:.2f}"
            )

        if self.critical_issues:
            lines.append("")
            lines.append("Critical Issues:")
            for issue in self.critical_issues:
                lines.append(f"  - {issue}")

        return "\n".join(lines)
