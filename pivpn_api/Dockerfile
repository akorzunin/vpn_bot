FROM python:3.11-buster

# pivpn_api port
EXPOSE 7070

# install speedtest-cli
RUN apt-get update; \
    apt-get install -y --no-install-recommends speedtest-cli

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

COPY requirements.txt /app

# Install dependencies
RUN pip install -r requirements.txt

COPY . /app

RUN adduser -u 5678 --disabled-password --gecos "" appuser

USER appuser

CMD ["python", "pivpn_app.py"]