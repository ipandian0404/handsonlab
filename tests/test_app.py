import sys
import unittest
from decimal import Decimal
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parents[1]))

from app import assess_payload, serialize_for_json


class AssessPayloadTests(unittest.TestCase):
    def test_complete_synthetic_claim_returns_approved_decision(self):
        decision = assess_payload(
            {
                "policy_number": "SYN-UI-1001",
                "claim_type": "life",
                "amount": "250000.00",
                "months_active": 24,
                "documents": ["death_certificate", "identity_document"],
            }
        )

        self.assertEqual("approved", decision["status"])
        self.assertEqual("250000.00", decision["approved_amount"])
        self.assertEqual([], decision["reasons"])
        self.assertIn("approved", decision["notification"])

    def test_assessment_payload_reports_approved_pending_referred_and_rejected_outcomes(self):
        scenarios = (
            (
                "approved",
                {
                    "policy_number": "SYN-UI-1002",
                    "claim_type": "life",
                    "amount": "250000.00",
                    "months_active": 24,
                    "documents": ["death_certificate", "identity_document"],
                },
                "approved",
                "250000.00",
                [],
            ),
            (
                "pending",
                {
                    "policy_number": "SYN-UI-1003",
                    "claim_type": "disability",
                    "amount": "30000.00",
                    "months_active": 6,
                    "documents": ["identity_document"],
                },
                "pending_documents",
                "0",
                ["Missing medical_report"],
            ),
            (
                "referred",
                {
                    "policy_number": "SYN-UI-1004",
                    "claim_type": "life",
                    "amount": "80000.00",
                    "months_active": 2,
                    "documents": ["death_certificate", "identity_document"],
                },
                "referred",
                "0",
                ["Waiting period review required"],
            ),
            (
                "rejected",
                {
                    "policy_number": "SYN-UI-1005",
                    "claim_type": "travel",
                    "amount": "10000.00",
                    "months_active": 12,
                    "documents": [],
                },
                "rejected",
                "0",
                ["Unsupported claim type: travel"],
            ),
        )

        for name, payload, expected_status, expected_amount, expected_reasons in scenarios:
            with self.subTest(case=name):
                decision = assess_payload(payload)

                self.assertEqual(expected_status, decision["status"])
                self.assertEqual(expected_amount, decision["approved_amount"])
                self.assertEqual(expected_reasons, decision["reasons"])
                self.assertIn("notification", decision)

    def test_invalid_browser_payload_raises_value_error(self):
        with self.assertRaisesRegex(ValueError, "Invalid claim payload"):
            assess_payload(
                {
                    "policy_number": "SYN-UI-1006",
                    "claim_type": "life",
                    "amount": "not-an-amount",
                    "months_active": 12,
                    "documents": [],
                }
            )


if __name__ == "__main__":
    unittest.main()