import fastapi_csp_docs


def test_get_swagger_ui_html_has_no_inline_script_or_style():
    html = bytes(
        fastapi_csp_docs.get_swagger_ui_html(
            title="Test - Swagger UI",
            swagger_ui_init_script_url="/docs/swagger-initializer.js",
        ).body
    ).decode()

    assert "<script>" not in html
    assert "<style>" not in html
    assert '<script src="/docs/swagger-initializer.js" charset="UTF-8"></script>' in html


def test_get_swagger_ui_html_custom_asset_urls():
    html = bytes(
        fastapi_csp_docs.get_swagger_ui_html(
            title="Test - Swagger UI",
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
            swagger_favicon_url="/static/favicon.png",
            swagger_ui_init_script_url="/docs/swagger-initializer.js",
        ).body
    ).decode()

    assert '<script src="/static/swagger-ui-bundle.js" charset="UTF-8"></script>' in html
    assert 'href="/static/swagger-ui.css"' in html
    assert 'href="/static/favicon.png"' in html


def test_get_swagger_ui_init_js_embeds_openapi_url_and_defaults():
    response = fastapi_csp_docs.get_swagger_ui_init_js(openapi_url="/openapi.json")

    assert response.headers["content-type"].startswith("text/javascript")
    js = bytes(response.body).decode()
    assert "url: '/openapi.json'" in js
    assert '"dom_id": "#swagger-ui"' in js


def test_get_swagger_ui_init_js_includes_oauth2_redirect_url_when_set():
    js = bytes(
        fastapi_csp_docs.get_swagger_ui_init_js(
            openapi_url="/openapi.json",
            oauth2_redirect_url="/docs/oauth2-redirect",
        ).body
    ).decode()

    assert "oauth2RedirectUrl" in js
    assert "/docs/oauth2-redirect" in js


def test_get_swagger_ui_init_js_omits_oauth2_redirect_url_when_none():
    js = bytes(fastapi_csp_docs.get_swagger_ui_init_js(openapi_url="/openapi.json").body).decode()

    assert "oauth2RedirectUrl" not in js


def test_get_swagger_ui_init_js_escapes_html_special_characters():
    js = bytes(
        fastapi_csp_docs.get_swagger_ui_init_js(
            openapi_url="/openapi.json",
            swagger_ui_parameters={"customCss": "</script><script>alert(1)</script>"},
        ).body
    ).decode()

    assert "</script><script>" not in js
    assert "\\u003c/script\\u003e" in js


def test_get_redoc_html_has_no_inline_style():
    html = bytes(
        fastapi_csp_docs.get_redoc_html(
            openapi_url="/openapi.json",
            title="Test - ReDoc",
            redoc_css_url="/redoc/redoc.css",
        ).body
    ).decode()

    assert "<style>" not in html
    assert '<link rel="stylesheet" type="text/css" href="/redoc/redoc.css">' in html


def test_get_redoc_html_without_google_fonts_skips_font_link():
    html = bytes(
        fastapi_csp_docs.get_redoc_html(
            openapi_url="/openapi.json",
            title="Test - ReDoc",
            redoc_css_url="/redoc/redoc.css",
            with_google_fonts=False,
        ).body
    ).decode()

    assert "fonts.googleapis.com" not in html


def test_get_redoc_html_disable_search_adds_attribute():
    html = bytes(
        fastapi_csp_docs.get_redoc_html(
            openapi_url="/openapi.json",
            title="Test - ReDoc",
            redoc_css_url="/redoc/redoc.css",
            disable_search=True,
        ).body
    ).decode()

    assert '<redoc spec-url="/openapi.json" disable-search="true"></redoc>' in html


def test_get_redoc_html_search_enabled_by_default():
    html = bytes(
        fastapi_csp_docs.get_redoc_html(
            openapi_url="/openapi.json",
            title="Test - ReDoc",
            redoc_css_url="/redoc/redoc.css",
        ).body
    ).decode()

    assert "disable-search" not in html


def test_get_redoc_css_is_minimal_reset():
    response = fastapi_csp_docs.get_redoc_css()

    assert response.headers["content-type"].startswith("text/css")
    assert bytes(response.body).decode() == "body{margin:0;padding:0;}"


def test_get_swagger_ui_oauth2_redirect_html_has_no_inline_script():
    html = bytes(
        fastapi_csp_docs.get_swagger_ui_oauth2_redirect_html(
            oauth2_redirect_script_url="/docs/oauth2-redirect.js",
        ).body
    ).decode()

    assert "<script>" not in html
    assert '<script src="/docs/oauth2-redirect.js"></script>' in html


def test_get_swagger_ui_oauth2_redirect_js_is_nonempty():
    response = fastapi_csp_docs.get_swagger_ui_oauth2_redirect_js()

    assert response.headers["content-type"].startswith("text/javascript")
    js = bytes(response.body).decode()
    assert js.strip()
    assert "swaggerUIRedirectOauth2" in js
