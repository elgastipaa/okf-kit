"""Servidor HTTP. stdlib, sin frameworks."""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from .codes import decode
from .store import connect, count_hit, resolve, shorten

FLAGS = {
    "ANALYTICS": os.environ.get("FLAG_ANALYTICS", "1") == "1",
    "CUSTOM_ALIAS": os.environ.get("FLAG_CUSTOM_ALIAS", "0") == "1",
    "QR": os.environ.get("FLAG_QR", "0") == "1",
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        code = self.path.lstrip("/")
        if not code:
            return self._json(200, {"ok": True, "flags": FLAGS})
        try:
            link_id = decode(code)
        except ValueError:
            return self._json(404, {"error": "no existe"})
        found = resolve(self.server.con, link_id)
        if found is None:
            return self._json(404, {"error": "no existe"})
        target, expired = found
        if expired:
            return self._json(410, {"error": "expirado"})
        if FLAGS["ANALYTICS"]:
            count_hit(self.server.con, link_id)
        self.send_response(302)
        self.send_header("Location", target)
        self.end_headers()

    def do_POST(self) -> None:
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        if not body.get("url"):
            return self._json(400, {"error": "falta url"})
        code = shorten(self.server.con, body["url"], body.get("ttl_days"))
        self._json(201, {"code": code})

    def _json(self, status: int, payload: dict) -> None:
        raw = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, *args) -> None:
        pass


def serve(port: int = 8080) -> None:
    srv = HTTPServer(("", port), Handler)
    srv.con = connect()
    srv.serve_forever()
