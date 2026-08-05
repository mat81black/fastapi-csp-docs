from fastapi.testclient import TestClient

from examples.oauth2_redirect_app import app

client = TestClient(app)


def test_oauth2_redirect_pages_have_no_inline_script():
    html_response = client.get("/docs/oauth2-redirect")
    js_response = client.get("/docs/oauth2-redirect.js")

    assert html_response.status_code == 200
    assert js_response.status_code == 200
    assert "<script>" not in html_response.text
    assert js_response.text.strip()


def test_swagger_ui_init_js_embeds_oauth_config():
    js = client.get("/docs/swagger-initializer.js").text

    assert "oauth2RedirectUrl" in js
    assert "demo-client-id" in js


def test_protected_route_requires_a_token():
    response = client.get("/protected")

    assert response.status_code == 401
