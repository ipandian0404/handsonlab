"""Load synthetic claims submitted to the DreamGuard assessment service.

This module handles JSON intake of claim records. All records processed are
synthetic and contain only fictional data.
"""

import json
from decimal import Decimal
from pathlib import Path

from .claims import Claim


def load_claims(path: str | Path) -> list[Claim]:
    """Load synthetic claims from a JSON file.

    Reads a top-level JSON array where each object represents a claim record.
    Converts the "amount" field to Decimal and the "documents" field to a
    tuple, then returns a list of Claim objects.

    All records are synthetic and contain only fictional data. Example JSON:

        [
          {
            "policy_number": "SYN-1001",
            "claim_type": "life",
            "amount": "250000.00",
            "months_active": 24,
            "documents": ["death_certificate", "identity_document"]
          }
        ]

    Args:
        path: File path (string or Path object) to the JSON claims file.

    Returns:
        A list of Claim objects parsed from the JSON file.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
        KeyError: If required fields are missing from a record
            (policy_number, claim_type, amount, months_active, documents).
        decimal.InvalidOperation: If the amount field cannot be converted to
            Decimal.
        TypeError: If documents is not a list/sequence.
    """
    with Path(path).open(encoding="utf-8") as claims_file:
        records = json.load(claims_file)

    return [
        Claim(
            policy_number=record["policy_number"],
            claim_type=record["claim_type"],
            amount=Decimal(record["amount"]),
            months_active=record["months_active"],
            documents=tuple(record["documents"]),
        )
        for record in records
    ]