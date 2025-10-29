"""JSON reporter for evaluation results."""

import json
from pathlib import Path
from typing import Union

from mmap_eval.core.result import EvaluationResult


class JSONReporter:
    """Exports evaluation results to JSON format."""

    @staticmethod
    def save(result: EvaluationResult, file_path: Union[str, Path]) -> None:
        """Save evaluation results to JSON file.

        Args:
            result: Evaluation result to save
            file_path: Path to save JSON file
        """
        result.to_json(file_path)

    @staticmethod
    def to_string(result: EvaluationResult, pretty: bool = True) -> str:
        """Convert evaluation result to JSON string.

        Args:
            result: Evaluation result to convert
            pretty: Whether to pretty-print the JSON

        Returns:
            JSON string
        """
        if pretty:
            return result.model_dump_json(indent=2)
        return result.model_dump_json()

    @staticmethod
    def load(file_path: Union[str, Path]) -> EvaluationResult:
        """Load evaluation results from JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            EvaluationResult object
        """
        return EvaluationResult.from_json(file_path)
