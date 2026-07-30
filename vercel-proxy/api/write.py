"""Vercel Serverless Function - GitHub API Write Proxy"""
import json
import os
import base64
from http.server import BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_API = "https://api.github.com/repos/yangwenhui-ywh/-/contents/data.json"

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self._send_cors()
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body_raw = self.rfile.read(content_len) if content_len > 0 else b"{}"
        try:
            body = json.loads(body_raw)
        except json.JSONDecodeError:
            self._json(400, {"error": "Invalid JSON"})
            return

        # Ping test
        if body.get("_ping"):
            self._json(200, {"ok": True, "service": "github-write-proxy"})
            return

        if not GITHUB_TOKEN:
            self._json(500, {"error": "GITHUB_TOKEN not configured"})
            return

        # Step 1: GET current SHA
        try:
            req = Request(GITHUB_API, headers={
                "Authorization": "token " + GITHUB_TOKEN,
                "Accept": "application/vnd.github+json",
                "User-Agent": "Vercel-Proxy",
                "Cache-Control": "no-cache"
            })
            resp = urlopen(req, timeout=15)
            file_info = json.loads(resp.read())
            sha = file_info.get("sha", "")
        except HTTPError as e:
            err_body = e.read().decode()[:200] if hasattr(e, "read") else str(e)
            self._json(502, {"error": "GitHub GET failed", "status": e.code, "detail": err_body})
            return
        except URLError as e:
            self._json(502, {"error": "GitHub unreachable", "detail": str(e.reason)})
            return

        # Build payload
        payload = {
            "updatedAt": body.get("updatedAt"),
            "updatedBy": body.get("updatedBy", "unknown"),
            "modules": body.get("modules", {}),
            "work段": body.get("work段", ""),
            "班组": body.get("班组", ""),
            "confirmed": body.get("confirmed", {})
        }

        json_str = json.dumps(payload, ensure_ascii=False)
        content_b64 = base64.b64encode(json_str.encode("utf-8")).decode("ascii")

        put_body = json.dumps({
            "message": "update by " + payload["updatedBy"],
            "content": content_b64,
            "sha": sha,
            "branch": "main"
        }).encode("utf-8")

        # Step 2: PUT data.json
        try:
            req2 = Request(GITHUB_API, data=put_body, method="PUT", headers={
                "Authorization": "token " + GITHUB_TOKEN,
                "Content-Type": "application/json",
                "Accept": "application/vnd.github+json",
                "User-Agent": "Vercel-Proxy"
            })
            resp2 = urlopen(req2, timeout=15)
            result = json.loads(resp2.read())
            new_sha = result.get("content", {}).get("sha", "")
            self._json(200, {"ok": True, "sha": new_sha})
        except HTTPError as e:
            err_body = e.read().decode()[:200] if hasattr(e, "read") else str(e)
            self._json(502, {"error": "GitHub PUT failed", "status": e.code, "detail": err_body})
        except URLError as e:
            self._json(502, {"error": "GitHub unreachable", "detail": str(e.reason)})

    def do_GET(self):
        self._json(200, {"status": "ok", "service": "github-write-proxy"})

    def _json(self, code, data):
        self._send_cors()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
