FROM python:3.11-alpine AS build

WORKDIR /app

COPY . /app

RUN pip install -r ./requirements.txt

CMD ["python", "-m", "app"]