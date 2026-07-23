# Release Notes

## Latest Changes

### Internal

* ⬆ Bump the python-packages group with 5 updates. PR [#18](https://github.com/mat81black/fastapi-csp-docs/pull/18) by [@dependabot[bot]](https://github.com/apps/dependabot).
* ⬆ Bump zizmorcore/zizmor-action from 0.5.7 to 0.6.0 in the github-actions group. PR [#17](https://github.com/mat81black/fastapi-csp-docs/pull/17) by [@dependabot[bot]](https://github.com/apps/dependabot).
* ⬆ Bump https://github.com/crate-ci/typos from v1.48.0 to 5.0.7 in the pre-commit group. PR [#15](https://github.com/mat81black/fastapi-csp-docs/pull/15) by [@dependabot[bot]](https://github.com/apps/dependabot).
* ⬆ Bump the github-actions group with 3 updates. PR [#16](https://github.com/mat81black/fastapi-csp-docs/pull/16) by [@dependabot[bot]](https://github.com/apps/dependabot).

## 0.1.3 (2026-07-10)

### Refactors

* ♻️ Align imports with FastAPI's public dependency contract. PR [#13](https://github.com/mat81black/fastapi-csp-docs/pull/13) by [@mat81black](https://github.com/mat81black).

### Internal

* 🔧 Add test coverage for setup()'s openapi and root_path edge cases. PR [#12](https://github.com/mat81black/fastapi-csp-docs/pull/12) by [@mat81black](https://github.com/mat81black).

## 0.1.2 (2026-07-09)

### Internal

* 🔧 Integrate Codecov for coverage tracking and update README. PR [#10](https://github.com/mat81black/fastapi-csp-docs/pull/10) by [@mat81black](https://github.com/mat81black).

## 0.1.1 (2026-07-08)

### Docs

* 📝 Update README badge styles and unwrap paragraphs. PR [#8](https://github.com/mat81black/fastapi-csp-docs/pull/8) by [@mat81black](https://github.com/mat81black).

## 0.1.0 (2026-07-08)

🚀 First official public release of **fastapi-csp-docs**.

FastAPI's built-in `/docs`, `/redoc`, and OAuth2 redirect pages embed inline `<script>`/`<style>` tags, breaking any Content-Security-Policy without `'unsafe-inline'`. Even FastAPI's own ["Custom Docs UI Static Assets"](https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/) recipe only swaps CDN URLs for local ones, without removing that inline content. `fastapi-csp-docs` replaces all three pages with versions that load every script and stylesheet from a separate endpoint.

### Features

* ✨ `setup(app, *, docs_url="/docs", redoc_url="/redoc")`: one call replaces FastAPI's built-in `/docs`, `/redoc`, and OAuth2 redirect wiring, with no inline script or style left anywhere.
* ✨ Fails fast on misconfiguration: `setup()` raises `RuntimeError` if the app's built-in docs aren't disabled first, instead of silently letting them shadow the CSP-safe routes.
* ✨ CDN or fully self-hosted: works with the default jsdelivr CDN (`script-src 'self' <cdn-host>`) or entirely offline with your own static assets (`script-src 'self'`, zero external origins).
* ✨ Reverse-proxy / sub-app aware: doc URLs include the ASGI `root_path` computed per request, so mounting under a prefix (`app.mount("/api", sub_app)`) works out of the box.
* ✨ Content generators (`get_swagger_ui_html`, `get_swagger_ui_init_js`, `get_redoc_html`, `get_redoc_css`, `get_swagger_ui_oauth2_redirect_html`, `get_swagger_ui_oauth2_redirect_js`) exported for manual wiring, enabling a fully self-hosted setup with no CDN at all.
* ✨ `get_redoc_html(disable_search=True)`: disables ReDoc's client-side search box, avoiding the Web Worker it runs in, which otherwise needs `worker-src 'self' blob:` in the CSP, since the worker is instantiated from a `blob:` URL with no separate file to point at instead.
