from fastapi.testclient import TestClient

from examples.self_hosted_app import app

client = TestClient(app)


def test_docs_and_redoc_render_with_self_hosted_assets():
    docs = client.get("/docs")
    redoc = client.get("/redoc")

    assert docs.status_code == 200
    assert redoc.status_code == 200
    assert '<script src="/static/swagger-ui-bundle.js" charset="UTF-8"></script>' in docs.text
    assert '<script src="/static/redoc.standalone.js">' in redoc.text


def test_static_vendor_assets_are_served():
    for path in [
        "/static/swagger-ui-bundle.js",
        "/static/swagger-ui.css",
        "/static/favicon.png",
        "/static/redoc.standalone.js",
        "/static/fonts.css",
    ]:
        assert client.get(path).status_code == 200, path


def test_oauth2_redirect_pages_have_no_inline_script():
    html_response = client.get("/docs/oauth2-redirect")
    js_response = client.get("/docs/oauth2-redirect.js")

    assert html_response.status_code == 200
    assert js_response.status_code == 200
    assert "<script>" not in html_response.text
    assert js_response.text.strip()


def test_csp_has_no_external_script_or_style_origins():
    response = client.get("/docs")

    csp = response.headers["content-security-policy"]
    assert "script-src 'self';" in csp
    assert "'unsafe-inline'" not in csp
