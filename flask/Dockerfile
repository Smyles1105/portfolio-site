FROM python:3.9.10
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt
CMD ["uwsgi", "app.ini"]