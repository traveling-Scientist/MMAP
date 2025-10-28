# Refund Agent Example

This is a comprehensive example demonstrating how to use MMAP to evaluate an AI agent across all 5 layers.

## Overview

The refund agent is a customer service agent that processes refund requests. It demonstrates:

- **Layer 1**: Input/Output Validation (intent classification, entity extraction)
- **Layer 2**: Model Performance (decision accuracy, hallucination detection)
- **Layer 3**: System Integration (API latency, transaction success)
- **Layer 4**: Business Logic (policy compliance, edge case handling)
- **Layer 5**: Fairness & Compliance (demographic parity, audit trails)

## Business Rules

The refund agent follows these business rules:

- Maximum refund amount: $500
- Refund window: 30 days from purchase
- Escalation threshold: $1,000
- Required fields: order ID, amount, purchase date

## Files

- `agent.py` - The refund agent implementation
- `generate_tests.py` - Script to generate test cases
- `test_cases.json` - Generated test cases (37+ tests)
- `evaluate.py` - Evaluation script
- `results/` - Output directory for evaluation results

## Running the Evaluation

1. Generate test cases (if not already generated):
   ```bash
   python generate_tests.py
   ```

2. Run the evaluation:
   ```bash
   python evaluate.py
   ```

3. View results:
   - Terminal output shows detailed results
   - JSON results saved to `results/evaluation_results.json`

## Test Cases

The test dataset includes:

- **Layer 1 Tests (5)**: Intent variations, entity extraction
- **Layer 2 Tests (3)**: Decision accuracy, hallucination detection
- **Layer 3 Tests (6)**: Latency tests, transaction success
- **Layer 4 Tests (8)**: Policy compliance, edge cases, boundary conditions
- **Layer 5 Tests (9)**: Demographic fairness, audit trails

### Edge Cases Covered

- Missing order ID
- Zero and negative amounts
- Expired refund window
- Amounts at/exceeding limits
- Escalation scenarios
- Boundary conditions

### Fairness Testing

The dataset includes test cases with different demographic groups to evaluate fairness and demographic parity.

## Expected Results

A well-implemented agent should achieve:

- Layer 1 (Input/Output): >90% accuracy
- Layer 2 (Model Performance): >95% accuracy
- Layer 3 (System Integration): >95% success rate, <2000ms latency
- Layer 4 (Business Logic): 100% policy compliance
- Layer 5 (Fairness): >95% demographic parity, 100% audit completeness

## Extending the Example

You can extend this example by:

1. Adding more test cases to `generate_tests.py`
2. Implementing additional metrics
3. Modifying business rules in `agent.py`
4. Adding custom evaluation logic

## Resources

- [MMAP Documentation](https://github.com/traveling-Scientist/MMAP)
- [API Reference](https://github.com/traveling-Scientist/MMAP#api-reference)
