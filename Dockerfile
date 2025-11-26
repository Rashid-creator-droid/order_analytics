FROM python:3.10-slim
RUN pip install --upgrade pip \
    && pip install poetry

WORKDIR /app
COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

COPY . .

EXPOSE 8000


CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]