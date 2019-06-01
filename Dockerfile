FROM sptkl/docker-geosupport:19a-api

USER root

WORKDIR /usr/src/app

COPY . .

RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories

RUN pip3 install --upgrade pip

RUN pip3 install --no-cache-dir dash redis flask gunicorn

RUN pip3 install --no-cache-dir pandas

EXPOSE 8050

# CMD ["gunicorn", "app:app", "--workers=4"]