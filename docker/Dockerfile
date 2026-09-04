FROM python:3.12-slim

WORKDIR /app

# Consumer-only deps, copied first so the layer caches across code edits
COPY requirements-consumer.txt .
RUN pip install --no-cache-dir -r requirements-consumer.txt

# etl/ lands at /app so `python consumer.py` resolves and `import features` works
COPY etl/ .

# Unbuffered so print() shows up in `docker compose logs` immediately
ENV PYTHONUNBUFFERED=1

CMD ["python", "consumer.py"]
