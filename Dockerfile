FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app

RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# RUN flask db init

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV FLASK_APP=app.py

EXPOSE 5000

# Install ffmpeg for video processing
RUN apt-get update && apt-get install -y ffmpeg 

ENTRYPOINT ["/entrypoint.sh"]