from __future__ import annotations

import json
from queue import Empty

import app
import pytest
from tests.helpers.webhook_server import start_webhook_server


def _read_request(server):
    try:
        return server.queue.get(timeout=1)
    except Empty:
        pytest.fail("Webhook server did not receive a request.")


def test_create_task_payload_with_reminder_only(test_logger) -> None:
    intent_payload = {
        "intent": "create-task",
        "content": "upload the Performance Review Files",
        "reminder": "2026-02-02T06:00:00+00:00",
    }
    payload = app.build_create_todo_payload(intent_payload)

    server = start_webhook_server()
    try:
        success = app.send_create_todo_webhook(server.url, payload, test_logger)
        assert success is True
        request = _read_request(server)
    finally:
        server.close()

    body = json.loads(request.body.decode("utf-8"))
    assert body == {
        "title": "upload the Performance Review Files",
        "reminder": "2026-02-02T06:00:00+00:00",
    }
    assert "due" not in body


def test_create_task_payload_with_due_and_reminder(test_logger) -> None:
    intent_payload = {
        "intent": "create-task",
        "content": "Follow-up with my boss. We should talk about our AI strategy.",
        "due": "2026-08-30T06:00:00Z",
        "reminder": "2026-08-20T06:00:00Z",
    }
    payload = app.build_create_todo_payload(intent_payload)

    server = start_webhook_server()
    try:
        success = app.send_create_todo_webhook(server.url, payload, test_logger)
        assert success is True
        request = _read_request(server)
    finally:
        server.close()

    body = json.loads(request.body.decode("utf-8"))
    assert body == {
        "title": "Follow-up with my boss. We should talk about our AI strategy.",
        "due": "2026-08-30T06:00:00Z",
        "reminder": "2026-08-20T06:00:00Z",
    }


def test_webhook_request_format_and_success(test_logger) -> None:
    payload = {"title": "Ping"}

    server = start_webhook_server(response_status=204)
    try:
        success = app.send_create_todo_webhook(server.url, payload, test_logger)
        assert success is True
        request = _read_request(server)
    finally:
        server.close()

    assert request.method == "POST"
    assert request.headers.get("content-type", "").startswith("application/json")
    assert "authorization" not in request.headers


def test_create_note_does_not_call_webhook(temp_config, test_logger, monkeypatch) -> None:
    temp_config.inbox_dir.mkdir(parents=True, exist_ok=True)
    temp_config.processed_dir.mkdir(parents=True, exist_ok=True)

    mp3_file = temp_config.inbox_dir / "voice.mp3"
    mp3_file.write_text("data", encoding="utf-8")

    def dummy_transcriber(_: object) -> str:
        return "hello"

    def dummy_intent(_: str) -> dict[str, str]:
        return {"intent": "create-note", "content": "hello"}

    def fail_if_called(*_: object, **__: object) -> bool:
        raise AssertionError("Webhook should not be called for create-note intents.")

    monkeypatch.setattr(app, "send_create_todo_webhook", fail_if_called)

    app.process_inbox_once(temp_config, test_logger, dummy_transcriber, set(), dummy_intent)


def test_get_create_todo_webhook_url_missing_or_invalid() -> None:
    assert app.get_create_todo_webhook_url({}) is None
    assert app.get_create_todo_webhook_url({"V2A_CREATE_TODO_WEBHOOK_URL": ""}) is None
    assert app.get_create_todo_webhook_url({"V2A_CREATE_TODO_WEBHOOK_URL": "   "}) is None

    with pytest.raises(ValueError):
        app.get_create_todo_webhook_url({"V2A_CREATE_TODO_WEBHOOK_URL": "ftp://example.com"})


def test_webhook_logs_payloads_on_400(test_logger, caplog) -> None:
    payload = {"title": "Ping"}
    server = start_webhook_server(response_status=400, response_body="bad request")
    caplog.set_level("ERROR")
    try:
        success = app.send_create_todo_webhook(server.url, payload, test_logger)
    finally:
        server.close()

    assert success is False
    assert any("Webhook request payload" in record.message for record in caplog.records)
    assert any("Webhook response payload" in record.message for record in caplog.records)
