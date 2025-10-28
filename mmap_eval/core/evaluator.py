"""Main agent evaluator orchestrator."""

import time
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from mmap_eval.core.metric import BaseMetric, MetricResult, Severity
from mmap_eval.core.registry import MetricRegistry
from mmap_eval.core.result import EvaluationResult, LayerResult
from mmap_eval.core.test_loader import TestCase, TestLoader


class AgentEvaluator:
    """Main evaluator for assessing AI agents across all 5 layers.

    Example:
        >>> evaluator = AgentEvaluator(
        ...     agent=my_agent_function,
        ...     test_dataset="tests.json"
        ... )
        >>> evaluator.add_metric(IntentAccuracy(threshold=0.90))
        >>> report = evaluator.evaluate()
        >>> report.print_summary()
    """

    # Layer names mapping
    LAYER_NAMES = {
        1: "Input/Output Validation",
        2: "Model Performance",
        3: "System Integration",
        4: "Business Logic",
        5: "Fairness & Compliance",
    }

    def __init__(
        self,
        agent: Callable[[Dict[str, Any]], Any],
        test_dataset: Optional[Union[str, Path, List[Dict[str, Any]]]] = None,
        agent_id: Optional[str] = None,
    ):
        """Initialize the evaluator.

        Args:
            agent: Agent function to evaluate (takes input dict, returns output)
            test_dataset: Test dataset (file path or list of test cases)
            agent_id: Optional identifier for the agent
        """
        self.agent = agent
        self.agent_id = agent_id or f"agent_{uuid.uuid4().hex[:8]}"
        self.registry = MetricRegistry()
        self.test_cases: List[TestCase] = []

        if test_dataset:
            self.load_test_dataset(test_dataset)

    def load_test_dataset(
        self, test_dataset: Union[str, Path, List[Dict[str, Any]]]
    ) -> None:
        """Load test dataset.

        Args:
            test_dataset: File path or list of test case dictionaries
        """
        if isinstance(test_dataset, (str, Path)):
            self.test_cases = TestLoader.load_from_json(test_dataset)
        elif isinstance(test_dataset, list):
            self.test_cases = TestLoader.load_from_list(test_dataset)
        else:
            raise ValueError(f"Invalid test_dataset type: {type(test_dataset)}")

    def add_metric(self, metric: BaseMetric, layer: Optional[int] = None) -> None:
        """Add a metric to the evaluation.

        Args:
            metric: Metric to add
            layer: Optional layer override (uses metric's default if not provided)
        """
        if layer is not None:
            metric.layer = layer
        self.registry.register(metric)

    def add_metrics(self, metrics: List[BaseMetric]) -> None:
        """Add multiple metrics at once.

        Args:
            metrics: List of metrics to add
        """
        for metric in metrics:
            self.add_metric(metric)

    def evaluate(
        self,
        test_cases: Optional[List[TestCase]] = None,
        parallel: bool = False,
    ) -> EvaluationResult:
        """Run the complete evaluation.

        Args:
            test_cases: Optional test cases to use (uses loaded dataset if not provided)
            parallel: Whether to run evaluations in parallel (not implemented yet)

        Returns:
            EvaluationResult with complete evaluation data

        Raises:
            ValueError: If no test cases provided
            ValueError: If no metrics registered
        """
        start_time = time.time()
        evaluation_id = f"eval_{uuid.uuid4().hex}"

        # Use provided test cases or fall back to loaded dataset
        cases_to_evaluate = test_cases or self.test_cases
        if not cases_to_evaluate:
            raise ValueError("No test cases provided for evaluation")

        if self.registry.count() == 0:
            raise ValueError("No metrics registered for evaluation")

        # Evaluate each layer
        layer_results: List[LayerResult] = []
        all_critical_issues: List[str] = []

        for layer_num in range(1, 6):
            layer_result = self._evaluate_layer(layer_num, cases_to_evaluate)
            layer_results.append(layer_result)

            # Collect critical issues
            for metric_result in layer_result.get_critical_failures():
                issue = f"Layer {layer_num} - {metric_result.metric_name}: {metric_result.details.get('error', 'Critical failure')}"
                all_critical_issues.append(issue)

        # Calculate overall score (average of layer scores)
        overall_score = sum(layer.score for layer in layer_results) / len(layer_results)

        # Determine if evaluation passed (all critical metrics passed)
        passed = len(all_critical_issues) == 0

        duration = time.time() - start_time

        return EvaluationResult(
            evaluation_id=evaluation_id,
            agent_id=self.agent_id,
            overall_score=overall_score,
            layers=layer_results,
            critical_issues=all_critical_issues,
            test_cases_count=len(cases_to_evaluate),
            duration_seconds=duration,
            passed=passed,
        )

    def _evaluate_layer(self, layer_num: int, test_cases: List[TestCase]) -> LayerResult:
        """Evaluate a single layer.

        Args:
            layer_num: Layer number to evaluate
            test_cases: Test cases to use

        Returns:
            LayerResult for the layer
        """
        metrics = self.registry.get_metrics_by_layer(layer_num)

        if not metrics:
            # No metrics for this layer, return perfect score
            return LayerResult(
                layer_number=layer_num,
                layer_name=self.LAYER_NAMES[layer_num],
                score=1.0,
                status="pass",
                metrics=[],
            )

        metric_results: List[MetricResult] = []

        # Run each metric on all test cases
        for metric in metrics:
            test_results = []

            for test_case in test_cases:
                try:
                    # Run agent on test case
                    output = self.agent(test_case.input)

                    # Evaluate metric
                    result = metric.evaluate(
                        output=output,
                        ground_truth=test_case.ground_truth,
                        test_case=test_case,
                    )
                    test_results.append(result)
                except Exception as e:
                    # Handle evaluation errors
                    test_results.append(
                        MetricResult(
                            metric_name=metric.name,
                            layer=metric.layer,
                            score=0.0,
                            threshold=metric.threshold,
                            passed=False,
                            severity=Severity.CRITICAL,
                            details={"error": str(e)},
                            remediation=f"Fix error in {metric.name} evaluation: {str(e)}",
                        )
                    )

            # Aggregate results for this metric (average score across test cases)
            avg_score = sum(r.score for r in test_results) / len(test_results)
            passed = avg_score >= metric.threshold

            aggregated_result = MetricResult(
                metric_name=metric.name,
                layer=metric.layer,
                score=avg_score,
                threshold=metric.threshold,
                passed=passed,
                severity=metric.severity,
                details={
                    "correct": sum(1 for r in test_results if r.passed),
                    "total": len(test_results),
                    "individual_scores": [r.score for r in test_results],
                },
                remediation=None if passed else f"{metric.name} below threshold. Review agent implementation.",
            )

            metric_results.append(aggregated_result)

        # Calculate layer score (average of metric scores)
        layer_score = sum(m.score for m in metric_results) / len(metric_results)
        layer_status = "pass" if all(m.passed for m in metric_results) else "fail"

        return LayerResult(
            layer_number=layer_num,
            layer_name=self.LAYER_NAMES[layer_num],
            score=layer_score,
            status=layer_status,
            metrics=metric_results,
        )

    def compare(
        self,
        agents: List[Callable[[Dict[str, Any]], Any]],
        test_dataset: Optional[Union[str, Path, List[Dict[str, Any]]]] = None,
    ) -> List[EvaluationResult]:
        """Compare multiple agents on the same test dataset.

        Args:
            agents: List of agent functions to compare
            test_dataset: Test dataset to use (uses loaded dataset if not provided)

        Returns:
            List of EvaluationResults, one per agent
        """
        results = []
        original_agent = self.agent

        test_cases = None
        if test_dataset:
            if isinstance(test_dataset, (str, Path)):
                test_cases = TestLoader.load_from_json(test_dataset)
            else:
                test_cases = TestLoader.load_from_list(test_dataset)

        for i, agent in enumerate(agents):
            self.agent = agent
            self.agent_id = f"agent_{i+1}"
            result = self.evaluate(test_cases=test_cases)
            results.append(result)

        # Restore original agent
        self.agent = original_agent

        return results

    def __repr__(self) -> str:
        return f"AgentEvaluator(agent_id={self.agent_id}, metrics={self.registry.count()}, tests={len(self.test_cases)})"
