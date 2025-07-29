#!/bin/bash

export VERSION=$(date '+%Y-%m-%d %H:%M:%S')

ls -l /app/clips
ls -l /app/uploads
pip install --upgrade yt-dlp
yt-dlp --rm-cache-dir
flask run --host=0.0.0.0 --port=5000
