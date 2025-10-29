"""
Example Customer Support Agent for MMAP Evaluation

This is a mock implementation demonstrating how to structure an agent
for evaluation with MMAP using synthetic customer support data.
"""

import time
from typing import Dict, Any


class CustomerSupportAgent:
    """
    Mock customer support agent that processes support requests.

    In a real implementation, this would integrate with your actual
    agent system (LangChain, LlamaIndex, custom LLM, etc.).
    """

    def __init__(self):
        """Initialize the customer support agent."""
        self.name = "CustomerSupportAgent"

        # Intent routing configuration
        self.intent_routing = {
            "technical_support": "tech_team",
            "billing_inquiry": "billing_team",
            "account_management": "account_team",
            "product_information": "sales_team",
            "complaint": "escalation_team",
            "feature_request": "product_team",
            "password_reset": "automated",
            "order_status": "order_team"
        }

        # Priority-based response times (ms)
        self.response_times = {
            "urgent": 100,
            "high": 200,
            "medium": 300,
            "low": 400
        }

    def classify_intent(self, text: str) -> str:
        """
        Classify the intent of a customer support request.

        In production, this would use NLP/LLM for classification.
        For this mock, we use simple keyword matching.
        """
        text_lower = text.lower()

        # Simple keyword-based classification
        if any(word in text_lower for word in ["login", "crash", "not working", "slow", "error"]):
            return "technical_support"
        elif any(word in text_lower for word in ["charge", "bill", "payment", "invoice"]):
            return "billing_inquiry"
        elif any(word in text_lower for word in ["account", "email", "upgrade", "delete", "merge"]):
            return "account_management"
        elif any(word in text_lower for word in ["product", "feature", "how to", "information"]):
            return "product_information"
        elif any(word in text_lower for word in ["unhappy", "disappointed", "terrible", "worst"]):
            return "complaint"
        elif any(word in text_lower for word in ["request", "add", "would be great"]):
            return "feature_request"
        elif any(word in text_lower for word in ["password", "reset", "forgot", "can't access"]):
            return "password_reset"
        elif any(word in text_lower for word in ["order", "status", "tracking", "delivery"]):
            return "order_status"
        else:
            return "technical_support"  # Default

    def determine_decision(self, intent: str, priority: str, sentiment: str) -> str:
        """Determine the handling decision based on case attributes."""
        # Urgent cases with negative sentiment get escalated
        if priority == "urgent" and sentiment in ["negative", "frustrated"]:
            return "escalated"

        # Password resets are automated
        if intent == "password_reset":
            return "resolved"

        # Complaints always escalate
        if intent == "complaint":
            return "escalated"

        # High priority technical issues escalate
        if intent == "technical_support" and priority == "high":
            return "escalated"

        # Most other cases can be resolved
        if priority in ["low", "medium"]:
            return "resolved"

        return "pending"

    def get_routing(self, intent: str) -> str:
        """Get the routing destination for an intent."""
        return self.intent_routing.get(intent, "general_support")

    def process(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a customer support request.

        Args:
            test_case: Test case from MMAP evaluation dataset

        Returns:
            Agent output dict with all fields needed for metric evaluation
        """
        start_time = time.time()

        # Extract input data
        input_data = test_case["input"]
        text = input_data.get("text", "")
        priority = input_data.get("priority", "medium")
        sentiment = input_data.get("sentiment", "neutral")

        # Classify intent
        intent = self.classify_intent(text)

        # Determine decision
        decision = self.determine_decision(intent, priority, sentiment)

        # Get routing
        routing = self.get_routing(intent)

        # Simulate processing time based on priority
        simulated_delay = self.response_times.get(priority, 300) / 1000.0
        time.sleep(simulated_delay)

        # Calculate latency
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000

        # Generate response
        response = self._generate_response(intent, decision, routing)

        # Build output
        output = {
            "intent": intent,
            "decision": decision,
            "priority": priority,
            "routing": routing,
            "response": response,
            "latency_ms": latency_ms,
            "success": True,
            "error": None,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "audit_trail": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "action": "support_request_processed",
                "decision": decision,
                "intent": intent,
                "routing": routing,
                "priority": priority
            }
        }

        return output

    def _generate_response(self, intent: str, decision: str, routing: str) -> str:
        """Generate a customer-facing response."""
        if decision == "escalated":
            return f"Your {intent.replace('_', ' ')} has been escalated to our {routing} for immediate attention."
        elif decision == "resolved":
            return f"Your {intent.replace('_', ' ')} has been processed and resolved by our {routing}."
        else:
            return f"Your {intent.replace('_', ' ')} is being reviewed by our {routing}."


# For direct testing
if __name__ == "__main__":
    agent = CustomerSupportAgent()

    # Test case
    test_input = {
        "input": {
            "text": "Can't login to my account",
            "customer_id": "CUST1234",
            "priority": "high",
            "sentiment": "frustrated",
            "channel": "chat",
            "timestamp": "2025-10-29T10:00:00Z"
        }
    }

    result = agent.process(test_input)

    print("Agent Output:")
    for key, value in result.items():
        print(f"  {key}: {value}")
