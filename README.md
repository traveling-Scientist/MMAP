# MMAP: Multi-Modal Agent Assessment Protocol

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**MMAP** is a comprehensive evaluation framework for autonomous AI agents that addresses the critical gap between development testing and production readiness.

## The Problem

**67% of AI agents fail in production despite passing development tests.**

Current evaluation approaches focus narrowly on model outputs, missing critical failures in:
- System integration
- Business logic compliance
- Fairness and bias
- Edge case handling
- Audit requirements

MMAP provides a **systematic, 5-layer evaluation framework** that catches failures before production.

## Features

- **5-Layer Evaluation Framework**: Comprehensive assessment across input/output, model performance, system integration, business logic, and fairness
- **10+ Pre-Built Metrics**: Ready-to-use metrics for common evaluation needs
- **Framework Agnostic**: Works with any agent architecture (LangChain, LlamaIndex, custom)
- **Production-First Design**: Built for continuous monitoring, not just one-time testing
- **CLI Tool**: Easy-to-use command-line interface
- **Rich Reporting**: Terminal and JSON outputs with detailed insights
- **Extensible**: Easy to add custom metrics

## Quick Start

### Installation

```bash
pip install mmap-eval
```

Or install from source:

```bash
git clone https://github.com/traveling-Scientist/MMAP.git
cd MMAP
pip install -e .
```

### Basic Usage

```python
from mmap_eval import AgentEvaluator
from mmap_eval.metrics import IntentAccuracy, DecisionAccuracy
from mmap_eval.reporters import TerminalReporter

# Define your agent function
def my_agent(input_data):
    # Your agent logic here
    return {
        "intent": "refund_request",
        "decision": "approved",
        "entities": {}
    }

# Create evaluator
evaluator = AgentEvaluator(
    agent=my_agent,
    test_dataset="tests.json",
    agent_id="my_agent_v1"
)

# Add metrics
evaluator.add_metric(IntentAccuracy(threshold=0.90))
evaluator.add_metric(DecisionAccuracy(threshold=0.95))

# Run evaluation
result = evaluator.evaluate()

# Print results
reporter = TerminalReporter()
reporter.print_summary(result)

# Save results
result.to_json("results/evaluation.json")
```

### CLI Usage

Initialize a new evaluation project:

```bash
mmap init my-agent-eval
cd my-agent-eval
```

Run evaluation:

```bash
python evaluate.py
```

View saved results:

```bash
mmap report results/evaluation.json
```

## The 5-Layer Framework

MMAP evaluates agents across 5 critical layers:

### Layer 1: Input/Output Validation
Validates that agents correctly parse inputs and produce well-formed outputs.

**Metrics:**
- `IntentAccuracy` - Intent classification accuracy
- `EntityExtractionAccuracy` - Entity extraction F1 score

### Layer 2: Model Performance
Evaluates core model decision-making and output quality.

**Metrics:**
- `DecisionAccuracy` - Decision correctness
- `HallucinationDetection` - Detects unsupported claims

### Layer 3: System Integration
Tests API interactions, latency, and transaction success.

**Metrics:**
- `APILatency` - Response time measurement
- `TransactionSuccess` - API call success rate

### Layer 4: Business Logic
Verifies compliance with business rules and edge case handling.

**Metrics:**
- `PolicyCompliance` - Business rule adherence
- `EdgeCaseHandling` - Edge case robustness

### Layer 5: Fairness & Compliance
Ensures fairness, bias mitigation, and audit compliance.

**Metrics:**
- `DemographicParity` - Fairness across groups
- `AuditTrail` - Audit log completeness

## Test Dataset Format

Test cases are defined in JSON format:

```json
[
  {
    "id": "test_001",
    "input": {
      "text": "I want a refund",
      "order_id": "ORD123",
      "amount": 50.0,
      "purchase_date": "2025-10-20T10:00:00Z"
    },
    "ground_truth": {
      "intent": "refund_request",
      "decision": "approved",
      "entities": {
        "order_id": "ORD123",
        "amount": 50.0
      }
    },
    "tags": ["standard", "refund"]
  }
]
```

## Examples

### Refund Agent Example

A complete example is provided in `examples/refund_agent/`:

```bash
cd examples/refund_agent
python evaluate.py
```

This demonstrates:
- Complete agent implementation
- 37+ test cases covering all 5 layers
- All 10 pre-built metrics
- Edge case handling
- Fairness testing

See [examples/refund_agent/README.md](examples/refund_agent/README.md) for details.

## Creating Custom Metrics

Extend `BaseMetric` to create custom metrics:

