
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import parse_qs, urlparse


HOST = "127.0.0.1"
PORT = 8000


class ApiHandler(BaseHTTPRequestHandler):
    server_version = "D3LocalAPI/1.1"

    def send_json(self, status: int, payload: dict) -> None:
        data = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")
        self.send_response(status)
        if status == 401:
            self.send_header("WWW-Authenticate", 'Bearer realm="D3-local"')
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            self.send_json(200, {"status": "ok"})
            return

        if parsed.path == "/echo":
            args = {
                key: values[0] if len(values) == 1 else values
                for key, values in parse_qs(parsed.query).items()
            }
            self.send_json(200, {"args": args})
            return

        if parsed.path == "/admin":
            authorization = self.headers.get("Authorization")
            if authorization is None:
                self.send_json(401, {"error": "missing_token"})
            elif authorization == "Bearer user-token":
                self.send_json(403, {"error": "permission_denied"})
            elif authorization == "Bearer admin-token":
                self.send_json(200, {"message": "welcome_admin"})
            else:
                self.send_json(401, {"error": "invalid_token"})
            return

        self.send_json(404, {"error": "not_found", "path": parsed.path})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/login":
            self.send_json(404, {"error": "not_found", "path": parsed.path})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            body = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            self.send_json(400, {"error": "invalid_json"})
            return

        if not isinstance(body, dict):
            self.send_json(400, {"error": "expected_json_object"})
            return

        if body.get("username") == "qa01" and body.get("password") == "123456":
            self.send_json(200, {"token": "user-token", "user": "qa01"})
        else:
            self.send_json(401, {"error": "invalid_credentials"})

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")


def main() -> None:
    server = HTTPServer((HOST, PORT), ApiHandler)
    print(f"D3 local API: http://{HOST}:{PORT}")
    print("按 Ctrl+C 停止服务")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
