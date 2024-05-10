FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
#ENV DJANGO_SETTINGS_MODULE=auth.settings

WORKDIR /auth-service-workdir

COPY ./requirements.txt .
RUN apk update && \
    apk add --no-cache netcat-openbsd postgresql-dev libpq && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del postgresql-dev && \
    rm -rf /var/cache/apk/*

COPY . .

COPY ./entrypoint.sh .
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]