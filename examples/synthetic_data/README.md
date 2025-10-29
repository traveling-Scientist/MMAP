# Synthetic Test Data for MMAP

This directory contains synthetically generated test datasets for evaluating multi-modal agents using the MMAP framework.

## 📁 Available Datasets

### 1. Refund Agent Tests (`refund_agent_tests.json`)
**94 test cases** covering refund processing scenarios

**Test Coverage:**
- ✅ **Standard Cases (50+)**: Valid refund requests with various amounts and timeframes
- 🔍 **Edge Cases (8)**: Missing data, zero/negative amounts, boundary conditions, expirations
- ⚖️ **Fairness Tests (30)**: Multiple demographic groups (age, region) for bias detection
- ⚡ **Latency Tests (15)**: Simple, moderate, and complex queries for performance measurement
- 🎯 **Hallucination Tests (6)**: Cases designed to test factual accuracy

**Layers Tested:**
- Layer 1: Intent classification, entity extraction
- Layer 2: Decision accuracy, hallucination detection
- Layer 3: API latency, transaction success
- Layer 4: Policy compliance, edge case handling
- Layer 5: Demographic parity, audit trail

**Business Rules:**
- Maximum refund: $500
- Refund window: 30 days
- Escalation threshold: $1,000

---

### 2. Customer Support Tests (`customer_support_tests.json`)
**100 test cases** for customer support agents

**Intent Categories:**
- `technical_support`: Login issues, crashes, performance problems
- `billing_inquiry`: Charges, invoices, payment updates
- `account_management`: Account updates, upgrades, deletions
- `product_information`: Feature questions, product inquiries
- `complaint`: Customer complaints
- `feature_request`: Enhancement requests
- `password_reset`: Authentication issues
- `order_status`: Order tracking

**Test Attributes:**
- **Priority Levels**: low, medium, high, urgent
- **Sentiment**: positive, neutral, negative, frustrated
- **Channels**: email, chat, phone, social_media
- **Routing**: Appropriate team assignment based on intent

**Layers Tested:**
- Layer 1: Intent classification, routing decisions
- Layer 2: Response accuracy, priority assessment
- Layer 4: Policy compliance, escalation handling

---

### 3. Content Moderation Tests (`content_moderation_tests.json`)
**100 test cases** for content moderation agents

**Content Distribution:**
- 70% Safe Content: Approved posts/comments
- 30% Unsafe Content: Policy violations

**Violation Types:**
- `spam`: Unsolicited promotional content
- `hate_speech`: Discriminatory language
- `violence`: Violent threats or content
- `sexual_content`: Inappropriate sexual material
- `misinformation`: False or misleading claims
- `harassment`: Targeted harassment
- `copyright`: Unauthorized copyrighted material
- `none`: No violations

**Severity Levels:**
- `low`: Minor infractions
- `medium`: Moderate policy violations
- `high`: Serious violations
- `critical`: Severe violations requiring immediate action

**Actions:**
- `publish`: Approve content
- `flag`: Mark for review
- `remove`: Remove content immediately

**Layers Tested:**
- Layer 1: Content classification, violation detection
- Layer 2: Decision accuracy, severity assessment
- Layer 4: Policy enforcement, edge case handling

---

## 🚀 Quick Start

### Generate New Synthetic Data

```bash
# Generate all datasets (100 test cases each)
python mmap_eval/utils/synthetic_generator.py --type all --count 100

# Generate only refund agent tests
python mmap_eval/utils/synthetic_generator.py --type refund --count 50

# Generate only customer support tests
python mmap_eval/utils/synthetic_generator.py --type support --count 75

# Generate only content moderation tests
python mmap_eval/utils/synthetic_generator.py --type moderation --count 100

# Custom output directory
python mmap_eval/utils/synthetic_generator.py --type all --output-dir ./my_tests --count 200

# Use different random seed
python mmap_eval/utils/synthetic_generator.py --type all --seed 12345
```

### Using Synthetic Data in Your Evaluation

```python
from mmap_eval.core.evaluator import AgentEvaluator
from mmap_eval.metrics.layer1 import IntentAccuracy, EntityExtractionAccuracy
from mmap_eval.metrics.layer2 import DecisionAccuracy
from your_agent import YourAgent

# Initialize your agent
agent = YourAgent()

# Load synthetic test data
evaluator = AgentEvaluator(
    agent=agent,
    test_dataset="examples/synthetic_data/refund_agent_tests.json",
    agent_id="my_refund_agent_v1"
)

# Add metrics you want to evaluate
evaluator.add_metric(IntentAccuracy(threshold=0.90))
evaluator.add_metric(DecisionAccuracy(threshold=0.95))
evaluator.add_metric(EntityExtractionAccuracy(threshold=0.85))

# Run evaluation
result = evaluator.evaluate()

# View results
from mmap_eval.reporters import TerminalReporter
reporter = TerminalReporter()
reporter.print_detailed(result)
```

---

## 📊 Test Case Schema

All test cases follow this structure:

