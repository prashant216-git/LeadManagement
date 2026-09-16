
FROM python:3.12-slim


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /app


COPY requirement .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirement

# Copy full application source code including alembic
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]