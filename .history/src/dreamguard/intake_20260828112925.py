"""Load synthetic claims submitted to the DreamGuard assessment service.

This module handles the JSON input boundary for the claims assessment pipeline.
All records loaded are synthetic and for training purposes only.
"""

import json
from decimal import Decimal
from pathlib import Path

from .claims import Claim


def load_claims(path: str | Path) -> list[Claim]:
    """Load a JSON array of claim records and return a list of Claim objects.

    This function reads a JSON file containing an array of claim records and converts
    each record into an immutable `Claim` object. The `amount` field is converted to
    `Decimal` for precise monetary calculations, and the `documents` array is converted
    to an immutable tuple.

    Args:
        path: A file path (string or Path object) pointing to a JSON file. The JSON file
              must contain a top-level array where each element is an object with keys:
              - policy_number (string)
              - claim_type (string)
              - amount (string or number, converted to Decimal)
              - months_active (integer)
              - documents (array of strings)

    Returns:
        A list of `Claim` objects in the order they appear in the JSON file.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
        KeyError: If a record is missing required fields.
        Exception: If conversion to Decimal or other type conversions fail.

    Notes:
        - All records in this repository are synthetic.
        - The JSON file must be valid UTF-8 encoded.
        - No validation of claim content is performed at load time; use `assess_claim`
          to validate individual claims.

    Example:
        >>> claims = load_claims("data/sample_claims.json")
        >>> for claim in claims:
        ...     decision = assess_claim(claim)
        ...     print(f"{claim.policy_number}: {decision.status}")
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