# Note regarding python-alpine:
# https://dev.to/pmutua/the-best-docker-base-image-for-your-python-application-3o83
FROM python:3.12.2-slim

# This approximately follows this guide: https://hynek.me/articles/docker-uv/
# Which creates a standalone environment with the dependencies.
# - Silence uv complaining about not being able to use hard links,
# - tell uv to byte-compile packages for faster application startups,
# - prevent uv from accidentally downloading isolated Python builds,
# - pick a Python (use `/usr/bin/python3.12` on uv 0.5.0 and later),
# - and finally declare `/web` as the target for `uv sync`.
ENV UV_LINK_MODE=copy \
  UV_COMPILE_BYTECODE=1 \
  UV_PYTHON_DOWNLOADS=never \
  UV_PROJECT_ENVIRONMENT=/web/.venv

COPY --from=ghcr.io/astral-sh/uv:0.5.2 /uv /uvx /bin/

# Since there's no point in shipping lock files, we move them
# into a directory that is NOT copied into the runtime image.
# The trailing slash makes COPY create `/_lock/` automagically.
COPY README.md pyproject.toml uv.lock /_lock/

# This layer is cached until uv.lock or pyproject.toml change.
RUN --mount=type=cache,target=/root/.cache \
  cd /_lock && \
  uv sync \
  --all-extras

WORKDIR /web

ENV PATH="/web/.venv/bin:$PATH"

VOLUME ["/web"]
