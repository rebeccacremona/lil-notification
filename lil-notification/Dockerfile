FROM python:3.6.5-stretch
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /lil-notification/lil-notification
WORKDIR /lil-notification/lil-notification
ADD requirements.txt /lil-notification/lil-notification/
RUN pip install -U pip; pip install -r requirements.txt
