# Research: Create-task webhook

## Decision 1: HTTP client for webhook delivery

- **Decision**: Use Python standard library `urllib.request` for HTTP POST calls.
- **Rationale**: Avoids adding new dependencies; sufficient for simple JSON POST with timeouts and status checks.
- **Alternatives considered**:
  - `requests`: ergonomic but adds a new dependency.
  - `httpx`: more features but heavier and unnecessary for this scope.
  - `http.client`: lower-level than needed.

## Decision 2: Webhook test server strategy

- **Decision**: Use `http.server.HTTPServer` with a custom `BaseHTTPRequestHandler`, run in a background thread, capture requests via `queue.Queue`, and shut down with `server.shutdown()`/`server_close()`.
- **Rationale**: Keeps tests dependency-free, deterministic, and easy to assert payloads, headers, and call counts.
- **Alternatives considered**:
  - External test utilities (e.g., `responses`, `pytest-httpserver`): would introduce new dependencies.
  - Real external webhook: not deterministic and violates test isolation.

## Decision 3: Webhook timeout and status handling

- **Decision**: Use a short request timeout (e.g., 10 seconds) and treat any HTTP 2xx as success; non-2xx is failure.
- **Rationale**: Prevents hangs in the scanner loop and aligns with webhook clarifications.
- **Alternatives considered**:
  - No timeout: risk of hanging processing loop.
  - Only 200 OK success: rejects valid 204/201 responses.
