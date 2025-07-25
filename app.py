import os
import subprocess
import uuid
import re
import threading
import time
import shutil
import json
from flask import (Flask, request, redirect, url_for, render_template,
                   send_from_directory, flash, jsonify, Response)
from werkzeug.utils import secure_filename
import os
import uuid
import subprocess
import threading
import time
import json
import re
import shutil

app = Flask(__name__)

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
CLIPS_FOLDER = 'clips'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CLIPS_FOLDER'] = CLIPS_FOLDER
app.secret_key = 'a_very_secret_key_for_production'

# Global dictionary to store download progress
download_progress = {}

# Global dictionary to store clip processing progress
clip_progress = {}

# --- Helper Functions ---
def allowed_file(filename):
    """Checks if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_folders():
    """Creates the necessary upload and clips folders if they don't exist."""
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CLIPS_FOLDER'], exist_ok=True)

def get_video_duration(filepath):
    """Get video duration using ffprobe."""
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', filepath
        ], capture_output=True, text=True, check=True)
        duration_seconds = float(result.stdout.strip())
        
        # Convert to hours:minutes:seconds.milliseconds format
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)
        milliseconds = int((duration_seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    
    except:
        return "Unknown"

def process_clip(original_filepath, clip_filepath, command):
    """Process a video clip using ffmpeg command."""
    try:
        print(f"Running command: {' '.join(command)}")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Command stdout: {result.stdout}")
        print(f"Command stderr: {result.stderr}")
        return {'status': 'success', 'clip_filepath': clip_filepath}
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e.stderr.strip()}")
        return {'status': 'error', 'message': e.stderr.strip()}

def download_video_from_url(url, download_path, download_id):
    """Download video from URL using yt-dlp with real-time progress tracking."""

    def update_progress(stage, percent, message=""):
        download_progress[download_id] = {
            'stage': stage,
            'percent': percent,
            'message': message
        }

    def progress_hook(d):
        """Progress hook for yt-dlp to track download progress."""
        if d['status'] == 'downloading':
            # Extract percentage from yt-dlp
            if '_percent_str' in d:
                import re
                percent_str = re.sub(r'\x1b\[[0-9;]*m', '', d['_percent_str']).strip().replace('%', '')
                try:
                    percent = float(percent_str)
                except (ValueError, TypeError):
                    percent = 0
            else:
                percent = 0

            speed = d.get('_speed_str', 'Unknown')
            eta = d.get('_eta_str', 'Unknown')

            if speed != 'Unknown':
                speed = re.sub(r'\x1b\[[0-9;]*m', '', speed).strip()
            if eta != 'Unknown':
                eta = re.sub(r'\x1b\[[0-9;]*m', '', eta).strip()

            message = f"Downloading... {percent:.1f}% (Speed: {speed}, ETA: {eta})"
            update_progress('downloading', percent, message)

        elif d['status'] == 'finished':
            update_progress('processing', 95, 'Download finished, processing...')

    try:
        update_progress('starting', 0, 'Preparing download...')

        try:
            import yt_dlp
        except ImportError:
            return download_video_subprocess(url, download_path, download_id)

        unique_id = str(uuid.uuid4())
        output_template = os.path.join(download_path, f"%(title)s.%(ext)s")

        ydl_opts = {
            'format': 'bv*+ba/b',
            'outtmpl': output_template,
            'noplaylist': True,
            'progress_hooks': [progress_hook],
        }

        update_progress('downloading', 0, 'Starting download...')

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        downloaded_files = []
        for file in os.listdir(download_path):
            if file.endswith(('.mp4', '.mkv', '.webm', '.avi', '.mov')):
                downloaded_files.append(file)

        if not downloaded_files:
            update_progress('error', 0, 'No files were downloaded')
            return {'status': 'error', 'message': 'No files were downloaded'}

        downloaded_file = downloaded_files[0]
        downloaded_path = os.path.join(download_path, downloaded_file)

        update_progress('complete', 100, 'Download complete!')

        return {'status': 'success', 'filepath': downloaded_path, 'filename': downloaded_file}

    except Exception as e:
        update_progress('error', 0, f'Download error: {str(e)}')
        return {'status': 'error', 'message': f'Download error: {str(e)}'}

def download_video_subprocess(url, download_path, download_id):
    """Fallback download method using subprocess when yt-dlp module is not available."""
    def update_progress(stage, percent, message=""):
        download_progress[download_id] = {
            'stage': stage,
            'percent': percent,
            'message': message
        }
    
    try:
        # Initialize progress
        update_progress('starting', 0, 'Preparing download...')
        
        # Generate filenames
        unique_id = str(uuid.uuid4())
        video_template = os.path.join(download_path, f"{unique_id}")
        filename = f"{unique_id}.mp4"
        
        # Download best video stream
        update_progress('downloading', 25, 'Downloading video...')
        video_command = [
            'yt-dlp',
            '-f', 'bv*+ba/b',
            '-S', 'res,filesize',
            '--output', video_template,
            '--no-playlist',
            url
        ]
        print(f"Running video download command: {' '.join(video_command)}")
        subprocess.run(video_command, capture_output=True, text=True, check=True)
        
        update_progress('complete', 100, 'Download complete!')
        
        return {'status': 'success', 'filepath': video_template, 'filename': filename}
   
    except Exception as e:
        update_progress('error', 0, f'Download error: {str(e)}')
        return {'status': 'error', 'message': f'Download error: {str(e)}'}

def is_valid_url(url):
    """Check if the provided string is a valid URL."""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

# --- Routes ---
@app.route('/')
def index():
    """Renders the main page with the form and the list of existing clips."""
    try:
        clip_files = [f for f in os.listdir(app.config['CLIPS_FOLDER']) if allowed_file(f)]
        clips = sorted(
            clip_files,
            key=lambda f: os.path.getmtime(os.path.join(app.config['CLIPS_FOLDER'], f)),
            reverse=True
        )
    except FileNotFoundError:
        clips = []
    
    # Get both clips and uploaded videos for selection dropdown
    try:
        upload_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if allowed_file(f)]
        uploads = sorted(
            upload_files,
            key=lambda f: os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], f)),
            reverse=True
        )
    except FileNotFoundError:
        uploads = []
    
    # Combine clips and uploads with prefixes to distinguish them
    available_videos = []
    for clip in clips:
        available_videos.append({'filename': clip, 'source': 'clips', 'display_name': f'[CLIP] {clip}'})
    for upload in uploads:
        available_videos.append({'filename': upload, 'source': 'uploads', 'display_name': f'[UPLOAD] {upload}'})
    
    return render_template('index.html', clips=clips, available_videos=available_videos)

