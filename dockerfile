FROM python:latest


WORKDIR /app

COPY ./requirements.txt /app/

RUN pip3 install -r requirements.txt

COPY . /app

EXPOSE 5000

CMD [ "python","app.py" ]