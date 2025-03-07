#                                                                                                               Base-Image for python server (backend)
#-----------------------------------------------------------------------------------------------------------------------------------------------------
ARG DEBIAN_VERSION
FROM debian:${DEBIAN_VERSION} AS base-image

#   Definition der lokalen Variablen innerhalb dieses Stage.
ARG DOCKER_CONTAINER_WORKDIR

#   Aktuelles Arbeitsverzeichnis festlegen.
WORKDIR ${DOCKER_CONTAINER_WORKDIR}


#                                                                                                                                       Build Frontend
#-----------------------------------------------------------------------------------------------------------------------------------------------------
FROM node:23-alpine AS build-frontend

ARG BUILD_OUTPUT_DIR
ARG DOCKER_CONTAINER_WORKDIR

ENV BUILD_OUTPUT_DIR=.output

WORKDIR ${DOCKER_CONTAINER_WORKDIR}

#   Kopiere die Frontend App, installiere die Abhängigkeiten und generiere die statischen Dateien.
COPY ./frontend ./frontend
COPY .env .

WORKDIR ${DOCKER_CONTAINER_WORKDIR}/frontend

RUN npm install
RUN npm run generate


#                                                                                                                                         Preparations
#-----------------------------------------------------------------------------------------------------------------------------------------------------
FROM base-image AS preparations

# Installieren verschiedener Standardprogramme.
RUN apt-get update && \
    apt-get install -y \
        dos2unix \
        htop \
        mc \
        nano \
        zip 

# Installieren von benötigten Debain packages
RUN apt-get install -y \
        python3 \
        python3-venv \
        gdal-bin

#                                                                                                                                              Locales
#-----------------------------------------------------------------------------------------------------------------------------------------------------
FROM preparations AS locales

#   Definition der lokalen Variablen innerhalb dieses Stage.
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
        apt-utils \
        locales \
        tzdata

#   Standorteinstellungen, Kodierung und Zeitzone definieren.
RUN dpkg-reconfigure tzdata && \
    sed -i -e 's/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen && \
    echo 'LANG="de_DE.UTF-8"' > /etc/default/locale && \
    locale-gen de de_DE de_DE.UTF-8 && \
    dpkg-reconfigure locales && \
    update-locale LANG=de_DE.UTF-8

#                                                                                                                          Install python dependencies
#-----------------------------------------------------------------------------------------------------------------------------------------------------
FROM locales AS python-dependencies

ARG DOCKER_CONTAINER_WORKDIR

WORKDIR ${DOCKER_CONTAINER_WORKDIR}

#   Erstelle ein virtuelles Environment und aktiviere es.
RUN python3 -m venv --system-site-packages ./.venv
RUN . ./.venv/bin/activate
ENV PATH="${DOCKER_CONTAINER_WORKDIR}/.venv/bin:$PATH"
ENV PROJ_DIR="${DOCKER_CONTAINER_WORKDIR}/proj"

#   Installiere die Abhängigkeiten für das Virtual Environment.
WORKDIR ${DOCKER_CONTAINER_WORKDIR}/server

COPY ./server/requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt
RUN pip install uvloop

COPY ./server .

#                                                                                                                                Finalized Application
#-----------------------------------------------------------------------------------------------------------------------------------------------------
FROM python-dependencies AS finalized-application

#   Definition der lokalen Variablen innerhalb dieses Stage.
ARG DOCKER_CONTAINER_WORKDIR
ARG BUILD_OUTPUT_DIR
ARG APP_ENV

#   Aktuelles Arbeitsverzeichnis festlegen.
WORKDIR ${DOCKER_CONTAINER_WORKDIR}

ENV PYTHONPATH="${DOCKER_CONTAINER_WORKDIR}"
ENV APP_ENV="${APP_ENV}"
ENV PROJ_DIR="${DOCKER_CONTAINER_WORKDIR}/proj"

#   Kopiere die gebaute Anwendung und die Abhängigkeiten in das finale Image.
COPY --from=build-frontend ${DOCKER_CONTAINER_WORKDIR}/frontend/.output ${DOCKER_CONTAINER_WORKDIR}/server/web/static
#   Kopiere das startup.sh Skript in das finale Image.
COPY ./server-startup.sh .

ENTRYPOINT [ "./server-startup.sh" ]