FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/app/ms-playwright

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install chromium --with-deps

COPY . .

EXPOSE 8000

CMD python manage.py collectstatic --noinput && python manage.py migrate && gunicorn plan_engine.wsgi --bind 0.0.0.0:8000
