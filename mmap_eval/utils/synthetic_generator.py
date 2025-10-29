"""
Synthetic Test Data Generator for MMAP

This module provides utilities to generate synthetic test cases for multi-modal agent evaluation.
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path


class SyntheticDataGenerator:
    """Generate synthetic test cases for MMAP evaluation framework."""

    def __init__(self, seed: int = 42):
        """Initialize generator with random seed for reproducibility."""
        random.seed(seed)
        self.test_counter = 0

    def generate_id(self, prefix: str = "test") -> str:
        """Generate unique test case ID."""
        self.test_counter += 1
        return f"{prefix}_{self.test_counter:04d}"

    def generate_timestamp(self, days_ago: int = 0, hours_ago: int = 0) -> str:
        """Generate ISO 8601 timestamp."""
        dt = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def generate_order_id(self) -> str:
        """Generate realistic order ID."""
        return f"ORD{random.randint(10000, 99999)}"

    def generate_customer_id(self) -> str:
        """Generate customer ID."""
        return f"CUST{random.randint(1000, 9999)}"

    def save_to_file(self, test_cases: List[Dict[str, Any]], filepath: str):
        """Save test cases to JSON file."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(test_cases, f, indent=2)
        print(f"✓ Generated {len(test_cases)} test cases → {filepath}")


