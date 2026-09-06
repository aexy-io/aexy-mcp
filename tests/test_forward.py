"""The bridge's one job: relay JSON-RPC, and never write anything else to stdout."""

import json

import httpx

from aexy_mcp import server


def _client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def _req(id=1, method="tools/list"):
    return json.dumps({"jsonrpc": "2.0", "id": id, "method": method, "params": {}})


def test_a_reply_is_passed_through():
    def handler(request):
        return httpx.Response(200, json={"jsonrpc": "2.0", "id": 1, "result": {"tools": []}})

    assert server.forward(_client(handler), _req()) == [{"jsonrpc": "2.0", "id": 1, "result": {"tools": []}}]


def test_a_notification_is_not_answered():
    def handler(request):
        return httpx.Response(202)

    assert server.forward(_client(handler), json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"})) == []


def test_auth_failures_become_errors_with_the_original_id():
    def handler(request):
        return httpx.Response(401, json={"error": "invalid_token", "error_description": "Token expired"})

    [reply] = server.forward(_client(handler), _req(id=7))
    assert reply["id"] == 7 and reply["error"]["code"] == -32001
    assert "Token expired" in reply["error"]["message"]


def test_a_wrong_url_does_not_leak_a_non_jsonrpc_body():
    """A 404 `{"detail": "Not Found"}` used to be written to stdout as if it
    were a reply; the client then waited on `initialize` until it timed out."""

    def handler(request):
        return httpx.Response(404, json={"detail": "Not Found"})

    [reply] = server.forward(_client(handler), _req(id=3))
    assert reply == {"jsonrpc": "2.0", "id": 3, "error": {"code": -32603, "message": "404: Not Found"}}


def test_a_200_that_is_not_jsonrpc_is_an_error_too():
    def handler(request):
        return httpx.Response(200, json={"hello": "world"})

    [reply] = server.forward(_client(handler), _req(id=4))
    assert reply["id"] == 4 and "error" in reply


def test_a_batch_gets_one_error_per_id_on_transport_failure():
    def handler(request):
        raise httpx.ConnectError("refused")

    batch = json.dumps([json.loads(_req(id=1)), json.loads(_req(id=2)), {"jsonrpc": "2.0", "method": "n"}])
    replies = server.forward(_client(handler), batch)
    assert [r["id"] for r in replies] == [1, 2]


def test_malformed_input_is_a_parse_error():
    [reply] = server.forward(_client(lambda r: httpx.Response(200)), "{not json")
    assert reply["id"] is None and reply["error"]["code"] == -32700


def test_a_placeholder_workspace_id_is_not_sent(monkeypatch):
    monkeypatch.setenv("AEXY_API_TOKEN", "aexy_x")
    monkeypatch.setenv("AEXY_WORKSPACE_ID", "<workspace-id, if you are in more than one>")
    from aexy_mcp.config import Config

    assert Config().workspace_id == ""
    monkeypatch.setenv("AEXY_WORKSPACE_ID", "8dae7887-1939-44ad-9b53-02b4823dcc38")
    assert Config().workspace_id == "8dae7887-1939-44ad-9b53-02b4823dcc38"
