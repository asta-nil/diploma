FROM python:3.10 as builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache -r requirements.txt

COPY . /app/

EXPOSE 5000

CMD python3 api.py