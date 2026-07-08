"""
OAuth2 "Authorize" flow: exercising the OAuth2 redirect endpoint fastapi_csp_docs.setup()
registers automatically whenever app.swagger_ui_oauth2_redirect_url is set (the default).

Swagger UI shows an "Authorize" button for any *path operation* that declares an OAuth2
security requirement (via Depends() on an OAuth2 scheme). Clicking it opens a popup that
round-trips through /docs/oauth2-redirect -- the CSP-safe page fastapi_csp_docs registers
instead of FastAPI's version, which embeds the same redirect logic as an inline <script>.

Run:

    uvicorn examples.oauth2_redirect_app:app --reload

Then open http://127.0.0.1:8000/docs, expand GET /protected, and click "Authorize": the
popup loads /docs/oauth2-redirect (HTML) and /docs/oauth2-redirect.js (JS) with no inline
<script> in either.
"""

from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2AuthorizationCodeBearer

import fastapi_csp_docs

from examples._csp import add_csp_header

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://example.com/oauth2/authorize",
    tokenUrl="https://example.com/oauth2/token",
)

app = FastAPI(
    title="OAuth2 Redirect Demo",
    docs_url=None,
    redoc_url=None,
    swagger_ui_init_oauth={
        "clientId": "demo-client-id",
        "usePkceWithAuthorizationCodeGrant": True,
    },
)
app.middleware("http")(add_csp_header)
fastapi_csp_docs.setup(app)


@app.get("/protected")
def read_protected(token: Annotated[str, Depends(oauth2_scheme)]) -> dict[str, str]:
    return {"token": token}
