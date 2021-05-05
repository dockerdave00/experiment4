  
# start from base
FROM python:3

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 5432

EXPOSE 5000

COPY . /app

CMD [ "python", "./app.py" ]
