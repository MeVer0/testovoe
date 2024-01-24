FROM python:3.11

RUN mkdir /testovoe

WORKDIR /testovoe

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x scripts/*.sh
