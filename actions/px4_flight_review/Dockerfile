# Use an Ubuntu base image
FROM ubuntu:latest

# Set DEBIAN_FRONTEND to noninteractive
ENV DEBIAN_FRONTEND noninteractive

# Set environment variables to make Python run in unbuffered mode (recommended for Docker)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies required for Python 3.10
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-dev python3.10-distutils python3-pip && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    wget \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    bzip2 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3.10 -m pip install --upgrade pip

COPY requirements.runtime.txt ./
RUN python3.10 -m pip install --upgrade pip setuptools && python3.10 -m pip install -r requirements.runtime.txt

COPY src/px4_flight_review/ ./px4_flight_review
RUN python3.10 -m pip install -r /px4_flight_review/flight_review/app/requirements.txt

#COPY src/config_default.ini ./

ENV PYTHONPATH="${PYTHONPATH}:/px4_flight_review"
ENV PYTHONPATH="${PYTHONPATH}:/px4_flight_review/flight_review/app/plot_app/"

RUN mkdir -p /data/cache/

ENTRYPOINT [ "python3.10", "-m", "px4_flight_review" ]
