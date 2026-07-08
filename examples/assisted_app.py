"""
Assisted mode: fastapi_csp_docs.setup() + CDN-hosted Swagger UI / ReDoc bundles.

This removes the inline <script>/<style> tags that FastAPI's default /docs and /redoc
pages embed, so a CSP without 'unsafe-inline' works. The Swagger UI / ReDoc JS and CSS
bundles are still loaded from the jsdelivr CDN, so the CSP whitelists the exact file URLs
(not the whole cdn.jsdelivr.net origin, which hosts arbitrary npm packages) instead of
falling back to 'unsafe-inline'. See _csp.py for the full CSP and why each directive is
there.

For a fully self-hosted setup with no external origins at all, see self_hosted_app.py.

Run:

    uvicorn examples.assisted_app:app --reload

Then open http://127.0.0.1:8000/docs and http://127.0.0.1:8000/redoc: both render fully under
this CSP, with no 'unsafe-inline' anywhere.
"""

from fastapi import FastAPI

import fastapi_csp_docs

from examples._csp import add_csp_header

app = FastAPI(
    title="Assisted CSP Docs API",
    docs_url=None,
    redoc_url=None,
)
app.middleware("http")(add_csp_header)

fastapi_csp_docs.setup(app)


@app.get("/items")
def list_items() -> dict[str, list[str]]:
    return {"items": []}
