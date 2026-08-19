FROM python:3.11-slim

WORKDIR /app

# Install dependencies from the root pyproject.toml
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy shared utilities and this service
COPY shared/ ./shared/
COPY preprocessing_service/ ./preprocessing_service/

EXPOSE 8001

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/')"

CMD ["uvicorn", "preprocessing_service.app.main:app", "--host", "0.0.0.0", "--port", "8001"]
