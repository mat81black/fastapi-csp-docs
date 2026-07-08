import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

import fastapi_csp_docs


def _no_inline_script_or_style(html: str) -> bool:
    return "<script>" not in html and "<style>" not in html


def test_setup_raises_if_docs_url_not_disabled():
    app = FastAPI()  # docs_url defaults to "/docs"

    with pytest.raises(RuntimeError, match="docs_url=None"):
        fastapi_csp_docs.setup(app)


def test_setup_raises_if_redoc_url_not_disabled():
    app = FastAPI(docs_url=None)  # redoc_url defaults to "/redoc"

    with pytest.raises(RuntimeError, match="redoc_url=None"):
        fastapi_csp_docs.setup(app)


def test_setup_registers_swagger_and_redoc_routes():
    app = FastAPI(docs_url=None, redoc_url=None)
    fastapi_csp_docs.setup(app)
    client = TestClient(app)

    for path in [
        "/docs",
        "/docs/swagger-initializer.js",
        "/redoc",
        "/redoc/redoc.css",
        "/docs/oauth2-redirect",
        "/docs/oauth2-redirect.js",
    ]:
        response = client.get(path)
        assert response.status_code == 200, path


def test_setup_docs_html_and_redoc_html_have_no_inline_script_or_style():
    app = FastAPI(docs_url=None, redoc_url=None)
    fastapi_csp_docs.setup(app)
    client = TestClient(app)

    docs_html = client.get("/docs").text
    redoc_html = client.get("/redoc").text
    oauth_html = client.get("/docs/oauth2-redirect").text

    assert _no_inline_script_or_style(docs_html)
    assert _no_inline_script_or_style(redoc_html)
    assert _no_inline_script_or_style(oauth_html)


def test_setup_asset_content_types():
    app = FastAPI(docs_url=None, redoc_url=None)
    fastapi_csp_docs.setup(app)
    client = TestClient(app)

    assert client.get("/docs/swagger-initializer.js").headers["content-type"].startswith("text/javascript")
    assert client.get("/docs/oauth2-redirect.js").headers["content-type"].startswith("text/javascript")
    assert client.get("/redoc/redoc.css").headers["content-type"].startswith("text/css")


def test_setup_swagger_initializer_embeds_openapi_url():
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url="/schema.json")
    fastapi_csp_docs.setup(app)
    client = TestClient(app)

    js = client.get("/docs/swagger-initializer.js").text
    assert "/schema.json" in js


def test_setup_redoc_search_enabled_by_default():
    app = FastAPI(docs_url=None, redoc_url=None)
    fastapi_csp_docs.setup(app)
    client = TestClient(app)

    html = client.get("/redoc").text
    assert "disable-search" not in html


def test_setup_respects_custom_docs_and_redoc_url():
    app = FastAPI(docs_url=None, redoc_url=None)
    fastapi_csp_docs.setup(app, docs_url="/documentation", redoc_url="/documentation/redoc")
    client = TestClient(app)

    assert client.get("/documentation").status_code == 200
    assert client.get("/documentation/swagger-initializer.js").status_code == 200
    assert client.get("/documentation/redoc").status_code == 200
    assert client.get("/documentation/redoc/redoc.css").status_code == 200
    assert client.get("/docs").status_code == 404
    assert client.get("/redoc").status_code == 404


def test_setup_docs_url_none_skips_swagger_ui_only():
    app = FastAPI(docs_url=None, redoc_url=None)
    fastapi_csp_docs.setup(app, docs_url=None)
    client = TestClient(app)

    assert client.get("/docs").status_code == 404
    assert client.get("/redoc").status_code == 200


def test_setup_redoc_url_none_skips_redoc_only():
    app = FastAPI(docs_url=None, redoc_url=None)
    fastapi_csp_docs.setup(app, redoc_url=None)
    client = TestClient(app)

    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 404


def test_setup_skips_oauth2_redirect_when_disabled_on_app():
    app = FastAPI(docs_url=None, redoc_url=None, swagger_ui_oauth2_redirect_url=None)
    fastapi_csp_docs.setup(app)
    client = TestClient(app)

    assert client.get("/docs").status_code == 200
    assert client.get("/docs/oauth2-redirect").status_code == 404
    assert client.get("/docs/oauth2-redirect.js").status_code == 404


def test_setup_no_routes_when_openapi_disabled():
    app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)
    fastapi_csp_docs.setup(app)
    client = TestClient(app)

    assert client.get("/docs").status_code == 404
    assert client.get("/redoc").status_code == 404


def test_setup_root_path_is_reflected_in_mounted_sub_app():
    sub_app = FastAPI(docs_url=None, redoc_url=None)
    fastapi_csp_docs.setup(sub_app)

    parent_app = FastAPI()
    parent_app.mount("/api", sub_app)

    client = TestClient(parent_app)
    js = client.get("/api/docs/swagger-initializer.js").text
    assert "/api/openapi.json" in js

    redoc_html = client.get("/api/redoc").text
    assert "/api/openapi.json" in redoc_html
    assert "/api/redoc/redoc.css" in redoc_html
