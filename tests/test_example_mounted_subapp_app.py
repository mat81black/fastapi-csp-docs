from fastapi.testclient import TestClient

from examples.mounted_subapp_app import app

client = TestClient(app)


def test_doc_urls_resolve_under_the_mount_prefix():
    js = client.get("/api/docs/swagger-initializer.js").text
    redoc_html = client.get("/api/redoc").text

    assert "/api/openapi.json" in js
    assert "/api/openapi.json" in redoc_html
    assert "/api/redoc/redoc.css" in redoc_html


def test_root_docs_are_fastapis_own_not_the_csp_safe_ones():
    # The parent app never disabled its own built-in docs (only sub_app did), so
    # "/docs" here is FastAPI's native inline-script page, not the CSP-safe one
    # fastapi_csp_docs registers on sub_app under /api.
    response = client.get("/docs")

    assert response.status_code == 200
    assert "<script>" in response.text


def test_sub_app_items_route_reachable_under_prefix():
    response = client.get("/api/items")

    assert response.status_code == 200
    assert response.json() == {"items": []}
