FROM python:3.7

ENV RUN_HOST="0.0.0.0"
ENV RUN_PORT=80

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt 

COPY . /usr/src/app

EXPOSE 80

ENTRYPOINT ["python3"]

CMD ["main.py"]
