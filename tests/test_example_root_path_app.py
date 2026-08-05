from fastapi.testclient import TestClient

from examples.root_path_app import app

client = TestClient(app)


def test_doc_urls_are_prefixed_with_the_configured_root_path():
    js = client.get("/docs/swagger-initializer.js").text
    redoc_html = client.get("/redoc").text

    assert "/api/openapi.json" in js
    assert "/api/openapi.json" in redoc_html
    assert "/api/redoc/redoc.css" in redoc_html


def test_items_route_still_works():
    response = client.get("/items")

    assert response.status_code == 200
    assert response.json() == {"items": []}
