from fastapi.testclient import TestClient

from examples.assisted_app import app

client = TestClient(app)


def test_docs_and_redoc_render_with_no_inline_script_or_style():
    docs = client.get("/docs")
    redoc = client.get("/redoc")

    assert docs.status_code == 200
    assert redoc.status_code == 200
    assert "<script>" not in docs.text
    assert "<style>" not in redoc.text


def test_csp_header_whitelists_exact_cdn_asset_urls():
    response = client.get("/docs")

    csp = response.headers["content-security-policy"]
    assert "'unsafe-inline'" not in csp
    assert "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js" in csp
    assert "https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js" in csp


def test_items_route_still_works_alongside_docs():
    response = client.get("/items")

    assert response.status_code == 200
    assert response.json() == {"items": []}
