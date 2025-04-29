FROM python:3.12.0
RUN pip install poetry
COPY pyproject.toml .
COPY poetry.lock .
RUN apt-get update && apt-get install libgl1 -y
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi
COPY . .