"""Evaluation script for the refund agent.

This demonstrates how to use MMAP to evaluate an AI agent across all 5 layers.
"""

import sys
from pathlib import Path

# Add parent directory to path to import mmap
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mmap_eval import AgentEvaluator
from mmap_eval.metrics import (
    # Layer 1: Input/Output Validation
    IntentAccuracy,
    EntityExtractionAccuracy,
    # Layer 2: Model Performance
    DecisionAccuracy,
    HallucinationDetection,
    # Layer 3: System Integration
    APILatency,
    TransactionSuccess,
    # Layer 4: Business Logic
    PolicyCompliance,
    EdgeCaseHandling,
    # Layer 5: Fairness & Compliance
    DemographicParity,
    AuditTrail,
)
from mmap_eval.reporters import TerminalReporter, JSONReporter

from agent import refund_agent


def main():
    """Run comprehensive evaluation of the refund agent."""
    print("=" * 70)
    print("MMAP Evaluation: Refund Agent")
    print("=" * 70)
    print()

    # Create evaluator
    evaluator = AgentEvaluator(
        agent=refund_agent,
        test_dataset="test_cases.json",
        agent_id="refund_agent_v1.0"
    )

    # Add Layer 1 metrics: Input/Output Validation
    print("Adding Layer 1 metrics (Input/Output Validation)...")
    evaluator.add_metric(IntentAccuracy(threshold=0.90))
    evaluator.add_metric(EntityExtractionAccuracy(threshold=0.85))

    # Add Layer 2 metrics: Model Performance
    print("Adding Layer 2 metrics (Model Performance)...")
    evaluator.add_metric(DecisionAccuracy(threshold=0.95))
    evaluator.add_metric(HallucinationDetection(threshold=0.90))

    # Add Layer 3 metrics: System Integration
    print("Adding Layer 3 metrics (System Integration)...")
    evaluator.add_metric(APILatency(max_latency_ms=2000, threshold=0.95))
    evaluator.add_metric(TransactionSuccess(threshold=0.99))

    # Add Layer 4 metrics: Business Logic
    print("Adding Layer 4 metrics (Business Logic)...")
    evaluator.add_metric(PolicyCompliance(threshold=1.0))
    evaluator.add_metric(EdgeCaseHandling(threshold=0.90))

    # Add Layer 5 metrics: Fairness & Compliance
    print("Adding Layer 5 metrics (Fairness & Compliance)...")
    evaluator.add_metric(DemographicParity(threshold=0.95))
    evaluator.add_metric(
        AuditTrail(
            required_fields=["timestamp", "action", "decision", "reason"],
            threshold=1.0
        )
    )

    print(f"\nTotal metrics registered: {evaluator.registry.count()}")
    print(f"Test cases loaded: {len(evaluator.test_cases)}")
    print()

    # Run evaluation
    print("Running evaluation...")
    print("This may take a moment...\n")

    result = evaluator.evaluate()

    # Print results to terminal
    reporter = TerminalReporter()
    reporter.print_detailed(result)

    # Save results to JSON
    output_file = Path("results") / "evaluation_results.json"
    output_file.parent.mkdir(exist_ok=True)
    JSONReporter.save(result, output_file)

    print(f"\nResults saved to: {output_file}")

    # Print summary statistics
    print("\n" + "=" * 70)
    print("Summary Statistics")
    print("=" * 70)
    print(f"Overall Score: {result.overall_score:.2%}")
    print(f"Status: {'PASS' if result.passed else 'FAIL'}")
    print(f"Total Test Cases: {result.test_cases_count}")
    print(f"Duration: {result.duration_seconds:.2f}s")
    print(f"Critical Issues: {len(result.critical_issues)}")
    print()

    # Layer-by-layer breakdown
    print("Layer Scores:")
    for layer in result.layers:
        status = "✓ PASS" if layer.passed else "✗ FAIL"
        print(f"  Layer {layer.layer_number} - {layer.layer_name}: {layer.score:.2%} [{status}]")
    print()

    # Exit with appropriate code
    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
