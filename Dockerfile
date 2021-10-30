FROM python:3.7

WORKDIR /usr/src/app

RUN apt update && apt install jq -y

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY init.py config.default.json /usr/src/app/
COPY cogs /usr/src/app/cogs
COPY core /usr/src/app/core

COPY docker /usr/src/app/docker

RUN chmod +x ./docker/run.sh

ENV PYTHONUNBUFFERED=1
CMD ["./docker/run.sh"]
