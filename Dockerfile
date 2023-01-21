# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11-bullseye

EXPOSE ${PORT}

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.2.0 

WORKDIR /app

# Install dependencies
RUN pip install "poetry==$POETRY_VERSION"

# Copy only dependencies file to cache them in docker layer
COPY poetry.lock pyproject.toml /app/

# install dev dependencies if DEBUG set to True
ARG DEBUG=${DEBUG}
RUN if [ "${DEBUG}" != "True" ] ; then \
    poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --without dev; \
    else poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi  --with dev; fi

COPY . /app

# create database file if not exist
RUN mkdir -p ./data && touch ./data/db.json

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser \
    && chown -R appuser /app 

USER root

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "main.py"]
