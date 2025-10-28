"""Pre-built metrics for MMAP evaluation."""

from mmap_eval.metrics.layer1.entity_extraction import EntityExtractionAccuracy
from mmap_eval.metrics.layer1.intent_accuracy import IntentAccuracy
from mmap_eval.metrics.layer2.decision_accuracy import DecisionAccuracy
from mmap_eval.metrics.layer2.hallucination_detection import HallucinationDetection
from mmap_eval.metrics.layer3.api_latency import APILatency
from mmap_eval.metrics.layer3.transaction_success import TransactionSuccess
from mmap_eval.metrics.layer4.edge_case_handling import EdgeCaseHandling
from mmap_eval.metrics.layer4.policy_compliance import PolicyCompliance
from mmap_eval.metrics.layer5.audit_trail import AuditTrail
from mmap_eval.metrics.layer5.demographic_parity import DemographicParity

__all__ = [
    # Layer 1: Input/Output Validation
    "IntentAccuracy",
    "EntityExtractionAccuracy",
    # Layer 2: Model Performance
    "DecisionAccuracy",
    "HallucinationDetection",
    # Layer 3: System Integration
    "APILatency",
    "TransactionSuccess",
    # Layer 4: Business Logic
    "PolicyCompliance",
    "EdgeCaseHandling",
    # Layer 5: Fairness & Compliance
    "DemographicParity",
    "AuditTrail",
]
