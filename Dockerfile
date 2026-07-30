FROM python:3.11-slim

WORKDIR /app

COPY dist/*.whl /tmp/

RUN pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp/*.whl

CMD ["python", "-m", "app"]