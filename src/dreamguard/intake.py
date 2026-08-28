"""Load synthetic claims submitted to the DreamGuard assessment service."""

import json
from decimal import Decimal
from pathlib import Path

from .claims import Claim


def load_claims(path: str | Path) -> list[Claim]:
    """Load synthetic claims from a JSON file for assessment.

    Reads a JSON file containing an array of claim records and converts each
    into an immutable :class:`Claim` object. All claims are entirely fictional.

    The JSON file must contain an array of objects with these fields:

    - ``policy_number`` (string): Fictional policy identifier.
    - ``claim_type`` (string): Claim category (typically ``life`` or ``disability``).
    - ``amount`` (string or number): Requested amount; will be converted to
      :class:`~decimal.Decimal` to avoid floating-point precision issues.
    - ``months_active`` (integer): How long the policy has been active.
    - ``documents`` (array of strings): Fictional document identifiers.

    Args:
        path: Path to the JSON claims file (string or :class:`~pathlib.Path`).

    Returns:
        List of :class:`Claim` objects ready for assessment.

    Raises:
        FileNotFoundError: If the JSON file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
        KeyError: If a record is missing a required field.
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