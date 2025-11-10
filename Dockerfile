FROM python:3
USER root

RUN apt-get update
RUN apt-get -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

RUN apt-get install -y vim less
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

RUN python -m pip install jupyterlab
RUN pip install flask
RUN pip install flask_sqlalchemy

COPY opt/ /opt/
WORKDIR /opt
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
CMD ["flask", "run"]