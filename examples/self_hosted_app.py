"""
Manual mode: fully self-hosted docs, one unavoidable external origin for ReDoc's own logo.

Same wiring mechanics as the official FastAPI recipe for "Custom Docs UI Static Assets"
(https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/) — direct @app.get() endpoints,
no fastapi_csp_docs.setup() — but built from this package's content generators instead of
fastapi.openapi.docs, so script-src stays 'self' with no CDN and no external origins at all.

Vendor bundles (swagger-ui-bundle.js, swagger-ui.css, redoc.standalone.js, favicon.png) are
committed under examples/static/ — nothing to download.

Run:

    uvicorn examples.self_hosted_app:app --reload

Then open http://127.0.0.1:8000/docs and http://127.0.0.1:8000/redoc: both render fully, with
img-src the only directive listing an external origin (see REDOC_LOGO_URL below).
"""

from collections.abc import Awaitable, Callable
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse, Response

import fastapi_csp_docs

STATIC_DIR = Path(__file__).parent / "static"

# ReDoc's UI is built with styled-components, which injects <style> tags into the page at
# runtime regardless of how its HTML/CSS are served -- a ReDoc rendering requirement,
# unrelated to the inline <script>/<style> tags fastapi_csp_docs removes from FastAPI's own
# generated HTML. Allowed here via a CSP hash allowlist (capture the exact 'sha256-...'
# values Chrome reports as blocked, e.g. via DevTools console or a report-to endpoint), not
# 'unsafe-inline' -- this has to be redone whenever the ReDoc version changes. script-src
# stays 'self' with zero external origins, which is what "fully self-hosted" refers to here.
REDOC_STYLE_HASHES = (
    "'sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU='",
    "'sha256-QMIg+bpjm3JdElJ388KYke01izlUW0UoNOeKjpMxdgc='",
)

# ReDoc's "API docs by Redocly" logo hardcodes an absolute cdn.redoc.ly URL with no override
# option (https://github.com/Redocly/redoc/issues/2141). There's no CSP hash mechanism for
# images (hash-source only applies to script-src/style-src), so whitelisting the origin in
# img-src is the only way to allow it -- and since data: is already needed there for the small
# SVG icons the Swagger UI bundle inlines, adding one more explicit origin costs nothing extra
# in practice. This ends up being the one external origin in an otherwise fully self-hosted CSP.
REDOC_LOGO_URL = "https://cdn.redoc.ly/redoc/logo-mini.svg"

CSP = (
    "default-src 'self'; script-src 'self'; "
    f"style-src 'self' {' '.join(REDOC_STYLE_HASHES)}; "
    f"img-src 'self' data: {REDOC_LOGO_URL}; "
    # ReDoc only runs its search indexing in a Web Worker when search is enabled -- it's
    # instantiated from a blob: URL (the worker's whole source is inlined as a string in
    # redoc.standalone.js, there's no separate file to point a real URL at instead), true
    # regardless of whether redoc.standalone.js itself is self-hosted or CDN-hosted. Rather
    # than allow blob: workers, get_redoc_html() below is called with disable_search=True,
    # which skips building the search index entirely, so the worker is never created and
    # this can stay 'self' with no blob: -- see the README section on worker-src.
    "worker-src 'self'"
)

app = FastAPI(
    title="Self-Hosted CSP Docs API",
    docs_url=None,
    redoc_url=None,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if app.openapi_url is None or app.swagger_ui_oauth2_redirect_url is None:
    raise RuntimeError("this example requires both openapi_url and swagger_ui_oauth2_redirect_url")
openapi_url = app.openapi_url
oauth2_redirect_url = app.swagger_ui_oauth2_redirect_url


@app.middleware("http")
async def add_csp_header(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = CSP
    return response


# --- Swagger UI ---------------------------------------------------------------------
# This example doesn't handle the ASGI root_path (sub-app mounting behind a prefix);
# fastapi_csp_docs.setup() does, by reading request.scope["root_path"] per request —
# add that here too if you mount this app under a parent app or a reverse proxy.


@app.get("/docs/swagger-initializer.js", include_in_schema=False)
async def swagger_ui_init_script() -> Response:
    return fastapi_csp_docs.get_swagger_ui_init_js(
        openapi_url=openapi_url,
        oauth2_redirect_url=oauth2_redirect_url,
    )


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html() -> HTMLResponse:
    return fastapi_csp_docs.get_swagger_ui_html(
        title=f"{app.title} - Swagger UI",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url="/static/favicon.png",
        swagger_ui_init_script_url="/docs/swagger-initializer.js",
    )


oauth2_redirect_script_url = f"{oauth2_redirect_url.rstrip('/')}.js"


@app.get(oauth2_redirect_script_url, include_in_schema=False)
async def oauth2_redirect_script() -> Response:
    return fastapi_csp_docs.get_swagger_ui_oauth2_redirect_js()


@app.get(oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect() -> HTMLResponse:
    # Deliberately NOT fastapi.openapi.docs.get_swagger_ui_oauth2_redirect_html() —
    # that one embeds the redirect logic as an inline <script>, which would reintroduce
    # the exact inline script this package exists to remove. Use this package's variant,
    # which references the separate oauth2-redirect.js endpoint above instead.
    return fastapi_csp_docs.get_swagger_ui_oauth2_redirect_html(
        oauth2_redirect_script_url=oauth2_redirect_script_url,
    )


# --- ReDoc ---------------------------------------------------------------------------


@app.get("/redoc/redoc.css", include_in_schema=False)
async def redoc_css() -> Response:
    return fastapi_csp_docs.get_redoc_css()


@app.get("/redoc", include_in_schema=False)
async def redoc_html() -> HTMLResponse:
    return fastapi_csp_docs.get_redoc_html(
        openapi_url=openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
        redoc_favicon_url="/static/favicon.png",
        with_google_fonts=True,
        google_fonts_css_url="/static/fonts.css",
        redoc_css_url="/redoc/redoc.css",
        disable_search=True,
    )


@app.get("/items")
def list_items() -> dict[str, list[str]]:
    return {"items": []}
