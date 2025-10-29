# Content Moderation Agent Example

This example demonstrates how to evaluate a content moderation agent using the MMAP framework with synthetic test data.

## Overview

The **ContentModerationAgent** is a mock implementation that:
- Detects policy violations (7 violation types)
- Calculates severity levels (low, medium, high, critical)
- Determines moderation actions (publish, flag, remove)
- Provides audit trails for decisions

## Quick Start

### 1. Install MMAP

```bash
# From the MMAP root directory
pip install -e .
```

### 2. Run Evaluation

```bash
cd examples/content_moderation_agent
python evaluate.py
```

This will:
1. Load the synthetic content moderation test dataset (100 cases)
2. Run the agent on all test cases
3. Evaluate performance across multiple layers and metrics
4. Display detailed results and save JSON report

## Expected Output

```
============================================================
MMAP Evaluation: Content Moderation Agent
============================================================

[1/5] Initializing Content Moderation Agent...
✓ Agent 'ContentModerationAgent' initialized

[2/5] Loading synthetic test dataset...
✓ Loaded test dataset: ../synthetic_data/content_moderation_tests.json

[3/5] Configuring evaluation metrics...
  ✓ Layer 1: IntentAccuracy (threshold=0.95)
  ✓ Layer 2: DecisionAccuracy (threshold=0.85)
  ✓ Layer 3: APILatency (threshold=200ms)
  ✓ Layer 3: TransactionSuccess (threshold=0.99)
  ✓ Layer 4: PolicyCompliance (threshold=1.0)

[4/5] Running evaluation...

[5/5] Evaluation Complete!
============================================================
```

## Agent Architecture

### Violation Detection

The agent detects 7 types of policy violations:

1. **spam**: Unsolicited promotional content
2. **hate_speech**: Discriminatory language
3. **violence**: Violent threats or content
4. **sexual_content**: Inappropriate sexual material
5. **misinformation**: False or misleading claims
6. **harassment**: Targeted harassment or bullying
7. **copyright**: Unauthorized copyrighted material

### Severity Calculation

Violations are weighted by severity:

| Violation Type | Weight | Typical Severity |
|----------------|--------|------------------|
| spam | 1 | low |
| harassment | 2 | medium |
| sexual_content | 3 | high |
| misinformation | 2 | medium |
| copyright | 2 | medium |
| hate_speech | 4 | critical |
| violence | 4 | critical |

**Severity Mapping:**
- Weight 4+ → **critical**
- Weight 3 → **high**
- Weight 2 → **medium**
- Weight 1 → **low**

### Action Determination

```python
Action = f(Violations, Severity)

Decision Rules:
- No violations → publish
- critical/high severity → remove
- medium/low severity → flag
```

### Decision Logic

- **approved**: No policy violations detected
- **rejected**: One or more violations detected

## Evaluation Metrics

### Layer 1: Input/Output Validation
- **IntentAccuracy (95%)**: Correct classification as moderation task

### Layer 2: Model Performance
- **DecisionAccuracy (85%)**: Correct approve/reject decisions

### Layer 3: System Integration
- **APILatency (200ms)**: Fast moderation response
- **TransactionSuccess (99%)**: High reliability

### Layer 4: Business Logic
- **PolicyCompliance (100%)**: Strict policy adherence

## Test Dataset

Uses **100 synthetic test cases** from `../synthetic_data/content_moderation_tests.json`

**Distribution:**
- Safe Content: 70 cases (should be approved)
- Unsafe Content: 30 cases (should be rejected)

**Violation Coverage:**
- spam
- hate_speech
- violence
- sexual_content
- misinformation
- harassment
- copyright

**Severity Distribution:**
- low: Minor infractions
- medium: Moderate violations
- high: Serious violations
- critical: Severe violations

**Content Types:**
- text
- image (metadata)
- video (metadata)
- comment
- post

## Customization

### Modify Detection Rules

Edit `agent.py`:

```python
# Add new violation type
self.violation_keywords["new_violation"] = ["keyword1", "keyword2"]

# Adjust severity weights
self.severity_weights["spam"] = 2  # Increase spam severity

# Custom detection logic
def detect_violations(self, content: str) -> List[str]:
    # Your ML model or API integration here
    pass
```

### Adjust Evaluation Thresholds

Edit `evaluate.py`:

```python
# Stricter decision accuracy
evaluator.add_metric(DecisionAccuracy(threshold=0.95))

# Even faster latency requirement
evaluator.add_metric(APILatency(threshold_ms=100.0))

# Add fairness testing
from mmap_eval.metrics.layer5 import DemographicParity
evaluator.add_metric(DemographicParity(threshold=0.95))
```

### Filter Test Cases

