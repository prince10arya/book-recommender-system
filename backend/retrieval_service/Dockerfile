FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY shared/ ./shared/
COPY retrieval_service/ ./retrieval_service/

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')"

CMD ["uvicorn", "retrieval_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
