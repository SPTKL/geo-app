FROM sptkl/docker-geosupport:19a-stretch

USER root

WORKDIR /usr/src/app

COPY . .

RUN pip3 install --upgrade pip\
    && pip3 install --no-cache-dir dash redis flask gunicorn pandas

EXPOSE 8050