@app.route('/get_video_duration', methods=['POST'])
def get_video_duration_route():
    """Get video duration for uploaded file."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    
    # Save temporary file to get duration
    original_extension = file.filename.rsplit('.', 1)[1].lower()
    temp_id = str(uuid.uuid4())
    temp_filename = f"temp_duration_{temp_id}.{original_extension}"
    temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
    file.save(temp_filepath)
    
    try:
        duration = get_video_duration(temp_filepath)
        return jsonify({'duration': duration})
    finally:
        # Clean up temporary file
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)

@app.route('/download_video', methods=['POST'])
def download_video():
    """Download video from URL and return duration."""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'success': False, 'message': 'No URL provided'}), 400
        
        if not is_valid_url(url):
            return jsonify({'success': False, 'message': 'Invalid URL format'}), 400
        
        # Generate a download ID for progress tracking
        download_id = str(uuid.uuid4())
        
        # Initialize progress
        download_progress[download_id] = {
            'stage': 'starting',
            'percent': 0,
            'message': 'Starting download...'
        }
        
        def download_in_background():
            result = download_video_from_url(url, app.config['UPLOAD_FOLDER'], download_id)
            # Store result in a way we can access it
            download_progress[download_id]['result'] = result
        
        # Start download in a separate thread
        thread = threading.Thread(target=download_in_background)
        thread.daemon = True
        thread.start()
        
        # Return immediately with download ID for progress tracking
        return jsonify({
            'success': True,
            'download_id': download_id,
            'message': 'Download started'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@app.route('/download_status/<download_id>')
def download_status(download_id):
    """Check download status and return result when complete."""
    if download_id not in download_progress:
        return jsonify({'success': False, 'message': 'Download not found'}), 404
    
    progress = download_progress[download_id]
    
    # If download is complete, return the result
    if 'result' in progress:
        result = progress['result']
        
        if result['status'] == 'error':
            # Clean up progress tracking
            del download_progress[download_id]
            return jsonify({'success': False, 'message': result['message']})
        
        # Get video duration
        duration = get_video_duration(result['filepath'])
        
        # Clean up progress tracking
        del download_progress[download_id]
        
        return jsonify({
            'success': True,
            'complete': True,
            'duration': duration,
            'filename': result['filename'],
            'filepath': result['filepath']
        })
    
    # Download still in progress
    return jsonify({
        'success': True,
        'complete': False,
        'stage': progress['stage'],
        'percent': progress['percent'],
        'message': progress['message']
    })

@app.route('/download_progress/<download_id>')
def download_progress_stream(download_id):
    """Stream download progress via Server-Sent Events."""
    def generate():
        while True:
            if download_id in download_progress:
                progress = download_progress[download_id]
                yield f"data: {json.dumps(progress)}\n\n"
                
                # Stop streaming when complete or error
                if progress['stage'] in ['complete', 'error'] or 'result' in progress:
                    break
            else:
                # No progress data yet
                yield f"data: {json.dumps({'stage': 'waiting', 'percent': 0, 'message': 'Waiting...'})}\n\n"
            
            time.sleep(1)
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/get_existing_video_duration', methods=['POST'])
def get_existing_video_duration():
    """Get duration of an existing video (clip or upload)."""
    try:
        data = request.get_json()
        source = data.get('source', '').strip()
        filename = data.get('filename', '').strip()
        
        if not source or not filename:
            return jsonify({'success': False, 'message': 'Source and filename required'}), 400
        
        if not allowed_file(filename):
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
        
        # Determine the correct folder based on source
        if source == 'clips':
            filepath = os.path.join(app.config['CLIPS_FOLDER'], filename)
        elif source == 'uploads':
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        else:
            return jsonify({'success': False, 'message': 'Invalid source'}), 400
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'message': 'Video not found'}), 404
        
        # Get video duration
        duration = get_video_duration(filepath)
        
        return jsonify({
            'success': True,
            'duration': duration
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Main upload handler that starts background processing."""
    clip_id = str(uuid.uuid4())
    
    # Extract form data and files
    form_data = dict(request.form)
    files = dict(request.files)
    
    # Start background processing
    thread = threading.Thread(target=process_clips_background, args=(clip_id, form_data, files))
    thread.daemon = True
    thread.start()
    
    # Return immediately with clip_id for progress tracking
    return jsonify({'clip_id': clip_id, 'message': 'Processing started'})

