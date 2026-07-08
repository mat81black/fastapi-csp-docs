#!/usr/bin/env bash
set -x

ruff check fastapi_csp_docs tests examples --fix
ruff format fastapi_csp_docs tests examples
