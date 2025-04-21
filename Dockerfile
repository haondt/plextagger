FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY plextagger ./plextagger
COPY run.sh .

ENV SCHEDULE_MINUTES=5

CMD ["./run.sh"]
