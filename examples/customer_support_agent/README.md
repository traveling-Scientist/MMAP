# Customer Support Agent Example

This example demonstrates how to evaluate a customer support agent using the MMAP framework with synthetic test data.

## Overview

The **CustomerSupportAgent** is a mock implementation that:
- Classifies customer support intents (8 categories)
- Routes requests to appropriate teams
- Handles priority levels and sentiment
- Processes requests across multiple channels

## Quick Start

### 1. Install MMAP

```bash
# From the MMAP root directory
pip install -e .
```

### 2. Run Evaluation

```bash
cd examples/customer_support_agent
python evaluate.py
```

This will:
1. Load the synthetic customer support test dataset (100 cases)
2. Run the agent on all test cases
3. Evaluate performance across multiple layers and metrics
4. Display detailed results and save JSON report

## Expected Output

```
============================================================
MMAP Evaluation: Customer Support Agent
============================================================

[1/5] Initializing Customer Support Agent...
✓ Agent 'CustomerSupportAgent' initialized

[2/5] Loading synthetic test dataset...
✓ Loaded test dataset: ../synthetic_data/customer_support_tests.json

[3/5] Configuring evaluation metrics...
  ✓ Layer 1: IntentAccuracy (threshold=0.85)
  ✓ Layer 2: DecisionAccuracy (threshold=0.80)
  ✓ Layer 3: APILatency (threshold=500ms)
  ✓ Layer 3: TransactionSuccess (threshold=0.95)

[4/5] Running evaluation...

[5/5] Evaluation Complete!
============================================================
```

## Agent Architecture

### Intent Classification

The agent classifies customer requests into 8 categories:

1. **technical_support**: Login issues, crashes, performance
2. **billing_inquiry**: Charges, invoices, payments
3. **account_management**: Account updates, upgrades
4. **product_information**: Feature questions
5. **complaint**: Customer complaints
6. **feature_request**: Enhancement requests
7. **password_reset**: Authentication issues
8. **order_status**: Order tracking

### Decision Logic

```python
Decision = f(Intent, Priority, Sentiment)

Examples:
- urgent + negative sentiment → escalated
- complaint → escalated
- password_reset → resolved (automated)
- low/medium priority → resolved
```

### Team Routing

Each intent is routed to the appropriate team:

| Intent | Routing Destination |
|--------|-------------------|
| technical_support | tech_team |
| billing_inquiry | billing_team |
| account_management | account_team |
| product_information | sales_team |
| complaint | escalation_team |
| feature_request | product_team |
| password_reset | automated |
| order_status | order_team |

## Evaluation Metrics

### Layer 1: Input/Output Validation
- **IntentAccuracy (85%)**: Correct intent classification

### Layer 2: Model Performance
- **DecisionAccuracy (80%)**: Correct handling decisions

### Layer 3: System Integration
- **APILatency (500ms)**: Response time performance
- **TransactionSuccess (95%)**: Request processing reliability

## Test Dataset

Uses **100 synthetic test cases** from `../synthetic_data/customer_support_tests.json`

**Distribution:**
- Intent Categories: Balanced across 8 types
- Priority Levels: 25% each (low, medium, high, urgent)
- Sentiment: 25% each (positive, neutral, negative, frustrated)
- Channels: 25% each (email, chat, phone, social_media)

**Test Coverage:**
- Standard support scenarios
- High-priority escalations
- Mixed priority and sentiment combinations
- Cross-channel consistency

## Customization

### Modify Business Rules

Edit `agent.py`:

```python
# Add new intent category
self.intent_routing["new_intent"] = "new_team"

# Adjust priority response times
self.response_times["urgent"] = 50  # Faster response

# Custom decision logic
def determine_decision(self, intent, priority, sentiment):
    # Your custom logic here
    pass
```

### Adjust Evaluation Thresholds

Edit `evaluate.py`:

```python
# Stricter intent accuracy
evaluator.add_metric(IntentAccuracy(threshold=0.95))

# Faster latency requirement
evaluator.add_metric(APILatency(threshold_ms=300.0))
```

### Filter Test Cases

```python
import json

with open("../synthetic_data/customer_support_tests.json") as f:
    all_tests = json.load(f)

# Only urgent cases
urgent_tests = [t for t in all_tests if t["input"]["priority"] == "urgent"]

# Only technical support
tech_tests = [t for t in all_tests if "technical_support" in t["tags"]]

evaluator = AgentEvaluator(
    agent=agent,
    test_dataset=urgent_tests,  # Use filtered subset
    agent_id="urgent_cases_eval"
)
```

## Integration with Real Agents

Replace the mock agent with your actual implementation:

```python
from langchain import LLMChain  # Or your framework
from your_agent import YourCustomerSupportAgent

# Your real agent
agent = YourCustomerSupportAgent()

# Ensure your agent implements process(test_case) -> dict
# with the required output fields

evaluator = AgentEvaluator(
    agent=agent,
    test_dataset="../synthetic_data/customer_support_tests.json",
    agent_id="your_agent_v1"
)

# Add metrics and evaluate
evaluator.add_metric(IntentAccuracy(threshold=0.90))
result = evaluator.evaluate()
```

## Output

### Terminal Report
Detailed metrics, scores, and pass/fail status displayed in the terminal.

### JSON Report
Saved to `./results/evaluation_result.json` with:
- Overall scores and pass rates
- Layer-by-layer breakdown
- Individual metric results
- Per-test-case details
- Timestamps and metadata

## File Structure

```
customer_support_agent/
├── agent.py              # Mock customer support agent
├── evaluate.py           # Evaluation script
├── README.md             # This file
└── results/              # Output directory (created on first run)
    └── evaluation_result.json
```

## Next Steps

1. **Run the evaluation**: `python evaluate.py`
2. **Review results**: Check terminal output and JSON report
3. **Adjust thresholds**: Modify metrics based on requirements
4. **Customize agent**: Update business logic for your use case
5. **Add more metrics**: Include Layer 4 (PolicyCompliance) or Layer 5 (Fairness)
6. **Generate more data**: Use synthetic data generator for additional test cases

## Related Examples

- [Refund Agent](../refund_agent/README.md) - Complete refund processing example
- [Content Moderation Agent](../content_moderation_agent/README.md) - Content safety example
- [Synthetic Data](../synthetic_data/README.md) - Test data generation guide

## Troubleshooting

**Import errors:**
```bash
# Ensure MMAP is installed
pip install -e /path/to/MMAP

# Or add to path
export PYTHONPATH="/path/to/MMAP:$PYTHONPATH"
```

**Dataset not found:**
```bash
# Ensure synthetic data exists
ls ../synthetic_data/customer_support_tests.json

# Or regenerate
cd ../..
python mmap_eval/utils/synthetic_generator.py --type support --count 100
```

## License

MIT License - See main MMAP repository for details.
