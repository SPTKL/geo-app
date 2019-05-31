FROM sptkl/docker-geosupport:19a-api

USER root

WORKDIR /usr/src/app

COPY . .

# RUN pip install -r requirements.txt
RUN pip install --upgrade pip\
    && pip install dash redis flask gunicorn

RUN pip install pandas

EXPOSE 8050

# CMD ["gunicorn", "app:app", "--workers=4"]