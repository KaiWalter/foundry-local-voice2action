from __future__ import annotations

from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from queue import Queue
from threading import Thread


@dataclass(frozen=True)
class WebhookRequest:
    method: str
    path: str
    headers: dict[str, str]
    body: bytes


@dataclass
class WebhookServer:
    server: HTTPServer
    thread: Thread
    queue: Queue[WebhookRequest]
    url: str

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


def start_webhook_server(response_status: int = 200, response_body: bytes | str = b"") -> WebhookServer:
    queue: Queue[WebhookRequest] = Queue()
    response_bytes = (
        response_body.encode("utf-8") if isinstance(response_body, str) else response_body
    )

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler naming
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length)
            headers = {key.lower(): value for key, value in self.headers.items()}
            queue.put(
                WebhookRequest(
                    method="POST",
                    path=self.path,
                    headers=headers,
                    body=body,
                )
            )
            self.send_response(response_status)
            if response_bytes:
                self.send_header("Content-Length", str(len(response_bytes)))
            self.end_headers()
            if response_bytes:
                self.wfile.write(response_bytes)

        def log_message(self, format: str, *args: object) -> None:  # noqa: A002
            return

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    return WebhookServer(server=server, thread=thread, queue=queue, url=f"http://{host}:{port}")
