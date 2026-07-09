from fastapi_csp_docs.docs import (
    get_redoc_css,
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_init_js,
    get_swagger_ui_oauth2_redirect_html,
    get_swagger_ui_oauth2_redirect_js,
)
from fastapi_csp_docs.setup import setup

__version__ = "0.1.2"

__all__ = [
    "get_redoc_css",
    "get_redoc_html",
    "get_swagger_ui_html",
    "get_swagger_ui_init_js",
    "get_swagger_ui_oauth2_redirect_html",
    "get_swagger_ui_oauth2_redirect_js",
    "setup",
]