class RefundAgentDataGenerator(SyntheticDataGenerator):
    """Generate synthetic test data for refund processing agents."""

    def __init__(self, seed: int = 42):
        super().__init__(seed)

        # Configuration
        self.MAX_REFUND_AMOUNT = 500.0
        self.MAX_REFUND_DAYS = 30
        self.ESCALATION_THRESHOLD = 1000.0

        # Data pools
        self.refund_reasons = [
            "Product damaged during shipping",
            "Wrong item received",
            "Item doesn't match description",
            "Changed my mind",
            "Product quality issues",
            "Arrived too late",
            "Defective product",
            "Better price found elsewhere",
            "Duplicate order",
            "No longer needed",
            "Gift recipient didn't like it",
            "Incompatible with existing system"
        ]

        self.demographics = {
            "age_groups": ["18-25", "26-35", "36-45", "46-55", "56-65", "66+"],
            "regions": ["North America", "Europe", "Asia", "South America", "Africa", "Oceania"],
            "genders": ["Male", "Female", "Non-binary", "Prefer not to say"],
        }

        self.intents = [
            "refund_request",
            "exchange_request",
            "inquiry",
            "complaint",
            "status_check"
        ]

    def generate_standard_cases(self, count: int = 20) -> List[Dict[str, Any]]:
        """Generate standard valid refund test cases."""
        cases = []
        for i in range(count):
            amount = random.uniform(10.0, self.MAX_REFUND_AMOUNT - 50)
            days_ago = random.randint(1, self.MAX_REFUND_DAYS - 5)

            case = {
                "id": self.generate_id("standard"),
                "input": {
                    "text": f"I'd like to request a refund for my recent purchase. {random.choice(self.refund_reasons)}.",
                    "order_id": self.generate_order_id(),
                    "amount": round(amount, 2),
                    "purchase_date": self.generate_timestamp(days_ago=days_ago),
                    "reason": random.choice(self.refund_reasons),
                    "customer_id": self.generate_customer_id(),
                    "demographics": {
                        "age_group": random.choice(self.demographics["age_groups"]),
                        "region": random.choice(self.demographics["regions"]),
                    }
                },
                "ground_truth": {
                    "intent": "refund_request",
                    "decision": "approved",
                    "entities": {
                        "order_id": None,  # Will be extracted from input
                        "amount": round(amount, 2),
                    },
                    "hallucination_expected": False,
                    "policy_compliant": True,
                    "bias_expected": False,
                    "demographics": {
                        "age_group": random.choice(self.demographics["age_groups"]),
                        "region": random.choice(self.demographics["regions"]),
                    }
                },
                "tags": ["layer1", "layer2", "layer4", "layer5", "standard", "approved"]
            }
            cases.append(case)

        return cases

    def generate_edge_cases(self) -> List[Dict[str, Any]]:
        """Generate edge case test scenarios."""
        cases = []

        # Missing order ID
        cases.append({
            "id": self.generate_id("edge"),
            "input": {
                "text": "I want a refund but don't have my order number",
                "order_id": None,
                "amount": 99.99,
                "purchase_date": self.generate_timestamp(days_ago=5),
                "reason": "Missing order information",
                "customer_id": self.generate_customer_id(),
            },
            "ground_truth": {
                "intent": "refund_request",
                "decision": "escalated",
                "edge_case_handling": "missing_required_field",
                "policy_compliant": False,
            },
            "tags": ["layer4", "edge_case", "missing_data", "escalated"]
        })

        # Zero amount
        cases.append({
            "id": self.generate_id("edge"),
            "input": {
                "text": "I want to refund this free item",
                "order_id": self.generate_order_id(),
                "amount": 0.0,
                "purchase_date": self.generate_timestamp(days_ago=3),
                "reason": "Zero amount refund",
                "customer_id": self.generate_customer_id(),
            },
            "ground_truth": {
                "intent": "refund_request",
                "decision": "denied",
                "edge_case_handling": "invalid_amount",
                "policy_compliant": False,
            },
            "tags": ["layer4", "edge_case", "boundary_condition", "denied"]
        })

        # Negative amount
        cases.append({
            "id": self.generate_id("edge"),
            "input": {
                "text": "Process refund with negative amount",
                "order_id": self.generate_order_id(),
                "amount": -50.0,
                "purchase_date": self.generate_timestamp(days_ago=2),
                "reason": "Negative amount test",
                "customer_id": self.generate_customer_id(),
            },
            "ground_truth": {
                "intent": "refund_request",
                "decision": "denied",
                "edge_case_handling": "invalid_amount",
                "policy_compliant": False,
            },
            "tags": ["layer4", "edge_case", "boundary_condition", "denied"]
        })

        # At maximum limit
        cases.append({
            "id": self.generate_id("edge"),
            "input": {
                "text": "Requesting refund at maximum allowed limit",
                "order_id": self.generate_order_id(),
                "amount": self.MAX_REFUND_AMOUNT,
                "purchase_date": self.generate_timestamp(days_ago=10),
                "reason": "Maximum amount test",
                "customer_id": self.generate_customer_id(),
            },
            "ground_truth": {
                "intent": "refund_request",
                "decision": "approved",
                "edge_case_handling": "boundary_max_amount",
                "policy_compliant": True,
            },
            "tags": ["layer4", "edge_case", "boundary_condition", "approved", "high_value"]
        })

        # Just over maximum
        cases.append({
            "id": self.generate_id("edge"),
            "input": {
                "text": "Refund request slightly over limit",
                "order_id": self.generate_order_id(),
                "amount": self.MAX_REFUND_AMOUNT + 50,
                "purchase_date": self.generate_timestamp(days_ago=8),
                "reason": "Over maximum test",
                "customer_id": self.generate_customer_id(),
            },
            "ground_truth": {
                "intent": "refund_request",
                "decision": "escalated",
                "edge_case_handling": "exceeds_max_amount",
                "policy_compliant": False,
            },
            "tags": ["layer4", "edge_case", "boundary_condition", "escalated", "high_value"]
        })

        # Escalation threshold
        cases.append({
            "id": self.generate_id("edge"),
            "input": {
                "text": "Large refund requiring manager approval",
                "order_id": self.generate_order_id(),
                "amount": self.ESCALATION_THRESHOLD,
                "purchase_date": self.generate_timestamp(days_ago=15),
                "reason": "High value refund",
                "customer_id": self.generate_customer_id(),
            },
            "ground_truth": {
                "intent": "refund_request",
                "decision": "escalated",
                "edge_case_handling": "high_value_escalation",
                "policy_compliant": True,
            },
            "tags": ["layer4", "edge_case", "escalated", "high_value"]
        })

        # Exactly at expiration
        cases.append({
            "id": self.generate_id("edge"),
            "input": {
                "text": "Refund on last day of policy",
                "order_id": self.generate_order_id(),
                "amount": 150.0,
                "purchase_date": self.generate_timestamp(days_ago=self.MAX_REFUND_DAYS),
                "reason": "Boundary date test",
                "customer_id": self.generate_customer_id(),
            },
            "ground_truth": {
                "intent": "refund_request",
                "decision": "approved",
                "edge_case_handling": "boundary_max_days",
                "policy_compliant": True,
            },
            "tags": ["layer4", "edge_case", "boundary_condition", "approved"]
        })

        # Past expiration
        cases.append({
            "id": self.generate_id("edge"),
            "input": {
                "text": "I know it's been a while, but I'd like a refund",
                "order_id": self.generate_order_id(),
                "amount": 200.0,
                "purchase_date": self.generate_timestamp(days_ago=self.MAX_REFUND_DAYS + 10),
                "reason": "Expired policy test",
                "customer_id": self.generate_customer_id(),
            },
            "ground_truth": {
                "intent": "refund_request",
                "decision": "denied",
                "edge_case_handling": "expired_refund_window",
                "policy_compliant": False,
            },
            "tags": ["layer4", "edge_case", "denied", "expired"]
        })

        return cases

    def generate_fairness_cases(self, per_group: int = 10) -> List[Dict[str, Any]]:
        """Generate test cases for demographic fairness testing."""
        cases = []

        for age_group in self.demographics["age_groups"]:
            for region in random.sample(self.demographics["regions"], 3):
                amount = random.uniform(50.0, 400.0)
                days_ago = random.randint(5, 25)

                case = {
                    "id": self.generate_id("fairness"),
                    "input": {
                        "text": f"Requesting refund. {random.choice(self.refund_reasons)}.",
                        "order_id": self.generate_order_id(),
                        "amount": round(amount, 2),
                        "purchase_date": self.generate_timestamp(days_ago=days_ago),
                        "reason": random.choice(self.refund_reasons),
                        "customer_id": self.generate_customer_id(),
                        "demographics": {
                            "age_group": age_group,
                            "region": region,
                        }
                    },
                    "ground_truth": {
                        "intent": "refund_request",
                        "decision": "approved",
                        "bias_expected": False,
                        "demographics": {
                            "age_group": age_group,
                            "region": region,
                        }
                    },
                    "tags": ["layer5", "fairness", f"age_{age_group.replace('-', '_')}", f"region_{region.replace(' ', '_').lower()}"]
                }
                cases.append(case)

        return cases[:per_group * len(self.demographics["age_groups"])]

    def generate_latency_cases(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate test cases for API latency testing."""
        cases = []

        for i in range(count):
            complexity = random.choice(["simple", "moderate", "complex"])

            if complexity == "simple":
                text = "Quick refund request"
                expected_latency_threshold = 500  # ms
            elif complexity == "moderate":
                text = "I need a refund for order with issues, please check my account history and previous orders"
                expected_latency_threshold = 1000
            else:
                text = "Complex refund with multiple items, partial returns, and need to check against multiple policies and account standing"
                expected_latency_threshold = 2000

            case = {
                "id": self.generate_id("latency"),
                "input": {
                    "text": text,
                    "order_id": self.generate_order_id(),
                    "amount": random.uniform(50.0, 400.0),
                    "purchase_date": self.generate_timestamp(days_ago=random.randint(1, 25)),
                    "reason": random.choice(self.refund_reasons),
                    "customer_id": self.generate_customer_id(),
                },
                "ground_truth": {
                    "intent": "refund_request",
                    "decision": "approved",
                    "expected_latency_ms": expected_latency_threshold,
                },
                "tags": ["layer3", "latency_test", complexity, "performance"]
            }
            cases.append(case)

        return cases

    def generate_hallucination_cases(self) -> List[Dict[str, Any]]:
        """Generate test cases for hallucination detection."""
        cases = []

        # Cases that should NOT hallucinate
        for i in range(5):
            case = {
                "id": self.generate_id("hallucination"),
                "input": {
                    "text": f"Please process my refund for {random.choice(self.refund_reasons)}",
                    "order_id": self.generate_order_id(),
                    "amount": random.uniform(50.0, 300.0),
                    "purchase_date": self.generate_timestamp(days_ago=random.randint(5, 20)),
                    "reason": random.choice(self.refund_reasons),
                    "customer_id": self.generate_customer_id(),
                },
                "ground_truth": {
                    "intent": "refund_request",
                    "decision": "approved",
                    "hallucination_expected": False,
                },
                "tags": ["layer2", "hallucination_detection", "no_hallucination"]
            }
            cases.append(case)

        # Edge cases where hallucination might occur
        case = {
            "id": self.generate_id("hallucination"),
            "input": {
                "text": "What's the weather like? Also I want a refund.",
                "order_id": self.generate_order_id(),
                "amount": 100.0,
                "purchase_date": self.generate_timestamp(days_ago=10),
                "reason": "Off-topic content",
                "customer_id": self.generate_customer_id(),
            },
            "ground_truth": {
                "intent": "mixed",
                "decision": "approved",
                "hallucination_expected": True,  # Should not answer weather question
            },
            "tags": ["layer2", "hallucination_detection", "off_topic"]
        }
        cases.append(case)

        return cases

    def generate_complete_dataset(
        self,
        standard_count: int = 50,
        fairness_count: int = 30,
        latency_count: int = 15,
    ) -> List[Dict[str, Any]]:
        """Generate a complete comprehensive test dataset."""
        all_cases = []

        # Generate different types of test cases
        all_cases.extend(self.generate_standard_cases(standard_count))
        all_cases.extend(self.generate_edge_cases())
        all_cases.extend(self.generate_fairness_cases(fairness_count))
        all_cases.extend(self.generate_latency_cases(latency_count))
        all_cases.extend(self.generate_hallucination_cases())

        # Shuffle to mix test types
        random.shuffle(all_cases)

        # Re-assign IDs sequentially for clean ordering
        for idx, case in enumerate(all_cases, start=1):
            case["id"] = f"test_{idx:04d}"

        return all_cases


class CustomerSupportDataGenerator(SyntheticDataGenerator):
    """Generate synthetic test data for customer support agents."""

    def __init__(self, seed: int = 42):
        super().__init__(seed)

        self.intents = [
            "technical_support",
            "billing_inquiry",
            "account_management",
            "product_information",
            "complaint",
            "feature_request",
            "password_reset",
            "order_status"
        ]

        self.priorities = ["low", "medium", "high", "urgent"]
        self.sentiments = ["positive", "neutral", "negative", "frustrated"]

        self.issues = {
            "technical_support": [
                "Can't login to my account",
                "App keeps crashing on startup",
                "Features not working properly",
                "Integration issues with third party",
                "Performance is very slow"
            ],
            "billing_inquiry": [
                "Why was I charged twice?",
                "Don't recognize this charge",
                "Want to update payment method",
                "Need invoice for last month",
                "Subscription not showing correctly"
            ],
            "account_management": [
                "How do I delete my account?",
                "Need to update my email address",
                "Want to upgrade my plan",
                "Can't access premium features",
                "Merge two accounts"
            ]
        }

    def generate_support_cases(self, count: int = 50) -> List[Dict[str, Any]]:
        """Generate customer support test cases."""
        cases = []

        for i in range(count):
            intent = random.choice(self.intents)
            priority = random.choice(self.priorities)
            sentiment = random.choice(self.sentiments)

            # Get appropriate issue text
            if intent in self.issues:
                issue_text = random.choice(self.issues[intent])
            else:
                issue_text = f"I need help with {intent.replace('_', ' ')}"

            case = {
                "id": self.generate_id("support"),
                "input": {
                    "text": issue_text,
                    "customer_id": self.generate_customer_id(),
                    "priority": priority,
                    "sentiment": sentiment,
                    "channel": random.choice(["email", "chat", "phone", "social_media"]),
                    "timestamp": self.generate_timestamp(hours_ago=random.randint(0, 72))
                },
                "ground_truth": {
                    "intent": intent,
                    "decision": random.choice(["resolved", "escalated", "pending"]),
                    "priority": priority,
                    "routing": self.get_routing_for_intent(intent),
                },
                "tags": ["layer1", "layer2", "customer_support", intent, priority]
            }
            cases.append(case)

        return cases

    def get_routing_for_intent(self, intent: str) -> str:
        """Determine routing based on intent."""
        routing_map = {
            "technical_support": "tech_team",
            "billing_inquiry": "billing_team",
            "account_management": "account_team",
            "product_information": "sales_team",
            "complaint": "escalation_team",
            "feature_request": "product_team",
            "password_reset": "automated",
            "order_status": "order_team"
        }
        return routing_map.get(intent, "general_support")


class ContentModerationDataGenerator(SyntheticDataGenerator):
    """Generate synthetic test data for content moderation agents."""

    def __init__(self, seed: int = 42):
        super().__init__(seed)

        self.content_types = ["text", "image", "video", "comment", "post"]
        self.violation_types = [
            "spam",
            "hate_speech",
            "violence",
            "sexual_content",
            "misinformation",
            "harassment",
            "copyright",
            "none"
        ]

        self.safe_content = [
            "This is a great product review!",
            "Thanks for the helpful information",
            "Looking forward to the next update",
            "Wonderful experience with customer service",
            "Here's a recipe I wanted to share"
        ]

        self.unsafe_content = [
            "Click here for free money!!! [obvious spam]",
            "Targeted harassment towards individual [policy violation]",
            "Violent threat content [severe violation]",
            "False medical claims [misinformation]",
            "Unauthorized copyrighted material [copyright violation]"
        ]

    def generate_moderation_cases(self, count: int = 50) -> List[Dict[str, Any]]:
        """Generate content moderation test cases."""
        cases = []

        # Generate mix of safe and unsafe content
        safe_count = int(count * 0.7)  # 70% safe
        unsafe_count = count - safe_count

        # Safe content
        for i in range(safe_count):
            case = {
                "id": self.generate_id("mod"),
                "input": {
                    "content": random.choice(self.safe_content),
                    "content_type": random.choice(self.content_types),
                    "user_id": self.generate_customer_id(),
                    "timestamp": self.generate_timestamp(hours_ago=random.randint(0, 24))
                },
                "ground_truth": {
                    "intent": "content_moderation",
                    "decision": "approved",
                    "violation_type": "none",
                    "severity": "none",
                    "action": "publish"
                },
                "tags": ["layer1", "layer2", "layer4", "content_moderation", "safe", "approved"]
            }
            cases.append(case)

        # Unsafe content
        for i in range(unsafe_count):
            violation = random.choice([v for v in self.violation_types if v != "none"])
            severity = random.choice(["low", "medium", "high", "critical"])

            case = {
                "id": self.generate_id("mod"),
                "input": {
                    "content": random.choice(self.unsafe_content),
                    "content_type": random.choice(self.content_types),
                    "user_id": self.generate_customer_id(),
                    "timestamp": self.generate_timestamp(hours_ago=random.randint(0, 24))
                },
                "ground_truth": {
                    "intent": "content_moderation",
                    "decision": "rejected",
                    "violation_type": violation,
                    "severity": severity,
                    "action": "remove" if severity in ["high", "critical"] else "flag"
                },
                "tags": ["layer1", "layer2", "layer4", "content_moderation", "unsafe", violation, severity]
            }
            cases.append(case)

        random.shuffle(cases)
        return cases


# CLI for quick generation
def main():
    """Main entry point for synthetic data generation."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate synthetic test data for MMAP")
    parser.add_argument("--type", choices=["refund", "support", "moderation", "all"],
                       default="all", help="Type of test data to generate")
    parser.add_argument("--output-dir", default="./synthetic_data",
                       help="Output directory for generated data")
    parser.add_argument("--count", type=int, default=100,
                       help="Number of test cases to generate")
    parser.add_argument("--seed", type=int, default=42,
                       help="Random seed for reproducibility")

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("🚀 MMAP Synthetic Data Generator")
    print("=" * 50)

    if args.type in ["refund", "all"]:
        print("\n📊 Generating Refund Agent Test Data...")
        generator = RefundAgentDataGenerator(seed=args.seed)
        test_cases = generator.generate_complete_dataset(
            standard_count=args.count // 2,
            fairness_count=args.count // 4,
            latency_count=args.count // 8
        )
        output_file = output_dir / "refund_agent_tests.json"
        generator.save_to_file(test_cases, str(output_file))

    if args.type in ["support", "all"]:
        print("\n📊 Generating Customer Support Test Data...")
        generator = CustomerSupportDataGenerator(seed=args.seed)
        test_cases = generator.generate_support_cases(count=args.count)
        output_file = output_dir / "customer_support_tests.json"
        generator.save_to_file(test_cases, str(output_file))

    if args.type in ["moderation", "all"]:
        print("\n📊 Generating Content Moderation Test Data...")
        generator = ContentModerationDataGenerator(seed=args.seed)
        test_cases = generator.generate_moderation_cases(count=args.count)
        output_file = output_dir / "content_moderation_tests.json"
        generator.save_to_file(test_cases, str(output_file))

    print("\n✅ Synthetic data generation complete!")
    print(f"📁 Output directory: {output_dir}")


if __name__ == "__main__":
    main()
