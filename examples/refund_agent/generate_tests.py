"""Generate test cases for the refund agent."""

import json
from datetime import datetime, timedelta


def generate_test_cases():
    """Generate comprehensive test cases for refund agent."""
    test_cases = []
    test_id = 1

    # Helper function
    def add_test(text, order_id, amount, purchase_date, reason, expected_intent,
                 expected_decision, tags=None, demographics=None, **kwargs):
        nonlocal test_id
        test = {
            "id": f"test_{test_id:03d}",
            "input": {
                "text": text,
                "order_id": order_id,
                "amount": amount,
                "purchase_date": purchase_date,
                "reason": reason,
            },
            "ground_truth": {
                "intent": expected_intent,
                "decision": expected_decision,
                **kwargs
            },
            "tags": tags or []
        }

        if demographics:
            test["input"]["demographics"] = demographics
            test["ground_truth"]["demographics"] = demographics

        test_cases.append(test)
        test_id += 1

    # Current date for relative calculations
    now = datetime.now()
    recent_date = (now - timedelta(days=5)).isoformat() + "Z"
    old_date = (now - timedelta(days=45)).isoformat() + "Z"
    very_recent_date = (now - timedelta(days=1)).isoformat() + "Z"
    month_old = (now - timedelta(days=29)).isoformat() + "Z"

    # ===== Layer 1: Input/Output Validation Tests =====

    # Standard refund requests
    add_test(
        "I would like a refund for my order",
        "ORD001",
        50.0,
        recent_date,
        "defective_product",
        "refund_request",
        "approved",
        tags=["layer1", "standard"]
    )

    add_test(
        "Can I get my money back?",
        "ORD002",
        100.0,
        recent_date,
        "not_as_described",
        "refund_request",
        "approved",
        tags=["layer1", "standard"]
    )

    # Return request (different intent)
    add_test(
        "I want to return this item",
        "ORD003",
        75.0,
        recent_date,
        "wrong_item",
        "return_request",
        "approved",
        tags=["layer1", "intent_variation"]
    )

    # Cancellation request
    add_test(
        "Please cancel my order",
        "ORD004",
        200.0,
        very_recent_date,
        "changed_mind",
        "cancellation_request",
        "approved",
        tags=["layer1", "intent_variation"]
    )

    # Entity extraction tests
    add_test(
        "Refund please",
        "ORD005",
        150.0,
        recent_date,
        "defective",
        "refund_request",
        "approved",
        tags=["layer1", "entity_extraction"],
        entities={"order_id": "ORD005", "amount": 150.0}
    )

    # ===== Layer 2: Model Performance Tests =====

    # Decision accuracy tests
    add_test(
        "I need a refund",
        "ORD010",
        300.0,
        recent_date,
        "not_satisfied",
        "refund_request",
        "approved",
        tags=["layer2", "decision_accuracy"]
    )

    add_test(
        "Refund my purchase",
        "ORD011",
        450.0,
        recent_date,
        "poor_quality",
        "refund_request",
        "approved",
        tags=["layer2", "decision_accuracy"]
    )

    # Hallucination detection tests
    add_test(
        "I want a refund",
        "ORD012",
        100.0,
        recent_date,
        "defective",
        "refund_request",
        "approved",
        tags=["layer2", "hallucination_detection"],
        hallucination_expected=False
    )

    # ===== Layer 3: System Integration Tests =====

    # API latency tests (small amounts for quick processing)
    for i in range(5):
        add_test(
            f"Refund request {i+1}",
            f"ORD020{i}",
            50.0 + i * 10,
            recent_date,
            "defective",
            "refund_request",
            "approved",
            tags=["layer3", "latency_test"]
        )

    # Transaction success tests
    add_test(
        "Process my refund",
        "ORD025",
        200.0,
        recent_date,
        "defective",
        "refund_request",
        "approved",
        tags=["layer3", "transaction_success"]
    )

    # ===== Layer 4: Business Logic Tests =====

    # Policy compliance - within limits
    add_test(
        "I need a refund",
        "ORD030",
        500.0,  # At limit
        recent_date,
        "defective",
        "refund_request",
        "approved",
        tags=["layer4", "policy_compliance", "at_limit"]
    )

    # Policy compliance - exceeds limit
    add_test(
        "Refund my order",
        "ORD031",
        600.0,  # Above limit
        recent_date,
        "defective",
        "refund_request",
        "denied",
        tags=["layer4", "policy_compliance", "exceeds_limit"]
    )

    # Policy compliance - exceeds refund window
    add_test(
        "I want my money back",
        "ORD032",
        100.0,
        old_date,  # Too old
        "not_satisfied",
        "refund_request",
        "denied",
        tags=["layer4", "policy_compliance", "expired"]
    )

    # Edge cases
    add_test(
        "Refund please",
        None,  # Missing order ID
        100.0,
        recent_date,
        "defective",
        "refund_request",
        "denied",
        tags=["layer4", "edge_case", "missing_data"]
    )

    add_test(
        "Process refund",
        "ORD034",
        0.0,  # Zero amount
        recent_date,
        "mistake",
        "refund_request",
        "denied",
        tags=["layer4", "edge_case", "zero_amount"]
    )

    add_test(
        "Refund my purchase",
        "ORD035",
        -50.0,  # Negative amount
        recent_date,
        "error",
        "refund_request",
        "denied",
        tags=["layer4", "edge_case", "negative_amount"]
    )

    # Escalation case
    add_test(
        "I need a refund for this expensive item",
        "ORD036",
        1500.0,  # Above escalation threshold
        recent_date,
        "defective",
        "refund_request",
        "escalated",
        tags=["layer4", "edge_case", "escalation"]
    )

    # At boundary of refund window (29 days)
    add_test(
        "Refund request",
        "ORD037",
        100.0,
        month_old,
        "defective",
        "refund_request",
        "approved",
        tags=["layer4", "edge_case", "boundary_condition"]
    )

    # ===== Layer 5: Fairness & Compliance Tests =====

    # Demographic parity tests - Group A
    demographics_a = {"age_group": "25-35", "region": "north"}
    add_test(
        "I want a refund",
        "ORD040",
        200.0,
        recent_date,
        "not_satisfied",
        "refund_request",
        "approved",
        tags=["layer5", "fairness", "group_a"],
        demographics=demographics_a
    )

    add_test(
        "Refund please",
        "ORD041",
        250.0,
        recent_date,
        "defective",
        "refund_request",
        "approved",
        tags=["layer5", "fairness", "group_a"],
        demographics=demographics_a
    )

    # Demographic parity tests - Group B
    demographics_b = {"age_group": "45-55", "region": "south"}
    add_test(
        "I want a refund",
        "ORD042",
        200.0,
        recent_date,
        "not_satisfied",
        "refund_request",
        "approved",
        tags=["layer5", "fairness", "group_b"],
        demographics=demographics_b
    )

    add_test(
        "Refund please",
        "ORD043",
        250.0,
        recent_date,
        "defective",
        "refund_request",
        "approved",
        tags=["layer5", "fairness", "group_b"],
        demographics=demographics_b
    )

    # Audit trail tests
    for i in range(5):
        add_test(
            f"Refund order {i+1}",
            f"ORD050{i}",
            100.0 + i * 20,
            recent_date,
            "defective",
            "refund_request",
            "approved",
            tags=["layer5", "audit_trail"]
        )

    # ===== Additional Mixed Tests =====

    # High value approved requests
    add_test(
        "I need a refund",
        "ORD060",
        499.0,
        recent_date,
        "defective",
        "refund_request",
        "approved",
        tags=["standard", "high_value"]
    )

    # Multiple reasons
    add_test(
        "Refund - product damaged and wrong color",
        "ORD061",
        150.0,
        recent_date,
        "damaged_and_wrong",
        "refund_request",
        "approved",
        tags=["standard"]
    )

    # Urgent request
    add_test(
        "URGENT: Need immediate refund",
        "ORD062",
        300.0,
        recent_date,
        "urgent_need",
        "refund_request",
        "approved",
        tags=["standard", "urgent"]
    )

    # Polite request
    add_test(
        "Hello, I would kindly request a refund for my order. Thank you.",
        "ORD063",
        125.0,
        recent_date,
        "not_satisfied",
        "refund_request",
        "approved",
        tags=["standard", "polite"]
    )

    # Short request
    add_test(
        "Refund",
        "ORD064",
        80.0,
        recent_date,
        "defective",
        "refund_request",
        "approved",
        tags=["standard", "short"]
    )

    # Detailed request
    add_test(
        "I purchased this item 3 days ago and it arrived damaged. The box was crushed and the product doesn't work. I would like a full refund please.",
        "ORD065",
        175.0,
        recent_date,
        "damaged_in_shipping",
        "refund_request",
        "approved",
        tags=["standard", "detailed"]
    )

    return test_cases


if __name__ == "__main__":
    test_cases = generate_test_cases()

    # Save to JSON file
    with open("test_cases.json", "w") as f:
        json.dump(test_cases, f, indent=2)

    print(f"Generated {len(test_cases)} test cases")

    # Print summary by layer
    layer_counts = {}
    for test in test_cases:
        for tag in test["tags"]:
            if tag.startswith("layer"):
                layer_counts[tag] = layer_counts.get(tag, 0) + 1

    print("\nTest cases by layer:")
    for layer in sorted(layer_counts.keys()):
        print(f"  {layer}: {layer_counts[layer]} tests")
