FROM python:3.9-buster

COPY requirements.txt requirements.txt
COPY src src

RUN ["pip","install","-r","requirements.txt"]
CMD ["python", "src/consumer.py"]