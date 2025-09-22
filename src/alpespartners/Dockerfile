FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app/
WORKDIR /app
RUN pip install -e .
RUN mkdir -p /app/migrations/versions

# Install alembic globally for migrations
RUN pip install alembic

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
