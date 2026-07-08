"""
Shared CSP for the "assisted" examples (fastapi_csp_docs.setup() + CDN-hosted Swagger UI /
ReDoc bundles). Not a runnable example on its own -- see assisted_app.py,
mounted_subapp_app.py, oauth2_redirect_app.py, root_path_app.py, which all load the exact
same CDN assets via fastapi_csp_docs.setup()'s defaults and so need the exact same CSP.

self_hosted_app.py is deliberately NOT built on this: it self-hosts every asset instead of
using a CDN, so its CSP is different (no CDN/Google Fonts origins, CSP hashes instead of
pinned CDN URLs for the ReDoc runtime styles) and lives entirely in that file.
"""

from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.responses import Response

# These must match the defaults fastapi_csp_docs.setup() actually loads internally --
# get_swagger_ui_html()/get_redoc_html() in fastapi_csp_docs/docs.py. setup() doesn't accept
# custom asset URLs (see README "assisted mode" vs "manual mode"), so pinning the CSP to
# these exact files (rather than the whole cdn.jsdelivr.net origin, which hosts arbitrary npm
# packages) requires keeping this list in sync with those defaults by hand.
SWAGGER_JS_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"
SWAGGER_CSS_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css"
REDOC_JS_URL = "https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js"
FAVICON_URL = "https://fastapi.tiangolo.com/img/favicon.png"
# swagger-ui.css and redoc.standalone.js each end with a "/*# sourceMappingURL=... */" comment
# pointing at a sibling .map file (swagger-ui-bundle.js has none). DevTools only fetches these
# lazily, when a source file is actually inspected -- easy to miss testing without DevTools
# open -- but the request still goes out under connect-src (falls back to default-src if
# connect-src isn't set), so it needs pinning too.
SWAGGER_CSS_MAP_URL = f"{SWAGGER_CSS_URL}.map"
REDOC_JS_MAP_URL = f"{REDOC_JS_URL}.map"
REDOC_LOGO_URL = "https://cdn.redoc.ly/redoc/logo-mini.svg"
# CSP source matching ignores the query string, so the "?family=..." part of
# get_redoc_html()'s default google_fonts_css_url is dropped here -- the path alone is enough
# to pin this to that one endpoint.
GOOGLE_FONTS_CSS_URL = "https://fonts.googleapis.com/css"
# Google serves the actual font files under unpredictable, version-hashed filenames that vary
# per requested subset (see the requests captured in the browser network tab), so a path
# prefix is as precise as this can get -- a source ending in "/" matches everything under it.
GOOGLE_FONTS_STATIC_PREFIX = "https://fonts.gstatic.com/s/"

# ReDoc's UI is built with styled-components, which injects <style> tags into the page at
# runtime -- unrelated to the inline <script>/<style> tags fastapi_csp_docs removes from
# FastAPI's own generated HTML, and not something this package can eliminate (it's ReDoc's
# own rendering mechanism). A CSP hash allowlist is used to allow them without
# 'unsafe-inline': capture the exact 'sha256-...' values Chrome reports as blocked (DevTools
# console, or a report-uri/report-to endpoint) and add them here. This has to be redone
# whenever the ReDoc version changes, since the injected content can change.
REDOC_STYLE_HASHES = (
    "'sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU='",
    "'sha256-QMIg+bpjm3JdElJ388KYke01izlUW0UoNOeKjpMxdgc='",
)

CSP = (
    "default-src 'self'; "
    f"script-src 'self' {SWAGGER_JS_URL} {REDOC_JS_URL}; "
    f"style-src 'self' {SWAGGER_CSS_URL} {GOOGLE_FONTS_CSS_URL} {' '.join(REDOC_STYLE_HASHES)}; "
    # get_redoc_html() loads Google Fonts by default (with_google_fonts=True); see
    # self_hosted_app.py for an example that passes with_google_fonts=False instead of
    # whitelisting this origin.
    f"font-src 'self' {GOOGLE_FONTS_STATIC_PREFIX}; "
    # data: is for small SVG icons the Swagger UI bundle inlines as data URIs (e.g. the
    # server-select dropdown arrow). REDOC_LOGO_URL is for ReDoc's own "API docs by
    # Redocly" logo.
    f"img-src 'self' data: {FAVICON_URL} {REDOC_LOGO_URL}; "
    f"connect-src 'self' {SWAGGER_CSS_MAP_URL} {REDOC_JS_MAP_URL}; "
    # ReDoc runs its search indexing in a Web Worker, instantiated from a blob: URL (the
    # worker's whole source is inlined as a string in redoc.standalone.js, there's no separate
    # file to point a real URL at instead). Worker instantiation is governed by worker-src,
    # not script-src -- without it explicitly set, browsers fall back to script-src, which
    # never matches a blob: URL. setup() has no knob to disable ReDoc's search (and so avoid
    # the worker) -- it stays a plain docs_url/redoc_url toggle, like FastAPI's own. See
    # redoc_disable_search_app.py for the alternative: skip setup() for the ReDoc route and
    # call get_redoc_html(disable_search=True) manually instead, which needs no blob: here.
    "worker-src 'self' blob:"
)


async def add_csp_header(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = CSP
    return response
