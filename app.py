import json
import os
import sys
from decimal import Decimal, InvalidOperation
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from dreamguard import Claim, assess_claim


def assess_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Convert a synthetic browser payload into a serialized claim decision."""
    try:
        claim = Claim(
            policy_number=str(payload["policy_number"]),
            claim_type=str(payload["claim_type"]),
            amount=Decimal(str(payload["amount"])),
            months_active=int(payload["months_active"]),
            documents=tuple(str(item) for item in payload["documents"]),
        )
    except (InvalidOperation, KeyError, TypeError, ValueError) as error:
        raise ValueError("Invalid claim payload") from error

    decision = assess_claim(claim)
    return {
        "status": decision.status,
        "approved_amount": str(decision.approved_amount),
        "reasons": list(decision.reasons),
    }


class ChallengeHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/":
            self.send_response(302)
            self.send_header("Location", "/challenge/")
            self.end_headers()
            return
        if path == "/health":
            body = b"healthy\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def do_POST(self):
        if urlsplit(self.path).path != "/api/assess":
            self.send_error(404)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(content_length))
            if not isinstance(payload, dict):
                raise ValueError("Invalid claim payload")
            response = assess_payload(payload)
        except (json.JSONDecodeError, ValueError):
            self._send_json(400, {"error": "Invalid claim payload"})
            return

        self._send_json(200, response)

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        super().end_headers()


def main():
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), ChallengeHandler)
    print(f"Serving Momentum Copilot Race on port {port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()