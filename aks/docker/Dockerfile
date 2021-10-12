FROM ubuntu:20.04

ARG EVENTHUB_CONSUMER_TOPIC_NAME
ARG EVENTHUB_PRODUCER_TOPIC_NAME
ARG SCHEMA_REGISTRY_GROUP
ARG EVENTHUB_HOSTNAME
ARG EVENTHUB_CONNECTION_STRING

ARG AZURE_CLIENT_ID
ARG AZURE_CLIENT_SECRET
ARG AZURE_USER_NAME
ARG AZURE_TENANT_ID

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && apt update && apt-get install -y apt-utils

RUN apt-get -y install python3-pip && apt install -y python3-venv && \
apt-get install sudo -y &&  apt install -y git && apt install wget


ENV EVENTHUB_CONSUMER_TOPIC_NAME ${EVENTHUB_CONSUMER_TOPIC_NAME}
ENV EVENTHUB_PRODUCER_TOPIC_NAME ${EVENTHUB_PRODUCER_TOPIC_NAME}
ENV SCHEMA_REGISTRY_GROUP ${SCHEMA_REGISTRY_GROUP}
ENV EVENTHUB_HOSTNAME ${EVENTHUB_HOSTNAME}
ENV EVENTHUB_CONNECTION_STRING ${EVENTHUB_CONNECTION_STRING}
ENV AZURE_CLIENT_ID ${AZURE_CLIENT_ID}
ENV AZURE_CLIENT_SECRET ${AZURE_CLIENT_SECRET}
ENV AZURE_USER_NAME ${AZURE_USER_NAME}
ENV AZURE_TENANT_ID ${AZURE_TENANT_ID}
ENV TZ=America/Los_Angeles

RUN cd /home && python3 -m venv serverenv
ADD /eventhubscore/server.py /home/server/server.py
ADD /eventhubscore/server.py /home/server/models.py
ENV VIRTUAL_ENV=/home/serverenv
RUN python3 -m venv ${VIRTUAL_ENV}
RUN pip install pip install azure-eventhub==5.6.0 && pip install azure.schemaregistry==1.0.0b2 && pip install pip install azure-schemaregistry-avroserializer==1.0.0b2 azure-identity && \
    pip install dataclasses-avroschema
ENTRYPOINT [ "python3", "/home/server/server.py"]
EXPOSE 80 443
