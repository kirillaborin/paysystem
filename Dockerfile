FROM python:3.7-slim

ENV TZ=Europe/Moscow

RUN apt-get -y update && \
	apt-get -y install python-dev python3-dev gcc libpq-dev

RUN pip install --no-cache-dir pylint==2.3.1 pylint-exit==1.0.0 pylint-django==2.0.8

COPY ./ /app/

WORKDIR /app/

RUN python3 -m pip install --upgrade pip -r /app/python-requirements.txt

CMD ["gunicorn", "paysystem.wsgi", "-b unix:/app/paysystem.sock", "--reload"]

