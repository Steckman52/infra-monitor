def test_request_from_an_unrecognised_host_is_rejected(client):
    """The API has no authentication because it is a single-user tool bound
    to localhost. That reasoning only holds if the Host header is one we
    recognise: a page the user visits can re-point its own hostname at
    127.0.0.1 (DNS rebinding), and the browser then treats the backend as
    same-origin and can read every response -- including file contents a
    scan collected."""
    response = client.get("/api/dashboard", headers={"Host": "attacker-rebind.example"})

    assert response.status_code == 400


def test_localhost_requests_are_allowed(client):
    assert client.get("/api/dashboard", headers={"Host": "localhost"}).status_code == 200
    assert client.get("/api/dashboard", headers={"Host": "127.0.0.1:8000"}).status_code == 200
