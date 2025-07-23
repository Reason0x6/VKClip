# Clipar

Clipar is a web application for creating video clips with precise time segments. Users can upload videos, download videos from URLs, or use existing videos to define clips and time segments.

## Features
- Upload video files or download videos from URLs.
- Define multiple clips with custom names and precise time segments.
- View and manage existing clips.
- Clear all clips with a single action.

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd clipar
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open the application in your browser at `http://localhost:5000`.

## Dependencies
- Flask: Web framework for building the application.
- yt-dlp: For downloading videos from URLs.
- ffmpeg: For processing video clips.

## Usage
1. Select a video source (upload, URL, or existing video).
2. Define clips and time segments.
3. Process and download the clips.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License.
