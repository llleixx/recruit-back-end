FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

EXPOSE 8000

ENV MYSQL_USER='root' MYSQL_PASSWORD='abcd' \
    MYSQL_HOST='172.17.0.1'

COPY ./app /code/app

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0"]