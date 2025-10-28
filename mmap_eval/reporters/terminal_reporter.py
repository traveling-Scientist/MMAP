"""Terminal reporter for evaluation results."""

from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from mmap_eval.core.result import EvaluationResult


class TerminalReporter:
    """Formats and prints evaluation results to terminal with colors."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize terminal reporter.

        Args:
            console: Rich console instance (creates new if not provided)
        """
        self.console = console or Console()

    def print_summary(self, result: EvaluationResult) -> None:
        """Print a formatted summary of evaluation results.

        Args:
            result: Evaluation result to print
        """
        # Header
        title = "MMAP Evaluation Report"
        if result.agent_id:
            title += f" - {result.agent_id}"

        self.console.print()
        self.console.print(Panel(title, style="bold blue"))
        self.console.print()

        # Overall Status
        status_color = "green" if result.passed else "red"
        status_text = "✓ PASS" if result.passed else "✗ FAIL"
        self.console.print(f"[{status_color}]Status: {status_text}[/{status_color}]")
        self.console.print(f"Overall Score: [bold]{result.overall_score:.2%}[/bold]")
        self.console.print(f"Test Cases: {result.test_cases_count}")
        self.console.print(f"Duration: {result.duration_seconds:.2f}s")
        self.console.print(f"Evaluation ID: {result.evaluation_id}")
        self.console.print()

        # Layer Results Table
        table = Table(title="Layer Results", show_header=True, header_style="bold magenta")
        table.add_column("Layer", style="cyan", width=6)
        table.add_column("Name", style="white", width=30)
        table.add_column("Score", justify="right", width=10)
        table.add_column("Status", justify="center", width=10)
        table.add_column("Metrics", justify="right", width=10)

        for layer in result.layers:
            status_icon = "✓" if layer.passed else "✗"
            status_color = "green" if layer.passed else "red"
            status_text = f"[{status_color}]{status_icon}[/{status_color}]"

            table.add_row(
                str(layer.layer_number),
                layer.layer_name,
                f"{layer.score:.2%}",
                status_text,
                f"{len(layer.metrics)} metrics",
            )

        self.console.print(table)
        self.console.print()

        # Failed Metrics Details
        failed_layers = result.get_failed_layers()
        if failed_layers:
            self.console.print("[bold red]Failed Metrics:[/bold red]")
            self.console.print()

            for layer in failed_layers:
                failed_metrics = layer.get_failed_metrics()
                if failed_metrics:
                    self.console.print(f"  [yellow]Layer {layer.layer_number}: {layer.layer_name}[/yellow]")

                    for metric in failed_metrics:
                        severity_color = {
                            "critical": "red",
                            "warning": "yellow",
                            "info": "blue",
                        }.get(metric.severity, "white")

                        self.console.print(
                            f"    [{severity_color}]✗ {metric.metric_name}[/{severity_color}]: "
                            f"Score {metric.score:.2%} (threshold: {metric.threshold:.2%})"
                        )

                        if metric.remediation:
                            self.console.print(f"      Remediation: {metric.remediation}")

                    self.console.print()

        # Critical Issues
        if result.critical_issues:
            self.console.print("[bold red]Critical Issues:[/bold red]")
            for issue in result.critical_issues:
                self.console.print(f"  [red]• {issue}[/red]")
            self.console.print()

    def print_detailed(self, result: EvaluationResult) -> None:
        """Print detailed evaluation results including all metrics.

        Args:
            result: Evaluation result to print
        """
        self.print_summary(result)

        self.console.print("[bold]Detailed Metrics:[/bold]")
        self.console.print()

        for layer in result.layers:
            self.console.print(f"[bold cyan]Layer {layer.layer_number}: {layer.layer_name}[/bold cyan]")
            self.console.print(f"Layer Score: {layer.score:.2%}")
            self.console.print()

            if layer.metrics:
                metrics_table = Table(show_header=True, header_style="bold")
                metrics_table.add_column("Metric", style="white", width=30)
                metrics_table.add_column("Score", justify="right", width=10)
                metrics_table.add_column("Threshold", justify="right", width=10)
                metrics_table.add_column("Status", justify="center", width=10)
                metrics_table.add_column("Severity", justify="center", width=10)

                for metric in layer.metrics:
                    status_icon = "✓" if metric.passed else "✗"
                    status_color = "green" if metric.passed else "red"
                    status_text = f"[{status_color}]{status_icon}[/{status_color}]"

                    severity_color = {
                        "critical": "red",
                        "warning": "yellow",
                        "info": "blue",
                    }.get(metric.severity, "white")

                    metrics_table.add_row(
                        metric.metric_name,
                        f"{metric.score:.2%}",
                        f"{metric.threshold:.2%}",
                        status_text,
                        f"[{severity_color}]{metric.severity}[/{severity_color}]",
                    )

                self.console.print(metrics_table)
            else:
                self.console.print("  [dim]No metrics evaluated for this layer[/dim]")

            self.console.print()
