"""
Root-path awareness: mounting a fastapi_csp_docs-enabled app as a sub-application.

fastapi_csp_docs.setup() computes every doc URL (openapi.json, swagger-initializer.js,
redoc.css, the OAuth2 redirect...) from the ASGI root_path at request time, not once at
setup() call time. sub_app below has no idea it will be mounted under /api -- root_path is
injected by Starlette's Mount machinery while routing each individual request -- yet its docs
still resolve every URL correctly under that prefix, exactly like FastAPI's own built-in docs
would.

For the other way an ASGI app learns its root_path -- FastAPI(root_path=...), typically set
when running behind a reverse proxy that strips a path prefix -- see root_path_app.py.

Run:

    uvicorn examples.mounted_subapp_app:app --reload

Then open http://127.0.0.1:8000/api/docs and http://127.0.0.1:8000/api/redoc: both correctly
reference /api/openapi.json, /api/docs/swagger-initializer.js, /api/redoc/redoc.css, etc.
"""

from fastapi import FastAPI

import fastapi_csp_docs

from examples._csp import add_csp_header

sub_app = FastAPI(title="Mounted Sub-App", docs_url=None, redoc_url=None)
sub_app.middleware("http")(add_csp_header)
fastapi_csp_docs.setup(sub_app)


@sub_app.get("/items")
def list_items() -> dict[str, list[str]]:
    return {"items": []}


app = FastAPI(title="Parent App")
app.mount("/api", sub_app)
