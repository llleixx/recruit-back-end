FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install -i 'http://mirrors.cloud.aliyuncs.com/pypi/simple/' --no-cache-dir --upgrade -r /code/requirements.txt

EXPOSE 8000

COPY ./.env /code/.env

COPY ./app /code/app

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0"]