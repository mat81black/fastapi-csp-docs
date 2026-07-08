# Release Notes

## Latest Changes

## 0.1.1 (2026-07-08)

🚀 First official public release of **fastapi-csp-docs**.

FastAPI's built-in `/docs`, `/redoc`, and OAuth2 redirect pages embed inline `<script>`/`<style>`
tags, breaking any Content-Security-Policy without `'unsafe-inline'` — even FastAPI's own
["Custom Docs UI Static Assets"](https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/)
recipe only swaps CDN URLs for local ones, without removing that inline content.
`fastapi-csp-docs` replaces all three pages with versions that load every script and stylesheet
from a separate endpoint.

### Features

* ✨ `setup(app, *, docs_url="/docs", redoc_url="/redoc")`: one call replaces FastAPI's built-in
  `/docs`, `/redoc`, and OAuth2 redirect wiring, with no inline script or style left anywhere.
* ✨ Fails fast on misconfiguration: `setup()` raises `RuntimeError` if the app's built-in docs
  aren't disabled first, instead of silently letting them shadow the CSP-safe routes.
* ✨ CDN or fully self-hosted: works with the default jsdelivr CDN
  (`script-src 'self' <cdn-host>`) or entirely offline with your own static assets
  (`script-src 'self'`, zero external origins).
* ✨ Reverse-proxy / sub-app aware: doc URLs include the ASGI `root_path` computed per request,
  so mounting under a prefix (`app.mount("/api", sub_app)`) works out of the box.
* ✨ Content generators (`get_swagger_ui_html`, `get_swagger_ui_init_js`, `get_redoc_html`,
  `get_redoc_css`, `get_swagger_ui_oauth2_redirect_html`, `get_swagger_ui_oauth2_redirect_js`)
  exported for manual wiring, enabling a fully self-hosted setup with no CDN at all.
* ✨ `get_redoc_html(disable_search=True)`: disables ReDoc's client-side search box, avoiding
  the Web Worker it runs in — which otherwise needs `worker-src 'self' blob:` in the CSP, since
  the worker is instantiated from a `blob:` URL with no separate file to point at instead.
