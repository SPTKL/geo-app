FROM sptkl/docker-geosupport:19a-api

USER root

WORKDIR /usr/src/app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8050

# CMD ["gunicorn", "app:app", "--workers=4"]