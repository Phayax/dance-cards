FROM ubuntu:24.04
SHELL ["/bin/bash", "-c"]

# --- Set up locale
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y locales

RUN sed -i -e 's/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=de_DE.UTF-8

ENV LANG=de_DE.UTF-8 

RUN apt-get install -y python3-dev \
                       python3-pip


RUN python3 -m pip config set global.break-system-packages true

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# --- QT setup
ENV QT_DEBUG_PLUGINS=1
RUN apt-get install -y libxcb-icccm4-dev \
 libxcb-image0-dev \
 libxcb-keysyms1-dev \
 libxcb-render-util0-dev \
 libxcb-shape0-dev \
 libxcb-xinerama0-dev

# --- Xforwarding
RUN apt-get install -y mesa-utils

WORKDIR /
CMD python3 /dance-cards/multi-gui.py
