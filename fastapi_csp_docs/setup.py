from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response

from fastapi_csp_docs.docs import (
    get_redoc_css,
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_init_js,
    get_swagger_ui_oauth2_redirect_html,
    get_swagger_ui_oauth2_redirect_js,
)


def setup(
    app: FastAPI,
    *,
    docs_url: str | None = "/docs",
    redoc_url: str | None = "/redoc",
) -> None:
    """
    Wire CSP-safe Swagger UI and ReDoc routes onto a FastAPI app.

    Registers replacement routes for the interactive API docs (Swagger UI) and the
    alternative API docs (ReDoc) that load their JavaScript/CSS from dedicated endpoints
    instead of FastAPI's inline `<script>`/`<style>` tags, so a Content-Security-Policy
    without `'unsafe-inline'` can be enforced.

    The app must already be created with `docs_url=None`/`redoc_url=None`, e.g.
    `FastAPI(docs_url=None, redoc_url=None)` — otherwise FastAPI's own built-in docs
    would shadow the routes registered here.

    Read more about it in the
    [README](https://github.com/mat81black/fastapi-csp-docs#readme).

    :param app: the FastAPI app to wire the docs routes onto.
    :param docs_url: path to serve Swagger UI at, or None to skip it.
    :param redoc_url: path to serve ReDoc at, or None to skip it.
    :raises RuntimeError: if `app.docs_url` or `app.redoc_url` is still set.
    """
    if docs_url:
        if app.docs_url:
            raise RuntimeError(
                f"fastapi_csp_docs.setup() cannot mount Swagger UI at {docs_url!r} because "
                f"the app still serves its built-in docs at {app.docs_url!r}. Create the "
                "FastAPI app with docs_url=None to disable it first, e.g. FastAPI(docs_url=None)."
            )
        if app.openapi_url:
            _setup_swagger_ui(app, docs_url)
    if redoc_url:
        if app.redoc_url:
            raise RuntimeError(
                f"fastapi_csp_docs.setup() cannot mount ReDoc at {redoc_url!r} because "
                f"the app still serves its built-in docs at {app.redoc_url!r}. Create the "
                "FastAPI app with redoc_url=None to disable it first, e.g. FastAPI(redoc_url=None)."
            )
        if app.openapi_url:
            _setup_redoc(app, redoc_url)


def _setup_swagger_ui(app: FastAPI, docs_url: str) -> None:
    swagger_ui_init_script_url = f"{docs_url.rstrip('/')}/swagger-initializer.js"

    async def swagger_ui_init_script(req: Request) -> Response:
        root_path = req.scope.get("root_path", "").rstrip("/")
        openapi_url = root_path + app.openapi_url
        oauth2_redirect_url = app.swagger_ui_oauth2_redirect_url
        if oauth2_redirect_url:
            oauth2_redirect_url = root_path + oauth2_redirect_url
        return get_swagger_ui_init_js(
            openapi_url=openapi_url,
            oauth2_redirect_url=oauth2_redirect_url,
            init_oauth=app.swagger_ui_init_oauth,
            swagger_ui_parameters=app.swagger_ui_parameters,
        )

    app.add_route(
        swagger_ui_init_script_url,
        swagger_ui_init_script,
        include_in_schema=False,
    )

    async def swagger_ui_html(req: Request) -> HTMLResponse:
        root_path = req.scope.get("root_path", "").rstrip("/")
        init_script_url = root_path + swagger_ui_init_script_url
        return get_swagger_ui_html(
            title=f"{app.title} - Swagger UI",
            swagger_ui_init_script_url=init_script_url,
        )

    app.add_route(docs_url, swagger_ui_html, include_in_schema=False)

    if app.swagger_ui_oauth2_redirect_url:
        _setup_swagger_ui_oauth2_redirect(app, app.swagger_ui_oauth2_redirect_url)


def _setup_swagger_ui_oauth2_redirect(app: FastAPI, oauth2_redirect_url: str) -> None:
    oauth2_redirect_script_url = f"{oauth2_redirect_url.rstrip('/')}.js"

    oauth2_redirect_js_response = get_swagger_ui_oauth2_redirect_js()

    async def oauth2_redirect_script(req: Request) -> Response:
        return oauth2_redirect_js_response

    app.add_route(
        oauth2_redirect_script_url,
        oauth2_redirect_script,
        include_in_schema=False,
    )

    async def swagger_ui_redirect(req: Request) -> HTMLResponse:
        root_path = req.scope.get("root_path", "").rstrip("/")
        redirect_script_url = root_path + oauth2_redirect_script_url
        return get_swagger_ui_oauth2_redirect_html(
            oauth2_redirect_script_url=redirect_script_url,
        )

    app.add_route(
        oauth2_redirect_url,
        swagger_ui_redirect,
        include_in_schema=False,
    )


def _setup_redoc(app: FastAPI, redoc_url: str) -> None:
    redoc_css_url = f"{redoc_url.rstrip('/')}/redoc.css"

    redoc_css_response = get_redoc_css()

    async def redoc_css(req: Request) -> Response:
        return redoc_css_response

    app.add_route(redoc_css_url, redoc_css, include_in_schema=False)

    async def redoc_html(req: Request) -> HTMLResponse:
        root_path = req.scope.get("root_path", "").rstrip("/")
        openapi_url = root_path + app.openapi_url
        css_url = root_path + redoc_css_url
        return get_redoc_html(
            openapi_url=openapi_url,
            title=f"{app.title} - ReDoc",
            redoc_css_url=css_url,
        )

    app.add_route(redoc_url, redoc_html, include_in_schema=False)
