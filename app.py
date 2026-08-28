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
    """Convert a synthetic browser payload into a serialized claim decision.

    Args:
        payload: JSON-like dictionary containing claim fields such as
            ``policy_number``, ``claim_type``, ``amount``, ``months_active``, and
            ``documents``.

    Returns:
        A dictionary with the normalized decision payload used by the browser API:
        ``status``, ``approved_amount`` as a string, and ``reasons`` as a list.

    Raises:
        ValueError: If the payload is missing required fields or contains values
            that cannot be converted into a valid ``Claim`` instance.
    """
    try:
        # The browser sends strings, so convert to the domain types expected by the
        # Claim dataclass before handing control to the assessment logic.
        claim = Claim(
            policy_number=str(payload["policy_number"]),
            claim_type=str(payload["claim_type"]),
            amount=Decimal(str(payload["amount"])),
            months_active=int(payload["months_active"]),
            documents=tuple(str(item) for item in payload["documents"]),
        )
    except (InvalidOperation, KeyError, TypeError, ValueError) as error:
        # The API intentionally collapses several different input problems into one
        # user-facing validation error so the browser can show a consistent message.
        raise ValueError("Invalid claim payload") from error

    decision = assess_claim(claim)
    return {
        # JSON responses must be serializable and browser-friendly, so the Decimal
        # from the domain model is converted to a string here.
        "status": decision.status,
        "approved_amount": str(decision.approved_amount),
        "reasons": list(decision.reasons),
    }


class ChallengeHandler(SimpleHTTPRequestHandler):
    """Serve the challenge app and the synthetic claims assessment API.

    This handler supports the static challenge pages and exposes a small
    assessment endpoint that accepts JSON payloads and responds with claim
    decisions from ``assess_claim``.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the request handler with the repository root as the document directory.

        Args:
            *args: Positional arguments passed to ``SimpleHTTPRequestHandler``.
            **kwargs: Keyword arguments passed to ``SimpleHTTPRequestHandler``.
        """
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        """Handle GET requests for the challenge app and health endpoint.

        Behavior:
            - Redirects ``/`` to ``/challenge/``.
            - Responds with ``200`` and ``healthy`` for ``/health``.
            - Delegates all other file requests to the default static file handler.
        """
        path = urlsplit(self.path).path
        if path == "/":
            # The challenge guide is served under /challenge/, so the app routes the
            # landing page there to keep the browser flow simple and predictable.
            self.send_response(302)
            self.send_header("Location", "/challenge/")
            self.end_headers()
            return
        if path == "/health":
            # A lightweight health check keeps the service easy to verify without
            # having to bootstrap the static UI or run any claims logic.
            body = b"healthy\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def do_POST(self):
        """Accept claim assessment requests posted to the API endpoint.

        Supported behavior:
            - Only ``/api/assess`` is accepted.
            - JSON request bodies are parsed and passed to ``assess_payload``.
            - Invalid JSON or invalid claim payloads return a JSON error response.

        Returns:
            None. The method writes an HTTP response directly to the client.
        """
        if urlsplit(self.path).path != "/api/assess":
            # This keeps the service intentionally narrow and prevents arbitrary POST
            # routes from being treated as assessment requests.
            self.send_error(404)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(content_length))
            if not isinstance(payload, dict):
                # The assessment logic expects a single object payload; rejecting a
                # non-dictionary keeps the conversion path consistent and predictable.
                raise ValueError("Invalid claim payload")
            response = assess_payload(payload)
        except (json.JSONDecodeError, ValueError):
            # The browser-facing API treats malformed input as a 400 so callers can
            # correct the request without exposing internal server details.
            self._send_json(400, {"error": "Invalid claim payload"})
            return

        self._send_json(200, response)

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        """Write a JSON response body to the client.

        Args:
            status: HTTP status code for the response.
            payload: Mapping that will be serialized as JSON.
        """
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        """Add security headers before finishing the HTTP response.

        This implementation adds ``X-Content-Type-Options`` and
        ``Referrer-Policy`` to the default response headers.
        """
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        super().end_headers()


def main():
    """Start the local DreamGuard challenge web server.

    The server binds to ``0.0.0.0`` on the configured port and serves the static
    challenge files and the synthetic claims assessment API.

    Environment:
        PORT: Optional port override; defaults to ``8000``.

    Returns:
        None. The function blocks indefinitely while the HTTP server runs.
    """
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), ChallengeHandler)
    print(f"Serving Momentum Copilot Race on port {port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()