```python
import json

with open("../synthetic_data/content_moderation_tests.json") as f:
    all_tests = json.load(f)

# Only unsafe content
unsafe_tests = [t for t in all_tests if "unsafe" in t["tags"]]

# Only high severity
high_severity = [t for t in all_tests if
                 t["ground_truth"].get("severity") == "high"]

# Specific violation type
spam_tests = [t for t in all_tests if "spam" in t["tags"]]

evaluator = AgentEvaluator(
    agent=agent,
    test_dataset=unsafe_tests,  # Use filtered subset
    agent_id="unsafe_content_eval"
)
```

## Integration with Real Moderation Systems

Replace the mock agent with your actual implementation:

```python
from your_moderation_system import YourModerationAgent

# Your real agent (could use ML models, APIs, etc.)
agent = YourModerationAgent()

# Ensure your agent implements process(test_case) -> dict
# with the required output fields:
# - intent
# - decision (approved/rejected)
# - violation_type
# - severity
# - action
# - response
# - audit_trail

evaluator = AgentEvaluator(
    agent=agent,
    test_dataset="../synthetic_data/content_moderation_tests.json",
    agent_id="your_moderation_agent_v1"
)

# Add metrics and evaluate
evaluator.add_metric(DecisionAccuracy(threshold=0.90))
evaluator.add_metric(PolicyCompliance(threshold=1.0))
result = evaluator.evaluate()
```

## Example: Integration with OpenAI Moderation API

```python
import openai
from content_moderation_agent import ContentModerationAgent

class OpenAIModerationAgent(ContentModerationAgent):
    def __init__(self, api_key):
        super().__init__()
        self.client = openai.OpenAI(api_key=api_key)

    def detect_violations(self, content: str):
        # Use OpenAI's moderation endpoint
        response = self.client.moderations.create(input=content)

        violations = []
        result = response.results[0]

        if result.categories.hate:
            violations.append("hate_speech")
        if result.categories.violence:
            violations.append("violence")
        if result.categories.sexual:
            violations.append("sexual_content")
        if result.categories.harassment:
            violations.append("harassment")

        return violations if violations else ["none"]

# Use with MMAP
agent = OpenAIModerationAgent(api_key="your-key")
evaluator = AgentEvaluator(agent=agent, test_dataset="test_cases.json")
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
- Violation statistics
- Timestamps and metadata

## File Structure

```
content_moderation_agent/
├── agent.py              # Mock content moderation agent
├── evaluate.py           # Evaluation script
├── README.md             # This file
└── results/              # Output directory (created on first run)
    └── evaluation_result.json
```

## Testing the Agent Directly

Run the agent standalone to see how it works:

```bash
python agent.py
```

Output:
```
Test 1: Safe Content
  Decision: approved
  Action: publish
  Explanation: Content approved - no policy violations detected.

Test 2: Spam Content
  Decision: rejected
  Violation: spam
  Severity: low
  Action: flag
  Explanation: Content flagged for: spam. Severity: low. Action taken: flag.

Test 3: Severe Violation
  Decision: rejected
  Violations: ['violence', 'hate_speech']
  Severity: critical
  Action: remove
  Explanation: Content flagged for: violence, hate_speech. Severity: critical. Action taken: remove.
```

## Best Practices

1. **High Accuracy Required**: Content moderation errors can harm users or suppress legitimate speech
2. **Fast Response Times**: Users expect quick feedback on content submissions
3. **Consistent Decisions**: Same content should yield same decisions
4. **Audit Trails**: Document all decisions for accountability
5. **Balance Safety & Expression**: Minimize false positives while protecting users
6. **Regular Evaluation**: Continuously test with new content patterns

## Next Steps

1. **Run the evaluation**: `python evaluate.py`
2. **Review results**: Analyze terminal output and JSON report
3. **Test edge cases**: Review how agent handles borderline content
4. **Adjust sensitivity**: Tune detection rules based on your policy
5. **Add fairness testing**: Ensure consistent decisions across demographics
6. **Integrate real ML**: Replace keyword matching with ML models or APIs
7. **Monitor production**: Continuously evaluate with real content samples

## Related Examples

- [Refund Agent](../refund_agent/README.md) - Business logic evaluation example
- [Customer Support Agent](../customer_support_agent/README.md) - Intent classification example
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
ls ../synthetic_data/content_moderation_tests.json

# Or regenerate
cd ../..
python mmap_eval/utils/synthetic_generator.py --type moderation --count 100
```

**Policy compliance failures:**
- Review your policy rules in `agent.py`
- Ensure ground truth in test data matches your policies
- Adjust detection thresholds as needed

## Safety & Ethics

When deploying content moderation systems:

- **Transparency**: Users should understand moderation decisions
- **Appeals Process**: Allow users to contest decisions
- **Bias Testing**: Regularly test for demographic bias
- **Human Oversight**: Critical decisions should involve human review
- **Regular Audits**: Conduct periodic audits of moderation decisions

## License

MIT License - See main MMAP repository for details.