```python
from mmap_eval.core.metric import BaseMetric, MetricResult, Severity

class CustomMetric(BaseMetric):
    def __init__(self, threshold=0.9):
        super().__init__(
            name="Custom Metric",
            layer=4,
            threshold=threshold,
            severity=Severity.WARNING,
            description="My custom metric"
        )

    def evaluate(self, output, ground_truth, **kwargs):
        # Your evaluation logic
        score = ... # Calculate score (0-1)

        return MetricResult(
            metric_name=self.name,
            layer=self.layer,
            score=score,
            threshold=self.threshold,
            passed=score >= self.threshold,
            severity=self.severity,
            details={"info": "details here"},
        )

# Use it
evaluator.add_metric(CustomMetric(threshold=0.85))
```

## API Reference

### Core Classes

- **`AgentEvaluator`** - Main evaluator orchestrator
- **`BaseMetric`** - Base class for all metrics
- **`MetricResult`** - Individual metric result
- **`EvaluationResult`** - Complete evaluation results
- **`TestCase`** - Test case data model
- **`TestLoader`** - Load test cases from various sources

### Metrics

All metrics are available in `mmap_eval.metrics`:

```python
from mmap_eval.metrics import (
    # Layer 1
    IntentAccuracy,
    EntityExtractionAccuracy,
    # Layer 2
    DecisionAccuracy,
    HallucinationDetection,
    # Layer 3
    APILatency,
    TransactionSuccess,
    # Layer 4
    PolicyCompliance,
    EdgeCaseHandling,
    # Layer 5
    DemographicParity,
    AuditTrail,
)
```

### Reporters

```python
from mmap_eval.reporters import TerminalReporter, JSONReporter

# Terminal output
reporter = TerminalReporter()
reporter.print_summary(result)
reporter.print_detailed(result)

# JSON export
JSONReporter.save(result, "output.json")
result_loaded = JSONReporter.load("output.json")
```

## Architecture

```
mmap/
├── core/
│   ├── evaluator.py      # AgentEvaluator
│   ├── metric.py         # BaseMetric, MetricResult
│   ├── registry.py       # MetricRegistry
│   ├── test_loader.py    # TestLoader, TestCase
│   └── result.py         # EvaluationResult, LayerResult
├── metrics/
│   ├── layer1/           # Input/Output metrics
│   ├── layer2/           # Model performance metrics
│   ├── layer3/           # System integration metrics
│   ├── layer4/           # Business logic metrics
│   └── layer5/           # Fairness & compliance metrics
├── cli/
│   └── main.py           # CLI application
└── reporters/
    ├── terminal_reporter.py
    └── json_reporter.py
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/traveling-Scientist/MMAP.git
cd MMAP

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy mmap

# Format code
black mmap
isort mmap
```

### Running Tests

```bash
pytest tests/ --cov=mmap --cov-report=html
```

## Roadmap

### MVP (v0.1-0.5) - Current
- ✅ 5-layer evaluation framework
- ✅ 10 pre-built metrics
- ✅ Python SDK
- ✅ CLI tool
- ✅ Terminal & JSON reporters
- ✅ Refund agent example

### v1.0 - Production Ready
- HTML dashboard
- Framework integrations (LangChain, LlamaIndex)
- Extended metrics library (30+ metrics)
- Batch evaluation
- CI/CD integration

### v2.0 - SaaS Platform
- Continuous monitoring
- Team collaboration
- Cloud-hosted evaluations
- Advanced analytics
- Compliance reporting

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas where we'd love help:
- Additional metrics
- Framework integrations
- Documentation improvements
- Bug reports and fixes
- Example implementations

## Citation

If you use MMAP in your research or project, please cite:

```bibtex
@software{mmap2025,
  title={MMAP: Multi-Modal Agent Assessment Protocol},
  author={MMAP Contributors},
  year={2025},
  url={https://github.com/traveling-Scientist/MMAP}
}
```

## License

MMAP is released under the MIT License. See [LICENSE](LICENSE) for details.

## Support

- **Documentation**: [GitHub README](https://github.com/traveling-Scientist/MMAP)
- **Issues**: [GitHub Issues](https://github.com/traveling-Scientist/MMAP/issues)
- **Discussions**: [GitHub Discussions](https://github.com/traveling-Scientist/MMAP/discussions)

## Acknowledgments

MMAP is inspired by the need for comprehensive AI agent evaluation in production environments. Special thanks to the AI/ML community for feedback and contributions.

---

**Make every AI agent production-ready through comprehensive, standardized evaluation.**
