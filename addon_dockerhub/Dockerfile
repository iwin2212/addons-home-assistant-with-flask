FROM javishome/base

ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED=1

COPY /hc/dist /dist/
COPY /hc/data /data_hc/
COPY /hc/static /static/
COPY /hc/templates /templates/
# RUN mkdir /etc/con-init.d
COPY ha_tool.sh /

EXPOSE 2021
ENTRYPOINT [ "/ha_tool.sh" ]