FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY shared/ ./shared/
COPY embedding_service/ ./embedding_service/

EXPOSE 8002

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8002/')"

CMD ["uvicorn", "embedding_service.app.main:app", "--host", "0.0.0.0", "--port", "8002"]
