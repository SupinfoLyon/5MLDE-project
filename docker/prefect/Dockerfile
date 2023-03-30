FROM ubuntu:latest

WORKDIR /prefect/
EXPOSE 4200

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Paris
RUN apt-get update -y && apt-get install -y tzdata python3 python3-pip
RUN pip3 install prefect

RUN prefect config set PREFECT_API_URL=http://localhost:4200/api 

CMD prefect server start --host 0.0.0.0