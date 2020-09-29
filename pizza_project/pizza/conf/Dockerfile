FROM python:3.5
RUN apt-get update -y && apt-get install supervisor -y
ADD conf/supervisor.conf /etc/supervisor/conf.d/celery.conf
ENV APP_DIR /app
ENV USER_APP www-data
WORKDIR ${APP_DIR}
RUN mkdir /logs && chown ${USER_APP}:${USER_APP} /logs -R
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt && pip install uwsgi
USER ${USER_APP}
EXPOSE 8000
CMD uwsgi ${APP_DIR}/conf/uwsgi.ini
