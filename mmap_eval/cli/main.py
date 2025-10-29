"""Main CLI application for MMAP."""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from mmap_eval import __version__
from mmap_eval.reporters.json_reporter import JSONReporter
from mmap_eval.reporters.terminal_reporter import TerminalReporter

app = typer.Typer(
    name="mmap",
    help="MMAP: Multi-Modal Agent Assessment Protocol - Comprehensive evaluation framework for AI agents",
    add_completion=False,
)

console = Console()


@app.command()
def version() -> None:
    """Show MMAP version."""
    console.print(f"MMAP version {__version__}")


@app.command()
def init(
    name: str = typer.Argument(..., help="Name of the evaluation project"),
    output_dir: Path = typer.Option(
        Path.cwd(), "--output", "-o", help="Output directory for project files"
    ),
) -> None:
    """Initialize a new MMAP evaluation project.

    Creates a directory structure and template files for agent evaluation.
    """
    project_dir = output_dir / name
    project_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    (project_dir / "tests").mkdir(exist_ok=True)
    (project_dir / "results").mkdir(exist_ok=True)

    # Create template test cases file
    test_template = [
        {
            "id": "test_001",
            "input": {
                "text": "Sample input text",
                "metadata": {}
            },
            "ground_truth": {
                "intent": "sample_intent",
                "decision": "sample_decision",
                "entities": {}
            },
            "tags": ["sample"]
        }
    ]

    test_file = project_dir / "tests" / "test_cases.json"
    with open(test_file, "w") as f:
        json.dump(test_template, f, indent=2)

    # Create template agent file
    agent_template = '''"""Sample agent implementation."""

def my_agent(input_data):
    """Process input and return output.

    Args:
        input_data: Dictionary containing input data

    Returns:
        Dictionary containing agent output
    """
    # TODO: Implement your agent logic here
    return {
        "intent": "sample_intent",
        "decision": "sample_decision",
        "entities": {},
        "response": "Sample response"
    }
'''

    agent_file = project_dir / "agent.py"
    with open(agent_file, "w") as f:
        f.write(agent_template)

    # Create template evaluation script
    eval_template = '''"""Evaluation script for the agent."""

from mmap import AgentEvaluator
from mmap_eval.metrics import (
    IntentAccuracy,
    EntityExtractionAccuracy,
    DecisionAccuracy,
)
from mmap_eval.reporters import TerminalReporter

from agent import my_agent


def main():
    """Run agent evaluation."""
    # Create evaluator
    evaluator = AgentEvaluator(
        agent=my_agent,
        test_dataset="tests/test_cases.json",
        agent_id="my_agent_v1"
    )

    # Add metrics
    evaluator.add_metric(IntentAccuracy(threshold=0.90))
    evaluator.add_metric(EntityExtractionAccuracy(threshold=0.85))
    evaluator.add_metric(DecisionAccuracy(threshold=0.95))

    # Run evaluation
    result = evaluator.evaluate()

    # Print results
    reporter = TerminalReporter()
    reporter.print_summary(result)

    # Save results
    result.to_json("results/evaluation.json")


if __name__ == "__main__":
    main()
'''

    eval_file = project_dir / "evaluate.py"
    with open(eval_file, "w") as f:
        f.write(eval_template)

    # Create README
    readme_content = f"""# {name} - MMAP Evaluation Project

This project was created with MMAP (Multi-Modal Agent Assessment Protocol).

## Project Structure

- `agent.py` - Your agent implementation
- `evaluate.py` - Evaluation script
- `tests/` - Test cases directory
- `results/` - Evaluation results directory

## Getting Started

1. Implement your agent in `agent.py`
2. Add test cases to `tests/test_cases.json`
3. Configure metrics in `evaluate.py`
4. Run evaluation:
   ```bash
   python evaluate.py
   ```

## Adding More Metrics

Available metrics:
- Layer 1: IntentAccuracy, EntityExtractionAccuracy
- Layer 2: DecisionAccuracy, HallucinationDetection
- Layer 3: APILatency, TransactionSuccess
- Layer 4: PolicyCompliance, EdgeCaseHandling
- Layer 5: DemographicParity, AuditTrail

Example:
```python
from mmap_eval.metrics import HallucinationDetection

evaluator.add_metric(HallucinationDetection(threshold=0.9))
```

## Resources

- MMAP Documentation: https://github.com/traveling-Scientist/MMAP
- Report Issues: https://github.com/traveling-Scientist/MMAP/issues
"""

    readme_file = project_dir / "README.md"
    with open(readme_file, "w") as f:
        f.write(readme_content)

    console.print(f"[green]✓ Created MMAP project: {project_dir}[/green]")
    console.print("\nNext steps:")
    console.print(f"1. cd {project_dir}")
    console.print("2. Edit agent.py to implement your agent")
    console.print("3. Add test cases to tests/test_cases.json")
    console.print("4. Run: python evaluate.py")


@app.command()
def report(
    result_file: Path = typer.Argument(..., help="Path to evaluation result JSON file"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed metrics"),
) -> None:
    """Display evaluation results from a JSON file.

    Args:
        result_file: Path to evaluation result JSON file
        detailed: Whether to show detailed metrics
    """
    try:
        result = JSONReporter.load(result_file)
        reporter = TerminalReporter()

        if detailed:
            reporter.print_detailed(result)
        else:
            reporter.print_summary(result)

    except FileNotFoundError:
        console.print(f"[red]Error: File not found: {result_file}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error loading results: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
