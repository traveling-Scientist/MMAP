"""Refund Request Agent Example.

This is a sample customer service agent that handles refund requests.
It demonstrates all 5 layers of MMAP evaluation.
"""

from datetime import datetime, timedelta
from typing import Any, Dict


class RefundAgent:
    """Customer service agent for processing refund requests."""

    # Business rules
    MAX_REFUND_AMOUNT = 500.0
    MAX_REFUND_DAYS = 30
    ESCALATION_THRESHOLD = 1000.0

    def __init__(self):
        """Initialize the refund agent."""
        self.processed_requests = []

    def process_request(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a refund request.

        Args:
            input_data: Dictionary containing:
                - text: Customer request text
                - order_id: Order identifier
                - purchase_date: Date of purchase (ISO format)
                - amount: Purchase amount
                - reason: Reason for refund
                - customer_id: Customer identifier (optional)
                - demographics: Customer demographics (optional)

        Returns:
            Dictionary containing:
                - intent: Identified intent
                - decision: Refund decision (approved/denied/escalated)
                - entities: Extracted entities
                - response: Response to customer
                - reason: Reason for decision
                - audit_trail: Audit information
                - timestamp: Processing timestamp
        """
        start_time = datetime.utcnow()

        try:
            # Step 1: Parse intent and extract entities (Layer 1)
            intent = self._extract_intent(input_data)
            entities = self._extract_entities(input_data)

            # Step 2: Make decision based on business logic (Layer 2 & 4)
            decision, reason = self._make_decision(entities)

            # Step 3: Generate response (Layer 2)
            response = self._generate_response(decision, entities, reason)

            # Step 4: Create audit trail (Layer 5)
            audit_trail = {
                "timestamp": start_time.isoformat() + "Z",
                "action": "refund_request_processed",
                "decision": decision,
                "reason": reason,
                "order_id": entities.get("order_id"),
                "amount": entities.get("amount"),
                "agent_version": "1.0",
            }

            # Store processed request
            self.processed_requests.append(audit_trail)

            # Calculate processing time (Layer 3)
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            result = {
                "intent": intent,
                "decision": decision,
                "entities": entities,
                "response": response,
                "reason": reason,
                "audit_trail": audit_trail,
                "timestamp": start_time.isoformat() + "Z",
                "latency_ms": processing_time,
                "success": True,
            }

            return result

        except Exception as e:
            # Error handling (Layer 3)
            return {
                "intent": "unknown",
                "decision": "error",
                "entities": {},
                "response": "I apologize, but I encountered an error processing your request. Please contact customer support.",
                "error": str(e),
                "success": False,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

    def _extract_intent(self, input_data: Dict[str, Any]) -> str:
        """Extract intent from input."""
        text = input_data.get("text", "").lower()

        if "refund" in text or "money back" in text:
            return "refund_request"
        elif "return" in text:
            return "return_request"
        elif "cancel" in text:
            return "cancellation_request"
        else:
            return "general_inquiry"

    def _extract_entities(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract entities from input."""
        entities = {
            "order_id": input_data.get("order_id"),
            "amount": input_data.get("amount"),
            "purchase_date": input_data.get("purchase_date"),
            "reason": input_data.get("reason"),
            "customer_id": input_data.get("customer_id"),
        }

        # Remove None values
        return {k: v for k, v in entities.items() if v is not None}

    def _make_decision(self, entities: Dict[str, Any]) -> tuple[str, str]:
        """Make refund decision based on business rules.

        Returns:
            Tuple of (decision, reason)
        """
        amount = entities.get("amount", 0)
        purchase_date_str = entities.get("purchase_date")

        # Check for missing required information
        if not entities.get("order_id"):
            return "denied", "Missing order ID"

        if amount is None or amount <= 0:
            return "denied", "Invalid amount"

        # Check if exceeds escalation threshold
        if amount > self.ESCALATION_THRESHOLD:
            return "escalated", f"Amount ${amount} exceeds escalation threshold"

        # Check refund amount limit
        if amount > self.MAX_REFUND_AMOUNT:
            return "denied", f"Amount ${amount} exceeds maximum refund limit of ${self.MAX_REFUND_AMOUNT}"

        # Check purchase date
        if purchase_date_str:
            try:
                purchase_date = datetime.fromisoformat(purchase_date_str.replace("Z", "+00:00"))
                days_since_purchase = (datetime.now(purchase_date.tzinfo) - purchase_date).days

                if days_since_purchase > self.MAX_REFUND_DAYS:
                    return "denied", f"Purchase date exceeds {self.MAX_REFUND_DAYS}-day refund window"

            except ValueError:
                return "denied", "Invalid purchase date format"

        # Approve if all checks pass
        return "approved", "Refund approved within policy guidelines"

    def _generate_response(
        self, decision: str, entities: Dict[str, Any], reason: str
    ) -> str:
        """Generate customer-facing response."""
        amount = entities.get("amount", 0)
        order_id = entities.get("order_id", "N/A")

        if decision == "approved":
            return f"Your refund of ${amount} for order {order_id} has been approved. You will receive the refund within 5-7 business days."

        elif decision == "denied":
            return f"We're unable to process your refund for order {order_id}. Reason: {reason}"

        elif decision == "escalated":
            return f"Your refund request for order {order_id} has been escalated to our specialist team. You will hear back within 24 hours."

        else:
            return "We're processing your request. Please check back later."


# Create a simple function interface for MMAP
def refund_agent(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Simple function interface for the refund agent.

    Args:
        input_data: Input data dictionary

    Returns:
        Agent output dictionary
    """
    agent = RefundAgent()
    return agent.process_request(input_data)
