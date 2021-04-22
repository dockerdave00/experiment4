  
# start from base
FROM python:3

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 5000

CMD [ "python", "./app.py" ]
