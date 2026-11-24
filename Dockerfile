
# Image officielle Python 3.11 slim-bookworm, figée par digest.
FROM python:3.11-slim-bookworm@sha256:a83ba18aef0f865b1a4a611c2cf460fe446f2795673bbb9fe43be570439e3b39

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN python -m pip install --no-cache-dir setuptools==80.9.0

COPY pyproject.toml README.md ./
COPY src/ ./src/

# Installation du projet et de ses dépendances.
RUN python -m pip install --no-cache-dir -e .

COPY tests/ ./tests/

# Exécution sans privilèges root.
USER 10001:10001

CMD ["python", "-m", "irrigation_edge_ai"]
