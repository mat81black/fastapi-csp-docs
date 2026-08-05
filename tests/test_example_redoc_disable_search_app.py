from fastapi.testclient import TestClient

from examples.redoc_disable_search_app import app

client = TestClient(app)


def test_redoc_disables_search_and_csp_has_no_blob_worker_src():
    response = client.get("/redoc")

    assert response.status_code == 200
    assert 'disable-search="true"' in response.text

    csp = response.headers["content-security-policy"]
    assert "worker-src 'self'" in csp
    assert "blob:" not in csp


def test_docs_still_wired_through_setup_and_renders():
    response = client.get("/docs")

    assert response.status_code == 200
    assert "<script>" not in response.text


def test_items_route_still_works():
    response = client.get("/items")

    assert response.status_code == 200
    assert response.json() == {"items": []}
