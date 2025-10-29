"""
Example Content Moderation Agent for MMAP Evaluation

This is a mock implementation demonstrating how to structure a
content moderation agent for evaluation with MMAP.
"""

import time
from typing import Dict, Any, List


class ContentModerationAgent:
    """
    Mock content moderation agent that classifies and moderates content.

    In a real implementation, this would integrate with ML models,
    LLMs, or moderation APIs for actual content analysis.
    """

    def __init__(self):
        """Initialize the content moderation agent."""
        self.name = "ContentModerationAgent"

        # Violation detection patterns (simplified for mock)
        self.violation_keywords = {
            "spam": ["free money", "click here", "limited time", "act now", "!!!"],
            "hate_speech": ["hate", "discriminatory", "targeted harassment"],
            "violence": ["violent", "threat", "harm", "attack"],
            "sexual_content": ["explicit", "nsfw", "inappropriate"],
            "misinformation": ["false", "fake", "misleading claims", "unverified"],
            "harassment": ["harassment", "bullying", "targeted", "abuse"],
            "copyright": ["copyrighted", "unauthorized", "stolen content", "pirated"]
        }

        # Severity scoring
        self.severity_weights = {
            "spam": 1,
            "harassment": 2,
            "sexual_content": 3,
            "misinformation": 2,
            "copyright": 2,
            "hate_speech": 4,
            "violence": 4
        }

    def detect_violations(self, content: str) -> List[str]:
        """
        Detect policy violations in content.

        In production, this would use ML models, LLMs, or moderation APIs.
        For this mock, we use simple keyword matching.
        """
        content_lower = content.lower()
        detected_violations = []

        for violation_type, keywords in self.violation_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                detected_violations.append(violation_type)

        return detected_violations if detected_violations else ["none"]

    def calculate_severity(self, violations: List[str]) -> str:
        """Calculate severity level based on detected violations."""
        if violations == ["none"]:
            return "none"

        # Calculate weighted severity
        max_weight = max(
            self.severity_weights.get(v, 1) for v in violations if v != "none"
        )

        if max_weight >= 4:
            return "critical"
        elif max_weight == 3:
            return "high"
        elif max_weight == 2:
            return "medium"
        else:
            return "low"

    def determine_action(self, violations: List[str], severity: str) -> str:
        """Determine moderation action based on violations and severity."""
        if violations == ["none"]:
            return "publish"

        if severity in ["critical", "high"]:
            return "remove"
        elif severity == "medium":
            return "flag"
        else:
            return "flag"

    def determine_decision(self, violations: List[str]) -> str:
        """Determine if content should be approved or rejected."""
        if violations == ["none"]:
            return "approved"
        else:
            return "rejected"

    def process(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process content for moderation.

        Args:
            test_case: Test case from MMAP evaluation dataset

        Returns:
            Agent output dict with all fields needed for metric evaluation
        """
        start_time = time.time()

        # Extract input data
        input_data = test_case["input"]
        content = input_data.get("content", "")
        content_type = input_data.get("content_type", "text")
        user_id = input_data.get("user_id", "unknown")

        # Detect violations
        violations = self.detect_violations(content)
        primary_violation = violations[0] if violations else "none"

        # Calculate severity
        severity = self.calculate_severity(violations)

        # Determine action
        action = self.determine_action(violations, severity)

        # Determine decision
        decision = self.determine_decision(violations)

        # Simulate processing time (content moderation can be fast)
        time.sleep(0.05)  # 50ms

        # Calculate latency
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000

        # Generate explanation
        explanation = self._generate_explanation(violations, severity, action)

        # Build output
        output = {
            "intent": "content_moderation",
            "decision": decision,
            "violation_type": primary_violation,
            "all_violations": violations,
            "severity": severity,
            "action": action,
            "explanation": explanation,
            "content_type": content_type,
            "response": explanation,
            "latency_ms": latency_ms,
            "success": True,
            "error": None,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "audit_trail": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "action": "content_moderated",
                "decision": decision,
                "violation_type": primary_violation,
                "severity": severity,
                "moderation_action": action,
                "user_id": user_id,
                "content_type": content_type
            }
        }

        return output

    def _generate_explanation(
        self,
        violations: List[str],
        severity: str,
        action: str
    ) -> str:
        """Generate human-readable explanation for moderation decision."""
        if violations == ["none"]:
            return "Content approved - no policy violations detected."

        violation_str = ", ".join(violations)
        return (
            f"Content flagged for: {violation_str}. "
            f"Severity: {severity}. "
            f"Action taken: {action}."
        )


# For direct testing
if __name__ == "__main__":
    agent = ContentModerationAgent()

    # Test case 1: Safe content
    test_safe = {
        "input": {
            "content": "This is a great product review!",
            "content_type": "comment",
            "user_id": "CUST1234",
            "timestamp": "2025-10-29T10:00:00Z"
        }
    }

    print("Test 1: Safe Content")
    result = agent.process(test_safe)
    print(f"  Decision: {result['decision']}")
    print(f"  Action: {result['action']}")
    print(f"  Explanation: {result['explanation']}")
    print()

    # Test case 2: Spam content
    test_spam = {
        "input": {
            "content": "Click here for free money!!! Limited time offer!!!",
            "content_type": "post",
            "user_id": "CUST5678",
            "timestamp": "2025-10-29T10:05:00Z"
        }
    }

    print("Test 2: Spam Content")
    result = agent.process(test_spam)
    print(f"  Decision: {result['decision']}")
    print(f"  Violation: {result['violation_type']}")
    print(f"  Severity: {result['severity']}")
    print(f"  Action: {result['action']}")
    print(f"  Explanation: {result['explanation']}")
    print()

    # Test case 3: Severe violation
    test_severe = {
        "input": {
            "content": "Violent threat content with hate speech",
            "content_type": "comment",
            "user_id": "CUST9999",
            "timestamp": "2025-10-29T10:10:00Z"
        }
    }

    print("Test 3: Severe Violation")
    result = agent.process(test_severe)
    print(f"  Decision: {result['decision']}")
    print(f"  Violations: {result['all_violations']}")
    print(f"  Severity: {result['severity']}")
    print(f"  Action: {result['action']}")
    print(f"  Explanation: {result['explanation']}")
