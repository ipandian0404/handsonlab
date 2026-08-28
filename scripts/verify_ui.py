#!/usr/bin/env python3
"""Verify all claim decision outcomes via the JSON API."""

import json
import sys
from decimal import Decimal
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dreamguard import Claim, assess_claim

# Test payload validator (same as app.py's assess_payload)
def assess_payload(payload: dict) -> dict:
    """Convert a synthetic browser payload into a serialized claim decision."""
    try:
        claim = Claim(
            policy_number=str(payload["policy_number"]),
            claim_type=str(payload["claim_type"]),
            amount=Decimal(str(payload["amount"])),
            months_active=int(payload["months_active"]),
            documents=tuple(str(item) for item in payload["documents"]),
        )
    except (Exception,) as error:
        raise ValueError(f"Invalid claim payload: {error}") from error

    decision = assess_claim(claim)
    return {
        "status": decision.status,
        "approved_amount": str(decision.approved_amount),
        "reasons": list(decision.reasons),
    }

# Test cases from the UI
test_cases = [
    {
        "title": "✅ Approved Life Claim",
        "payload": {
            "policy_number": "POL-2001",
            "claim_type": "life",
            "amount": "250000.00",
            "months_active": 24,
            "documents": ["death_certificate", "identity_document"]
        },
        "expected_status": "approved"
    },
    {
        "title": "✅ Approved Disability Claim",
        "payload": {
            "policy_number": "POL-2002",
            "claim_type": "disability",
            "amount": "75000.00",
            "months_active": 6,
            "documents": ["medical_report", "identity_document"]
        },
        "expected_status": "approved"
    },
    {
        "title": "⏳ Pending Documents (Life)",
        "payload": {
            "policy_number": "POL-3002",
            "claim_type": "life",
            "amount": "120000.00",
            "months_active": 12,
            "documents": ["death_certificate"]
        },
        "expected_status": "pending_documents"
    },
    {
        "title": "⏳ Pending Documents (Disability)",
        "payload": {
            "policy_number": "POL-3005",
            "claim_type": "disability",
            "amount": "45000.00",
            "months_active": 12,
            "documents": ["identity_document"]
        },
        "expected_status": "pending_documents"
    },
    {
        "title": "🔄 Referred (Waiting Period)",
        "payload": {
            "policy_number": "POL-4002",
            "claim_type": "life",
            "amount": "150000.00",
            "months_active": 1,
            "documents": ["death_certificate", "identity_document"]
        },
        "expected_status": "referred"
    },
    {
        "title": "🔄 Referred (Zero Months)",
        "payload": {
            "policy_number": "POL-4001",
            "claim_type": "life",
            "amount": "200000.00",
            "months_active": 0,
            "documents": ["death_certificate", "identity_document"]
        },
        "expected_status": "referred"
    },
    {
        "title": "❌ Rejected (Unsupported Type)",
        "payload": {
            "policy_number": "POL-7001",
            "claim_type": "travel",
            "amount": "10000.00",
            "months_active": 12,
            "documents": []
        },
        "expected_status": "rejected"
    },
    {
        "title": "❌ Rejected (Zero Amount)",
        "payload": {
            "policy_number": "POL-8001",
            "claim_type": "life",
            "amount": "0",
            "months_active": 12,
            "documents": ["death_certificate", "identity_document"]
        },
        "expected_status": "rejected"
    },
    {
        "title": "❌ Rejected (Negative Amount)",
        "payload": {
            "policy_number": "POL-8002",
            "claim_type": "life",
            "amount": "-100.00",
            "months_active": 12,
            "documents": ["death_certificate", "identity_document"]
        },
        "expected_status": "rejected"
    },
    {
        "title": "✅ Boundary Test (3 Months)",
        "payload": {
            "policy_number": "POL-5001",
            "claim_type": "life",
            "amount": "180000.00",
            "months_active": 3,
            "documents": ["death_certificate", "identity_document"]
        },
        "expected_status": "approved"
    },
    {
        "title": "✅ Minimum Amount",
        "payload": {
            "policy_number": "POL-8003",
            "claim_type": "disability",
            "amount": "0.01",
            "months_active": 3,
            "documents": ["medical_report", "identity_document"]
        },
        "expected_status": "approved"
    },
]

def main():
    print("🛡️  DreamGuard Claims Assessment - API Verification\n")
    print(f"Testing {len(test_cases)} scenarios...\n")
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        try:
            result = assess_payload(test["payload"])
            status = result["status"]
            expected = test["expected_status"]
            
            if status == expected:
                passed += 1
                print(f"✅ {test['title']}")
                print(f"   Status: {status} | Amount: ${result['approved_amount']}")
                if result["reasons"]:
                    for reason in result["reasons"]:
                        print(f"   • {reason}")
            else:
                failed += 1
                print(f"❌ {test['title']}")
                print(f"   Expected: {expected}, Got: {status}")
                if result["reasons"]:
                    for reason in result["reasons"]:
                        print(f"   • {reason}")
        except Exception as e:
            failed += 1
            print(f"❌ {test['title']}")
            print(f"   Error: {e}")
        
        print()
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
