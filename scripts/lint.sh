#!/usr/bin/env bash

set -e
set -x

mypy fastapi_csp_docs examples
ty check fastapi_csp_docs examples
ruff check fastapi_csp_docs tests examples
ruff format fastapi_csp_docs tests examples --check
