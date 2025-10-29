"""
Evaluation Script for Content Moderation Agent using MMAP

This script demonstrates how to evaluate a content moderation agent
using the MMAP framework with synthetic test data.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mmap_eval.core.evaluator import AgentEvaluator
from mmap_eval.metrics.layer1 import IntentAccuracy
from mmap_eval.metrics.layer2 import DecisionAccuracy
from mmap_eval.metrics.layer3 import APILatency, TransactionSuccess
from mmap_eval.metrics.layer4 import PolicyCompliance
from mmap_eval.reporters import TerminalReporter, JSONReporter

from agent import ContentModerationAgent


def main():
    """Main evaluation workflow."""
    print("=" * 60)
    print("MMAP Evaluation: Content Moderation Agent")
    print("=" * 60)

    # Initialize agent
    print("\n[1/5] Initializing Content Moderation Agent...")
    agent = ContentModerationAgent()
    print(f"✓ Agent '{agent.name}' initialized")

    # Setup evaluator with synthetic test data
    print("\n[2/5] Loading synthetic test dataset...")
    test_data_path = "../synthetic_data/content_moderation_tests.json"

    evaluator = AgentEvaluator(
        agent=agent,
        test_dataset=test_data_path,
        agent_id="content_moderation_agent_v1"
    )
    print(f"✓ Loaded test dataset: {test_data_path}")

    # Add metrics for evaluation
    print("\n[3/5] Configuring evaluation metrics...")

    # Layer 1: Input/Output Validation
    evaluator.add_metric(
        IntentAccuracy(threshold=0.95)
    )
    print("  ✓ Layer 1: IntentAccuracy (threshold=0.95)")

    # Layer 2: Model Performance
    evaluator.add_metric(
        DecisionAccuracy(threshold=0.85)
    )
    print("  ✓ Layer 2: DecisionAccuracy (threshold=0.85)")

    # Layer 3: System Integration
    evaluator.add_metric(
        APILatency(threshold_ms=200.0)  # Content moderation should be fast
    )
    print("  ✓ Layer 3: APILatency (threshold=200ms)")

    evaluator.add_metric(
        TransactionSuccess(threshold=0.99)  # High reliability expected
    )
    print("  ✓ Layer 3: TransactionSuccess (threshold=0.99)")

    # Layer 4: Business Logic
    evaluator.add_metric(
        PolicyCompliance(threshold=1.0)  # Strict policy adherence
    )
    print("  ✓ Layer 4: PolicyCompliance (threshold=1.0)")

    # Run evaluation
    print("\n[4/5] Running evaluation...")
    print("This may take a few moments...\n")

    result = evaluator.evaluate()

    # Display results
    print("\n[5/5] Evaluation Complete!")
    print("=" * 60)

    # Terminal output
    reporter = TerminalReporter()
    reporter.print_detailed(result)

    # Save JSON report
    print("\n[Saving Results]")
    json_reporter = JSONReporter()
    output_path = "./results/evaluation_result.json"
    Path("./results").mkdir(exist_ok=True)
    json_reporter.save(result, output_path)
    print(f"✓ Detailed results saved to: {output_path}")

    # Summary
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Agent ID: {result.agent_id}")
    print(f"Total Tests: {result.total_tests}")
    print(f"Overall Pass Rate: {result.overall_pass_rate:.1%}")
    print(f"Timestamp: {result.timestamp}")

    # Layer-by-layer breakdown
    print("\nLayer Results:")
    for layer_num in sorted(result.layer_results.keys()):
        layer = result.layer_results[layer_num]
        print(f"  Layer {layer_num}: {layer.pass_rate:.1%} pass rate "
              f"({layer.metrics_passed}/{layer.total_metrics} metrics passed)")

    # Metric details
    print("\nMetric Details:")
    for metric_result in result.metric_results:
        status = "✓ PASS" if metric_result.passed else "✗ FAIL"
        print(f"  {status} {metric_result.metric_name}: "
              f"{metric_result.score:.3f} (threshold: {metric_result.threshold:.3f})")

    # Content moderation specific insights
    print("\n" + "=" * 60)
    print("CONTENT MODERATION INSIGHTS")
    print("=" * 60)

    # Analyze test results for moderation-specific metrics
    print("\nKey Metrics:")
    print(f"  • Decision Accuracy: Critical for content safety")
    print(f"  • Policy Compliance: Ensures consistent moderation")
    print(f"  • Latency: Fast moderation improves user experience")

    print("\n" + "=" * 60)

    # Return exit code based on overall pass
    return 0 if result.overall_passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
