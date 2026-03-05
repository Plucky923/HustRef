"""Local web app for HustRef."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from typing import Any

from hustref.pipeline import convert_with_diagnostics

STATIC_DIR = Path(__file__).resolve().parent / "webui"
SUPPORTED_SOURCES = {"auto", "bibtex", "endnote", "ris", "acm_ref", "plain", "text"}


@dataclass(frozen=True)
class ConvertRequest:
    text: str
    source: str
    strict: bool


class BadRequestError(ValueError):
    """Raised when request payload is invalid."""


def convert_payload_to_response(payload: dict[str, Any]) -> dict[str, Any]:
    request = _parse_convert_payload(payload)
    report = convert_with_diagnostics(
        request.text,
        source_format=request.source,
        strict=request.strict,
    )

    error_count = 0
    warning_count = 0
    for entry in report.entries:
        for issue in entry.issues:
            if issue.level == "error":
                error_count += 1
            elif issue.level == "warning":
                warning_count += 1

    output_text = "\n".join(report.formatted_lines())
    return {
        "ok": not report.has_errors or not request.strict,
        "strict": request.strict,
        "source": request.source,
        "text": output_text,
        "lines": report.formatted_lines(),
        "entries": [entry.to_dict() for entry in report.entries],
        "summary": {
            "record_count": len(report.entries),
            "error_count": error_count,
            "warning_count": warning_count,
        },
    }


def build_server(host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), HustRefRequestHandler)


class HustRefRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path in {"/", "/index.html"}:
            self._serve_file("index.html", content_type="text/html; charset=utf-8")
            return
        if self.path == "/styles.css":
            self._serve_file("styles.css", content_type="text/css; charset=utf-8")
            return
        if self.path == "/app.js":
            self._serve_file("app.js", content_type="application/javascript; charset=utf-8")
            return

        self._write_json({"ok": False, "error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path != "/api/convert":
            self._write_json({"ok": False, "error": "Not found"}, status=HTTPStatus.NOT_FOUND)
            return

        try:
            body = self._read_json_body()
            result = convert_payload_to_response(body)
            self._write_json(result, status=HTTPStatus.OK)
        except BadRequestError as exc:
            self._write_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
        except Exception:
            self._write_json(
                {"ok": False, "error": "Internal server error"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    def log_message(self, fmt: str, *args: Any) -> None:
        # Keep CLI output clean for local usage.
        return

    def _read_json_body(self) -> dict[str, Any]:
        raw_length = self.headers.get("Content-Length", "0")
        try:
            content_length = int(raw_length)
        except ValueError as exc:
            raise BadRequestError("Invalid Content-Length header") from exc

        body = self.rfile.read(max(content_length, 0))
        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception as exc:
            raise BadRequestError("Request body must be valid JSON") from exc

        if not isinstance(payload, dict):
            raise BadRequestError("JSON payload must be an object")
        return payload

    def _serve_file(self, name: str, content_type: str) -> None:
        path = STATIC_DIR / name
        if not path.exists():
            self._write_json({"ok": False, "error": "Not found"}, status=HTTPStatus.NOT_FOUND)
            return

        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _write_json(self, payload: dict[str, Any], status: HTTPStatus) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _parse_convert_payload(payload: dict[str, Any]) -> ConvertRequest:
    text = payload.get("text", "")
    source = str(payload.get("source", "auto")).strip().lower()
    strict = bool(payload.get("strict", False))

    if not isinstance(text, str):
        raise BadRequestError("'text' must be a string")
    if not text.strip():
        raise BadRequestError("'text' is required")
    if source not in SUPPORTED_SOURCES:
        raise BadRequestError(f"Unsupported source format: {source}")

    return ConvertRequest(text=text, source=source, strict=strict)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run HustRef local web app.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host.")
    parser.add_argument("--port", type=int, default=8765, help="Bind port.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    server = build_server(args.host, args.port)
    print(f"HustRef web app running at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

