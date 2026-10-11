"""Serve the local simulation demo without any infrastructure-control interface."""

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .demo import run_episode
from .scenarios import manifest


class DemoHandler(BaseHTTPRequestHandler):
    """Expose frozen scenarios and freshly executed simulator episodes."""

    def do_GET(self):
        request = urlparse(self.path)
        if request.path == "/":
            payload = Path(__file__).with_name("demo.html").read_bytes()
            kind = "text/html; charset=utf-8"
        elif request.path == "/scenarios":
            payload = json.dumps(manifest()).encode()
            kind = "application/json"
        elif request.path == "/run":
            query = parse_qs(request.query)
            try:
                episode = run_episode(
                    query.get("controller", ["filtered"])[0],
                    query.get("scenario", ["node_0"])[0],
                    int(query.get("seed", ["1000"])[0]),
                )
            except ValueError as error:
                self.send_error(400, str(error))
                return
            payload = json.dumps(episode).encode()
            kind = "application/json"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)


def make_server(port=8765):
    """Bind only to this computer; callers can use port zero for isolated checks."""
    return HTTPServer(("127.0.0.1", port), DemoHandler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    with make_server(args.port) as server:
        print(f"Live simulation demo: http://127.0.0.1:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
