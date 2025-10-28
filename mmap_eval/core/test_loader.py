"""Test case loading and management."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class TestCase(BaseModel):
    """A single test case for agent evaluation.

    Attributes:
        id: Unique identifier for the test case
        input: Input data for the agent
        ground_truth: Expected outputs and behaviors
        tags: Optional tags for categorization
        metadata: Additional metadata
    """

    id: str
    input: Dict[str, Any]
    ground_truth: Dict[str, Any]
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestCase":
        """Create a TestCase from a dictionary."""
        return cls(**data)


class TestLoader:
    """Loads test cases from various sources."""

    @staticmethod
    def load_from_json(file_path: Union[str, Path]) -> List[TestCase]:
        """Load test cases from a JSON file.

        Args:
            file_path: Path to JSON file containing test cases

        Returns:
            List of TestCase objects

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Test file not found: {file_path}")

        with open(path, "r") as f:
            data = json.load(f)

        # Handle both single test case and list of test cases
        if isinstance(data, dict):
            return [TestCase.from_dict(data)]
        elif isinstance(data, list):
            return [TestCase.from_dict(item) for item in data]
        else:
            raise ValueError(f"Invalid test data format: expected dict or list, got {type(data)}")

    @staticmethod
    def load_from_list(test_cases: List[Dict[str, Any]]) -> List[TestCase]:
        """Load test cases from a list of dictionaries.

        Args:
            test_cases: List of test case dictionaries

        Returns:
            List of TestCase objects
        """
        return [TestCase.from_dict(tc) for tc in test_cases]

    @staticmethod
    def save_to_json(test_cases: List[TestCase], file_path: Union[str, Path]) -> None:
        """Save test cases to a JSON file.

        Args:
            test_cases: List of TestCase objects
            file_path: Path to save JSON file
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            json.dump(
                [tc.model_dump() for tc in test_cases],
                f,
                indent=2
            )
