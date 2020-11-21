FROM python:3.9-buster

COPY requirements.txt requirements.txt
COPY src src

RUN ["pip","install","-r","requirements.txt"]
WORKDIR /src
EXPOSE 8000
CMD ["gunicorn","-b","0.0.0.0:8000","api:api"]