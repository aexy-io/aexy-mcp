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


# --- Responses that used to vanish -------------------------------------------
#
# `not response.content` was checked before the status, so anything that failed
# without a body returned [] and the client waited on `initialize` until its own
# timeout. Each of these is a real way to get a bodiless non-200.


def test_a_redirect_is_not_silence():
    """An http:// URL for an https:// server. httpx does not follow redirects,
    so this used to be a bodiless 307 read as "nothing to say"."""

    def handler(request):
        return httpx.Response(307, headers={"location": "https://app.aexy.io/api/v1/mcp"})

    [reply] = server.forward(_client(handler), _req(id=11))
    assert reply["id"] == 11 and reply["error"]["code"] == -32001
    assert "redirects to https://app.aexy.io/api/v1/mcp" in reply["error"]["message"]
    assert "AEXY_API_URL" in reply["error"]["message"]


def test_a_permanent_redirect_is_not_silence():
    def handler(request):
        return httpx.Response(301, headers={"location": "https://app.aexy.io/api/v1/mcp"})

    [reply] = server.forward(_client(handler), _req(id=12))
    assert reply["error"]["code"] == -32001


def test_a_redirect_without_a_location_still_says_something():
    [reply] = server.forward(_client(lambda r: httpx.Response(308)), _req(id=13))
    assert "no Location header" in reply["error"]["message"]


def test_a_bodiless_auth_failure_is_not_silence():
    """A proxy rejecting the token before it reaches Aexy sends no body."""

    def handler(request):
        return httpx.Response(401)

    [reply] = server.forward(_client(handler), _req(id=14))
    assert reply["id"] == 14 and reply["error"]["code"] == -32001
    assert "401" in reply["error"]["message"]


def test_a_bodiless_gateway_error_is_not_silence():
    [reply] = server.forward(_client(lambda r: httpx.Response(502)), _req(id=15))
    assert reply["error"]["code"] == -32603 and "502" in reply["error"]["message"]


def test_an_empty_200_answers_a_request_but_not_a_notification():
    """No id means it really was only notifications; an id means somebody waits."""
    empty_200 = _client(lambda r: httpx.Response(200))

    [reply] = server.forward(empty_200, _req(id=16))
    assert reply["error"]["code"] == -32603 and "Empty 200" in reply["error"]["message"]

    notification = json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"})
    assert server.forward(empty_200, notification) == []


def test_a_202_is_still_not_answered():
    """The accepted-notification path must survive the reordering."""
    assert server.forward(_client(lambda r: httpx.Response(202)), _req(id=17)) == []


# --- Failures that used to kill the process ----------------------------------


def test_a_malformed_url_is_an_error_not_a_crash():
    """httpx.InvalidURL is not an httpx.HTTPError, so it escaped the handler."""

    def handler(request):
        raise httpx.InvalidURL("no host")

    [reply] = server.forward(_client(handler), _req(id=18))
    assert reply["id"] == 18 and reply["error"]["code"] == -32000
    assert "InvalidURL" in reply["error"]["message"]


def test_a_timeout_value_that_is_not_a_number_falls_back(monkeypatch, capsys):
    """float() ran at import, before main's friendly token check."""
    from aexy_mcp.config import DEFAULT_TIMEOUT_SECONDS, Config

    monkeypatch.setenv("AEXY_TIMEOUT_SECONDS", "90s")
    assert Config().timeout_seconds == DEFAULT_TIMEOUT_SECONDS
    assert "AEXY_TIMEOUT_SECONDS" in capsys.readouterr().err

    monkeypatch.setenv("AEXY_TIMEOUT_SECONDS", "0")
    assert Config().timeout_seconds == DEFAULT_TIMEOUT_SECONDS

    monkeypatch.setenv("AEXY_TIMEOUT_SECONDS", "12.5")
    assert Config().timeout_seconds == 12.5


# --- A relayed body is bounded -----------------------------------------------


def test_a_proxy_html_page_is_clipped():
    page = "<html>" + "x" * 9000 + "</html>"

    def handler(request):
        return httpx.Response(504, text=page)

    [reply] = server.forward(_client(handler), _req(id=19))
    assert len(reply["error"]["message"]) < len(page)
    assert "more chars" in reply["error"]["message"]
