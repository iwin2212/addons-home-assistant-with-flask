FROM ubuntu:18.04

ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED=1
# Setup base
ARG BUILD_ARCH=amd64
# Install requirements for add-on
COPY requirements.txt /tmp/
RUN apt-get update \
    && apt-get install -y python3-pip python3-dev \
    && cd /usr/local/bin \
    && ln -s /usr/bin/python3 python \
    && pip3 --no-cache-dir install --upgrade pip \
    && rm -rf /var/lib/apt/lists/*\
    && pip3 install -r /tmp/requirements.txt
COPY run.sh /
COPY /hc/dist /dist/
COPY /hc/data /share/data_hc/
COPY /hc/static /static/
COPY /hc/templates /templates/

EXPOSE 2021
RUN chmod a+x /run.sh
CMD [ "/run.sh" ]