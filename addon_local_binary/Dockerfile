FROM javishome/base

ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install python-pip && \
    pip install --no-cache-dir --upgrade pip && \
    pip install gitpython

COPY /hc/dist /dist/
COPY /hc/data /data_hc/
COPY /hc/static /static/
COPY /hc/templates /templates/
COPY ha_tool.sh /

EXPOSE 2021
ENTRYPOINT [ "/ha_tool.sh" ]
