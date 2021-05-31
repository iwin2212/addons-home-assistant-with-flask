FROM javishome/base

ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

COPY /hc/dist /dist/
COPY /hc/data /data_hc/
COPY /hc/static /static/
COPY /hc/templates /templates/
# RUN mkdir /etc/con-init.d
COPY ha_tool.sh /

#open port 2021 cho addon
EXPOSE 2021
#Run file shell sau khi start container
ENTRYPOINT [ "/ha_tool.sh" ]
