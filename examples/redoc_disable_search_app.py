"""
Manual ReDoc wiring: disabling search to avoid the Web Worker/blob: CSP entirely.

setup() intentionally has no CSP-specific parameters -- it mirrors FastAPI's own
docs_url/redoc_url surface, nothing more. Disabling ReDoc's search box (and the Web Worker it
runs in, which otherwise needs `worker-src 'self' blob:` -- see assisted_app.py) is a ReDoc
rendering choice, not something setup() should grow a parameter for. So: use setup() for
Swagger UI as usual, skip it for ReDoc (redoc_url=None), and wire the ReDoc route manually
with get_redoc_html(disable_search=True) instead.

Run:

    uvicorn examples.redoc_disable_search_app:app --reload

Then open http://127.0.0.1:8000/redoc: no search box, no Web Worker, so worker-src can stay a
plain 'self' with no blob: -- compare CSP with assisted_app.py's, identical except for that
one directive.
"""

from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse, Response

import fastapi_csp_docs

from examples._csp import (
    FAVICON_URL,
    GOOGLE_FONTS_CSS_URL,
    GOOGLE_FONTS_STATIC_PREFIX,
    REDOC_JS_MAP_URL,
    REDOC_JS_URL,
    REDOC_LOGO_URL,
    REDOC_STYLE_HASHES,
    SWAGGER_CSS_MAP_URL,
    SWAGGER_CSS_URL,
    SWAGGER_JS_URL,
)

# Same as _csp.py's CSP, except worker-src drops blob: -- ReDoc's search worker is never
# created when disable_search=True is passed to get_redoc_html() below.
CSP = (
    "default-src 'self'; "
    f"script-src 'self' {SWAGGER_JS_URL} {REDOC_JS_URL}; "
    f"style-src 'self' {SWAGGER_CSS_URL} {GOOGLE_FONTS_CSS_URL} {' '.join(REDOC_STYLE_HASHES)}; "
    f"font-src 'self' {GOOGLE_FONTS_STATIC_PREFIX}; "
    f"img-src 'self' data: {FAVICON_URL} {REDOC_LOGO_URL}; "
    f"connect-src 'self' {SWAGGER_CSS_MAP_URL} {REDOC_JS_MAP_URL}; "
    "worker-src 'self'"
)

app = FastAPI(
    title="ReDoc Disable Search Demo",
    docs_url=None,
    redoc_url=None,
)

if app.openapi_url is None:
    raise RuntimeError("this example requires openapi_url")
openapi_url = app.openapi_url


@app.middleware("http")
async def add_csp_header(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = CSP
    return response


fastapi_csp_docs.setup(app, redoc_url=None)  # ReDoc wired manually below instead


@app.get("/redoc/redoc.css", include_in_schema=False)
async def redoc_css() -> Response:
    return fastapi_csp_docs.get_redoc_css()


@app.get("/redoc", include_in_schema=False)
async def redoc_html() -> HTMLResponse:
    return fastapi_csp_docs.get_redoc_html(
        openapi_url=openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_css_url="/redoc/redoc.css",
        disable_search=True,
    )


@app.get("/items")
def list_items() -> dict[str, list[str]]:
    return {"items": []}