```json
{
  "id": "test_0001",
  "input": {
    "text": "User input text",
    "field1": "domain-specific data",
    "field2": 123,
    "demographics": {
      "age_group": "26-35",
      "region": "North America"
    }
  },
  "ground_truth": {
    "intent": "expected_intent",
    "decision": "expected_decision",
    "entities": {
      "entity1": "value1"
    },
    "hallucination_expected": false,
    "policy_compliant": true,
    "bias_expected": false
  },
  "tags": [
    "layer1",
    "layer2",
    "standard",
    "specific_category"
  ],
  "metadata": {
    "custom_field": "optional"
  }
}
```

---

## 🎯 Creating Custom Synthetic Data

### Extend the Generator

```python
from mmap_eval.utils.synthetic_generator import SyntheticDataGenerator

class MyCustomDataGenerator(SyntheticDataGenerator):
    def __init__(self, seed=42):
        super().__init__(seed)
        # Your custom configuration

    def generate_custom_cases(self, count=50):
        cases = []
        for i in range(count):
            case = {
                "id": self.generate_id("custom"),
                "input": {
                    "text": "Custom input",
                    # Your fields
                },
                "ground_truth": {
                    "intent": "custom_intent",
                    # Your expected outputs
                },
                "tags": ["layer1", "custom"]
            }
            cases.append(case)
        return cases

# Use your custom generator
generator = MyCustomDataGenerator(seed=42)
test_cases = generator.generate_custom_cases(count=100)
generator.save_to_file(test_cases, "my_custom_tests.json")
```

---

## 🔍 Filtering Test Cases

Filter by tags or other criteria:

```python
import json

# Load test data
with open("examples/synthetic_data/refund_agent_tests.json") as f:
    all_tests = json.load(f)

# Filter edge cases only
edge_cases = [t for t in all_tests if "edge_case" in t["tags"]]

# Filter by layer
layer1_tests = [t for t in all_tests if "layer1" in t["tags"]]

# Filter by decision type
approved_tests = [t for t in all_tests if t["ground_truth"]["decision"] == "approved"]

# Use filtered data
evaluator = AgentEvaluator(
    agent=my_agent,
    test_dataset=edge_cases,  # Use filtered subset
    agent_id="edge_case_evaluation"
)
```

---

## 📈 Test Statistics

### Refund Agent Tests (94 cases)
- Standard cases: ~53% (50 cases)
- Edge cases: ~9% (8 cases)
- Fairness cases: ~32% (30 cases)
- Latency cases: ~16% (15 cases)
- Hallucination cases: ~6% (6 cases)

### Customer Support Tests (100 cases)
- Intent distribution: Balanced across 8 intent categories
- Priority: 25% each (low, medium, high, urgent)
- Sentiment: 25% each (positive, neutral, negative, frustrated)
- Channel: 25% each (email, chat, phone, social_media)

### Content Moderation Tests (100 cases)
- Safe content: 70 cases
- Unsafe content: 30 cases
- Violation types: Distributed across 7 categories
- Severity: Varies from low to critical

---

## 🔧 Customization Options

### Adjust Generation Parameters

```python
from mmap_eval.utils.synthetic_generator import RefundAgentDataGenerator

generator = RefundAgentDataGenerator(seed=42)

# Customize business rules
generator.MAX_REFUND_AMOUNT = 1000.0  # Increase limit
generator.MAX_REFUND_DAYS = 45         # Extend window
generator.ESCALATION_THRESHOLD = 5000.0  # Higher escalation

# Generate with custom distribution
test_cases = generator.generate_complete_dataset(
    standard_count=100,   # More standard cases
    fairness_count=50,    # More fairness tests
    latency_count=25      # More latency tests
)

generator.save_to_file(test_cases, "custom_refund_tests.json")
```

---

## 📚 Best Practices

1. **Use Appropriate Dataset**: Choose the dataset that matches your agent's domain
2. **Start Small**: Begin with 10-20 test cases to validate your agent integration
3. **Scale Gradually**: Increase to full dataset once integration is confirmed
4. **Mix Test Types**: Include standard, edge, fairness, and performance cases
5. **Filter When Needed**: Use tags to focus on specific layers or scenarios
6. **Regenerate Regularly**: Generate fresh data with different seeds for variety
7. **Custom Ground Truth**: Adjust ground truth values to match your business rules
8. **Monitor Coverage**: Ensure all layers and scenarios important to you are tested

---

## 🤝 Contributing

To add new synthetic data generators:

1. Extend `SyntheticDataGenerator` base class
2. Implement domain-specific generation methods
3. Follow the standard test case schema
4. Include comprehensive tags for filtering
5. Document your generator in this README

---

## 📝 License

These synthetic datasets are provided under the same MIT License as MMAP.

---

## 🐛 Issues & Feedback

If you encounter issues with synthetic data or need additional test scenarios, please open an issue at the MMAP repository.

---

## 📖 Related Documentation

- [MMAP README](../../README.md) - Main framework documentation
- [Refund Agent Example](../refund_agent/README.md) - Complete example implementation
- [Core Evaluator](../../mmap_eval/core/evaluator.py) - Evaluation framework
- [Metrics Documentation](../../mmap_eval/metrics/) - Available metrics

---

Generated with MMAP Synthetic Data Generator v0.1.0
