# HF Spaces (Docker SDK). Build context = the Space's OWN git repo, which mirrors
# the relative folder depth pipeline.py expects (src/ and dashboard/backend/app/
# at the same level) - see README.md "Deploy ke HF Spaces" for exactly which files
# to copy into that separate repo before pushing. Do NOT point this at the PI2
# monorepo directly; models/ and the full src/ tree are intentionally not included.
FROM python:3.11-slim

RUN useradd -m -u 1000 user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR /app

COPY --chown=user:user dashboard/backend/requirements.txt ./dashboard/backend/requirements.txt
USER user
RUN pip install --no-cache-dir --user -r dashboard/backend/requirements.txt

COPY --chown=user:user src/ ./src/
COPY --chown=user:user dashboard/backend/app/ ./dashboard/backend/app/

EXPOSE 7860

CMD ["python", "-m", "uvicorn", "dashboard.backend.app.main:app", "--host", "0.0.0.0", "--port", "7860"]