def process_clips_background(clip_id, form_data, files):
    """Background function to process clips with progress updates."""
    def update_clip_progress(stage, percent, message=""):
        print(f"Updating progress for clip {clip_id}: {stage} - {percent}% - {message}")
        clip_progress[clip_id] = {
            'stage': stage,
            'percent': percent,
            'message': message,
            'status': 'processing'
        }

    try:
        update_clip_progress("initializing", 5, "Starting clip processing...")

        video_source = form_data.get('video_source', 'file')
        folder = form_data.get('folder', '').strip()
        season = form_data.get('season', '').strip()
        unique_id = str(uuid.uuid4())

        # Handle different video sources
        if video_source == 'file':
            update_clip_progress("file_upload", 10, "Processing uploaded file...")
            file = files.get('file')
            if not file or file.filename == '' or not allowed_file(file.filename):
                clip_progress[clip_id] = {'status': 'error', 'message': 'Invalid file'}
                return

            original_extension = file.filename.rsplit('.', 1)[1].lower()
            original_filename = f"{unique_id}.{original_extension}"
            original_filepath = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
            file.save(original_filepath)

        elif video_source == 'url':
            update_clip_progress("url_download", 10, "Downloading video from URL...")
            video_url = form_data.get('video_url', '').strip()
            if not video_url or not is_valid_url(video_url):
                clip_progress[clip_id] = {'status': 'error', 'message': 'Invalid URL'}
                return
                
            downloaded_filename = form_data.get('downloaded_filename', '').strip()
            if downloaded_filename:
                original_filepath = os.path.join(app.config['UPLOAD_FOLDER'], downloaded_filename)
                if not os.path.exists(original_filepath):
                    result = download_video_from_url(video_url, app.config['UPLOAD_FOLDER'])
                    if result['status'] == 'error':
                        clip_progress[clip_id] = {'status': 'error', 'message': result['message']}
                        return
                    original_filepath = result['filepath']
            else:
                result = download_video_from_url(video_url, app.config['UPLOAD_FOLDER'])
                if result['status'] == 'error':
                    clip_progress[clip_id] = {'status': 'error', 'message': result['message']}
                    return
                original_filepath = result['filepath']
                
        elif video_source == 'existing':
            update_clip_progress("existing_video", 10, "Processing existing video...")
            existing_video = form_data.get('existing_clip', '').strip()
            if not existing_video:
                clip_progress[clip_id] = {'status': 'error', 'message': 'No existing video selected'}
                return
                
            try:
                source, filename = existing_video.split(':', 1)
            except ValueError:
                clip_progress[clip_id] = {'status': 'error', 'message': 'Invalid video selection format'}
                return
                
            if source == 'clips':
                existing_video_path = os.path.join(app.config['CLIPS_FOLDER'], filename)
            elif source == 'uploads':
                existing_video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            else:
                clip_progress[clip_id] = {'status': 'error', 'message': 'Invalid video source'}
                return
                
            if not os.path.exists(existing_video_path):
                clip_progress[clip_id] = {'status': 'error', 'message': 'Selected video not found'}
                return
                
            original_extension = os.path.splitext(filename)[1][1:].lower()
            original_filename = f"{unique_id}.{original_extension}"
            original_filepath = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
            shutil.copy2(existing_video_path, original_filepath)
        else:
            clip_progress[clip_id] = {'status': 'error', 'message': 'Invalid video source'}
            return

        update_clip_progress("parsing_clips", 20, "Parsing clip data...")
        
        # Parse clips data
        clips_data = {}
        for key, value in form_data.items():
            if key.startswith('clip_name_'):
                clip_index = key.split('_')[-1]
                if clip_index not in clips_data:
                    clips_data[clip_index] = {'name': value, 'segments': []}
            elif key.startswith('clip_') and ('_start_' in key or '_end_' in key):
                parts = key.split('_')
                clip_index, time_type, time_unit, segment_index = parts[1], parts[2], parts[3], parts[4]
                
                if clip_index not in clips_data:
                    clips_data[clip_index] = {'name': f"unnamed_clip_{clip_index}", 'segments': []}
                
                segment_idx = int(segment_index)
                while len(clips_data[clip_index]['segments']) <= segment_idx:
                    clips_data[clip_index]['segments'].append({})
                
                if time_type not in clips_data[clip_index]['segments'][segment_idx]:
                    clips_data[clip_index]['segments'][segment_idx][time_type] = {}
                
                clips_data[clip_index]['segments'][segment_idx][time_type][time_unit] = int(value)

        # Convert time components to HH:MM:SS.mmm format
        for clip_data in clips_data.values():
            for segment in clip_data['segments']:
                if 'start' in segment and 'end' in segment:
                    start = segment['start']
                    segment['start'] = f"{start.get('hours', 0):02d}:{start.get('minutes', 0):02d}:{start.get('seconds', 0):02d}.{start.get('milliseconds', 0):03d}"
                    
                    end = segment['end']
                    segment['end'] = f"{end.get('hours', 0):02d}:{end.get('minutes', 0):02d}:{end.get('seconds', 0):02d}.{end.get('milliseconds', 0):03d}"

        total_clips = len(clips_data)
        processed_clips = 0
        
        for index, data in clips_data.items():
            update_clip_progress("processing_clips", 30 + (processed_clips * 60 // total_clips), f"Processing clip '{data['name']}'...")
            
            segments = [s for s in data.get('segments', []) if s.get('start') and s.get('end')]
            if not segments:
                processed_clips += 1
                continue

            # Validate segments
            segments.sort(key=lambda s: s['start'])
            for i in range(1, len(segments)):
                if segments[i]['start'] < segments[i - 1]['end']:
                    clip_progress[clip_id] = {'status': 'error', 'message': f"Segments for clip '{data['name']}' are not in chronological order"}
                    return

            safe_base_name = secure_filename(data['name'])

            # Build the directory structure
            clip_dir = app.config['CLIPS_FOLDER']
            if folder:
                clip_dir = app.config['JELLYFIN_FOLDER']
                clip_dir = os.path.join(clip_dir, secure_filename(folder))
            if season:
                clip_dir = os.path.join(clip_dir, secure_filename(season))
            clip_dir = os.path.join(clip_dir, safe_base_name)

            os.makedirs(clip_dir, exist_ok=True)

            clip_filename = f"{safe_base_name}.mp4"
            clip_filepath = os.path.join(clip_dir, clip_filename)

            command = []
            temp_files = []
            concat_list_path = None

            if len(segments) == 1:
                seg = segments[0]
                command = [
                    'ffmpeg', '-i', original_filepath, '-ss', seg['start'],
                    '-to', seg['end'], '-c:v', 'libx264', '-c:a', 'aac',
                    '-preset', 'fast', '-crf', '23', '-y', clip_filepath
                ]
            else:
                temp_files = []
                for i, seg in enumerate(segments):
                    temp_filename = f"temp_segment_{i}_{unique_id}.mp4"
                    temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
                    temp_files.append(temp_filepath)
                    
                    segment_command = [
                        'ffmpeg', '-i', original_filepath, '-ss', seg['start'],
                        '-to', seg['end'], '-c:v', 'libx264', '-c:a', 'aac',
                        '-preset', 'fast', '-crf', '23', '-y', temp_filepath
                    ]
                    
                    subprocess.run(segment_command, check=True, capture_output=True, text=True)
                
                concat_list_path = os.path.join(app.config['UPLOAD_FOLDER'], f"concat_list_{unique_id}.txt")
                with open(concat_list_path, 'w') as f:
                    for temp_file in temp_files:
                        f.write(f"file '{os.path.abspath(temp_file)}'\n")
                
                command = [
                    'ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat_list_path,
                    '-c', 'copy', '-y', clip_filepath
                ]

            # Process the clip
            result = process_clip(original_filepath, clip_filepath, command)
            
            # Clean up temporary files
            if len(segments) > 1 and temp_files:
                for temp_file in temp_files:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                if concat_list_path and os.path.exists(concat_list_path):
                    os.remove(concat_list_path)

            processed_clips += 1

        # Clean up original file
        if os.path.exists(original_filepath):
            os.remove(original_filepath)

        update_clip_progress("completed", 100, "All clips processed successfully!")
        clip_progress[clip_id]['status'] = 'completed'
        
    except Exception as e:
        clip_progress[clip_id] = {
            'status': 'error',
            'message': f'Error processing clips: {str(e)}'
        }

@app.route('/clip_progress/<clip_id>')
def clip_progress_endpoint(clip_id):
    """Server-sent events endpoint for clip processing progress."""
    def generate():
        while True:
            if clip_id in clip_progress:
                progress_data = clip_progress[clip_id]
                yield f"data: {json.dumps(progress_data)}\n\n"
                
                # If completed or error, stop streaming
                if progress_data.get('status') in ['completed', 'error']:
                    break
            else:
                # If no progress data yet, send waiting status
                yield f"data: {json.dumps({'status': 'waiting', 'message': 'Waiting to start...'})}\n\n"
            
            time.sleep(1)
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/clip_status/<clip_id>')
def clip_status(clip_id):
    """Get current clip processing status."""
    if clip_id in clip_progress:
        return jsonify(clip_progress[clip_id])
    return jsonify({'status': 'not_found', 'message': 'Clip processing not found'})

@app.route('/clips/<filename>')
def download_clip(filename):
    """Provides a route to download the finished clips."""
    return send_from_directory(app.config['CLIPS_FOLDER'], filename, as_attachment=True)

@app.route('/clear_clips', methods=['POST'])
def clear_clips():
    """Clears all clips from the clips folder."""
    try:
        clip_files = [f for f in os.listdir(app.config['CLIPS_FOLDER']) if allowed_file(f)]
        deleted_count = 0
        
        for filename in clip_files:
            filepath = os.path.join(app.config['CLIPS_FOLDER'], filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                deleted_count += 1
        
        if deleted_count > 0:
            flash(f'Successfully deleted {deleted_count} clip(s).', 'success')
        else:
            flash('No clips found to delete.', 'error')
            
    except Exception as e:
        flash(f'Error clearing clips: {str(e)}', 'error')
    
    return jsonify({'success': True, 'deleted_count': deleted_count})

if __name__ == '__main__':
    create_folders()
    app.run(debug=True, port=5000)
