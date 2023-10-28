FROM quay.io/centos/centos:stream9
LABEL system="django"

ENV RUNUSER=nginx
RUN dnf install -y gcc python3.11 python3.11-devel python3.11-pip python3.11-pip-wheel nginx
RUN alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    alternatives --install /usr/bin/pip pip /usr/bin/pip3.11 1
RUN mkdir -m 0760 /run/$RUNUSER && chown $RUNUSER:$RUNUSER /run/$RUNUSER
RUN pip install wheel supervisor uWSGI django
COPY etc /etc
USER $RUNUSER:$RUNUSER
COPY --chown=$RUNUSER:$RUNUSER manage.py /web/manage.py
COPY --chown=$RUNUSER:$RUNUSER hasker /web/hasker
RUN mkdir /web/log
EXPOSE 7777
CMD ["supervisord"]