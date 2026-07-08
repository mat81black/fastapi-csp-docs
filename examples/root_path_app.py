"""
Root-path awareness: FastAPI(root_path=...), the reverse-proxy way of setting root_path.

Set this when the app runs behind a reverse proxy that strips a path prefix before
forwarding the request (e.g. nginx `location /api/ { proxy_pass http://app/; }`, or
Uvicorn's `--root-path` flag) -- the app itself only ever sees paths without that prefix, but
needs to know about it to generate correct absolute URLs. fastapi_csp_docs.setup() reads
request.scope["root_path"] per request, so every doc URL (openapi.json,
swagger-initializer.js, redoc.css, the OAuth2 redirect...) comes out correctly prefixed too,
exactly like FastAPI's own built-in docs would.

For the other way an ASGI app learns its root_path -- mounting a sub-app with
app.mount(prefix, sub_app) -- see mounted_subapp_app.py.

Run:

    uvicorn examples.root_path_app:app --reload

Then open http://127.0.0.1:8000/docs and http://127.0.0.1:8000/redoc directly: even though
nothing proxies this app in this example, root_path="/api" alone is enough to see every doc
URL come out prefixed with /api (openapi.json link, Swagger UI's "Servers" dropdown,
swagger-initializer.js, redoc.css).
"""

from fastapi import FastAPI

import fastapi_csp_docs

from examples._csp import add_csp_header

app = FastAPI(
    title="Root Path Demo",
    docs_url=None,
    redoc_url=None,
    root_path="/api",
)
app.middleware("http")(add_csp_header)
fastapi_csp_docs.setup(app)


@app.get("/items")
def list_items() -> dict[str, list[str]]:
    return {"items": []}
