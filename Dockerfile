FROM python:3.11-slim as builder

RUN apt-get update && \
    apt-get -y install libpq-dev gcc

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.11-slim

RUN apt-get update &&  \
    apt-get install -y libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1\
    PATH="/opt/venv/bin:$PATH"

COPY . /srv/zone-stats-aggregator
WORKDIR /srv/zone-stats-aggregator

CMD ["python", "./main.py"]