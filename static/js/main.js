let clipCounter = 0;
let segmentCounters = {};

function addClip() {
    clipCounter++;
    segmentCounters[clipCounter] = 0;
    const container = document.getElementById('clips-container');
    const newClipGroup = document.createElement('div');
    newClipGroup.className = 'clip-group';
    newClipGroup.id = 'clip-group-' + clipCounter;
    newClipGroup.innerHTML = `
        <div class="margin: 10px 0>
        <h3>Clip #${clipCounter + 1} <button type="button" onclick="removeClip(${clipCounter})" class="btn btn-outline btn-small">🗑️ Remove Clip</button></h3>
        </div>
        
        <div style="margin: 10px 0;">
        <label for="clip_name_${clipCounter}">Custom Clip Name:</label>
        <input type="text" id="clip_name_${clipCounter}" name="clip_name_${clipCounter}" placeholder="e.g., Highlight Reel" required>
        </div>
        <div id="segments-container-${clipCounter}"></div>
        <button type="button" onclick="addSegment(${clipCounter})" class="btn btn-primary" class="btn btn-outline btn-small">➕ Add Time Segment</button>
    `;
    container.appendChild(newClipGroup);
    addSegment(clipCounter);
}

function removeClip(clipIndex) { 
    document.getElementById('clip-group-' + clipIndex)?.remove();
}

function addSegment(clipIndex) {
    const segmentIndex = segmentCounters[clipIndex]++;
    const container = document.getElementById(`segments-container-${clipIndex}`);
    
    // Get the end time of the previous segment (if any)
    let prevEndHours = 0, prevEndMinutes = 0, prevEndSeconds = 0, prevEndMilliseconds = 0;
    if (segmentIndex > 0) {
        const prevSegmentId = `segment-${clipIndex}-${segmentIndex - 1}`;
        const prevSegment = document.getElementById(prevSegmentId);
        if (prevSegment) {
            const prevEndHoursInput = prevSegment.querySelector(`input[name="clip_${clipIndex}_end_hours_${segmentIndex - 1}"]`);
            const prevEndMinutesInput = prevSegment.querySelector(`input[name="clip_${clipIndex}_end_minutes_${segmentIndex - 1}"]`);
            const prevEndSecondsInput = prevSegment.querySelector(`input[name="clip_${clipIndex}_end_seconds_${segmentIndex - 1}"]`);
            const prevEndMillisecondsInput = prevSegment.querySelector(`input[name="clip_${clipIndex}_end_milliseconds_${segmentIndex - 1}"]`);
            
            if (prevEndHoursInput) prevEndHours = parseInt(prevEndHoursInput.value) || 0;
            if (prevEndMinutesInput) prevEndMinutes = parseInt(prevEndMinutesInput.value) || 0;
            if (prevEndSecondsInput) prevEndSeconds = parseInt(prevEndSecondsInput.value) || 0;
            if (prevEndMillisecondsInput) prevEndMilliseconds = parseInt(prevEndMillisecondsInput.value) || 0;
        }
    }
    
    const newSegment = document.createElement('div');
    newSegment.className = 'time-segment';
    newSegment.id = `segment-${clipIndex}-${segmentIndex}`;
    newSegment.innerHTML = `
        <h4>Time Segment #${segmentIndex + 1} <button type="button" onclick="removeSegment(${clipIndex}, ${segmentIndex})" class="btn btn-outline btn-small">🗑️ Remove Segment</button></h4>
        <div class="time-inputs">
            <div>
                <label>Start Hours</label>
                <input type="number" name="clip_${clipIndex}_start_hours_${segmentIndex}" min="0" max="23" value="${prevEndHours}" placeholder="0">
            </div>
            <div>
                <label>Start Minutes</label>
                <input type="number" name="clip_${clipIndex}_start_minutes_${segmentIndex}" min="0" max="59" value="${prevEndMinutes}" placeholder="0">
            </div>
            <div>
                <label>Start Seconds</label>
                <input type="number" name="clip_${clipIndex}_start_seconds_${segmentIndex}" min="0" max="59" value="${prevEndSeconds}" placeholder="0">
            </div>
            <div>
                <label>Start Milliseconds</label>
                <input type="number" name="clip_${clipIndex}_start_milliseconds_${segmentIndex}" min="0" max="999" value="${prevEndMilliseconds}" placeholder="0">
            </div>
        </div>
        <div class="time-inputs">
            <div>
                <label>End Hours</label>
                <input type="number" name="clip_${clipIndex}_end_hours_${segmentIndex}" min="0" max="23" value="${prevEndHours}" placeholder="0">
            </div>
            <div>
                <label>End Minutes</label>
                <input type="number" name="clip_${clipIndex}_end_minutes_${segmentIndex}" min="0" max="59" value="${prevEndMinutes + 1}" placeholder="1">
            </div>
            <div>
                <label>End Seconds</label>
                <input type="number" name="clip_${clipIndex}_end_seconds_${segmentIndex}" min="0" max="59" value="${prevEndSeconds}" placeholder="0">
            </div>
            <div>
                <label>End Milliseconds</label>
                <input type="number" name="clip_${clipIndex}_end_milliseconds_${segmentIndex}" min="0" max="999" value="${prevEndMilliseconds}" placeholder="0">
            </div>
        </div>
    `;
    container.appendChild(newSegment);
}

function removeSegment(clipIndex, segmentIndex) { 
    document.getElementById(`segment-${clipIndex}-${segmentIndex}`)?.remove(); 
}

function createFirstClip() {
    const clipsContainer = document.getElementById('clips-container');
    const videoNotLoaded = document.getElementById('video-not-loaded');
    const clipControls = document.getElementById('clip-controls');
    
    // Hide the "video not loaded" message and show clips container
    videoNotLoaded.style.display = 'none';
    clipsContainer.style.display = 'block';
    clipControls.style.display = 'block';
    
    // Reset counters
    clipCounter = 0;
    segmentCounters = {};
    segmentCounters[0] = 0;
    
    // Create the first clip
    const newClipGroup = document.createElement('div');
    newClipGroup.className = 'clip-group';
    newClipGroup.id = 'clip-group-0';
    newClipGroup.innerHTML = `
        <h3>Clip #1</h3>
        <div style="margin: 10px 0;">
        <label for="clip_name_0">Custom Clip Name:</label>
        <input type="text" id="clip_name_0" name="clip_name_0" value="Clipar_clip" required>
        </div>
        <div id="segments-container-0"></div>
        <button type="button" onclick="addSegment(0)" class="btn btn-primary" class="btn btn-outline btn-small">➕ Add Time Segment</button>
    `;
    clipsContainer.appendChild(newClipGroup);
    
    // Add the first segment
    addSegment(0);
}

function resetClipsUI() {
    const durationText = document.getElementById('duration-text');
    const clipsContainer = document.getElementById('clips-container');
    const videoNotLoaded = document.getElementById('video-not-loaded');
    const clipControls = document.getElementById('clip-controls');
    
    durationText.textContent = '--:--:--.---';
    clipsContainer.style.display = 'none';
    clipsContainer.innerHTML = '';
    clipControls.style.display = 'none';
    videoNotLoaded.style.display = 'block';
    
    clipCounter = 0;
    segmentCounters = {};
}

async function loadVideoFile(file) {
    resetClipsUI(); // Clear all existing clips and segments

    const durationText = document.getElementById('duration-text');
    durationText.innerHTML = 'Loading...';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/get_video_duration', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            durationText.textContent = result.duration;
            createFirstClip(); // Add the first clip and segment
        } else {
            durationText.textContent = 'Error loading duration';
        }
    } catch (error) {
        durationText.textContent = 'Error loading duration';
    }
}

async function loadVideoFromUrl() {
    resetClipsUI(); // Clear all existing clips and segments

    const urlInput = document.getElementById('video-url');
    const url = urlInput.value.trim();

    if (!url) {
        alert('Please enter a video URL');
        return;
    }

    const vidDownDiv = document.getElementById('video-download');
    const vidDownDivTxt = document.getElementById('download-text');
    vidDownDiv.style.display = 'block';
    vidDownDivTxt.innerHTML = `
        <div style="margin-bottom: 10px;">
            <div class="progress">
                <div class="progress-fill" id="download-progress-fill" style="width: 0%;"></div>
            </div>
            <div id="download-progress-text" style="margin-top: 5px; font-size: 0.875rem;">Starting download...</div>
        </div>
    `;

    try {
        const response = await fetch('/download_video', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });

        if (response.ok) {
            const result = await response.json();
            if (result.success) {
                startProgressTracking(result.download_id);
                pollDownloadStatus(result.download_id); // Add the first clip and segment after download
            } else {
                vidDownDivTxt.textContent = 'Error starting download';
                alert('Error: ' + result.message);
            }
        } else {
            vidDownDivTxt.textContent = 'Error starting download';
            alert('Failed to start download');
        }
    } catch (error) {
        vidDownDivTxt.textContent = 'Error starting download';
        alert('An error occurred: ' + error.message);
    }
}

function startProgressTracking(downloadId) {
    const progressBar = document.getElementById('download-progress-fill');
    const progressText = document.getElementById('download-progress-text');
    
    if (!progressBar || !progressText) return;
    
    const eventSource = new EventSource('/download_progress/' + downloadId);
    
    eventSource.onmessage = function(event) {
        try {
            const progress = JSON.parse(event.data);
            
            // Update progress bar
            progressBar.style.width = progress.percent + '%';
            progressText.textContent = progress.message || 'Processing...';
            
            // Close connection when complete
            if (progress.stage === 'complete' || progress.stage === 'error') {
                eventSource.close();
            }
        } catch (e) {
            console.error('Error parsing progress data:', e);
        }
    };
    
    eventSource.onerror = function(event) {
        console.error('EventSource failed:', event);
        eventSource.close();
    };
}

async function pollDownloadStatus(downloadId) {
    const durationText = document.getElementById('duration-text');
    
    while (true) {
        try {
            const response = await fetch('/download_status/' + downloadId);
            const result = await response.json();
            
            if (result.success && result.complete) {
                // Download completed successfully
                durationText.textContent = result.duration;
                document.getElementById('video-url').setAttribute('data-downloaded-file', result.filename);
                createFirstClip();
                break;
            } else if (!result.success) {
                // Download failed
                durationText.textContent = 'Error downloading video';
                alert('Error: ' + result.message);
                break;
            }
            
            // Wait before polling again
            await new Promise(resolve => setTimeout(resolve, 1000));
            
        } catch (error) {
            durationText.textContent = 'Error checking download status';
            alert('An error occurred: ' + error.message);
            break;
        }
    }
}

async function loadExistingClip() {
    
    resetClipsUI(); // Clear all existing clips and segments
    const clipSelect = document.getElementById('existing-clip');
    const selectedValue = clipSelect.value;
    
    if (!selectedValue) {
        alert('Please select a video');
        return;
    }
    
    // Parse the source and filename from the value (format: "source:filename")
    const [source, filename] = selectedValue.split(':');
    
    const durationText = document.getElementById('duration-text');
    
    durationText.innerHTML = 'Loading...';
    
    try {
        const response = await fetch('/get_existing_video_duration', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ source: source, filename: filename })
        });
        
        if (response.ok) {
            const result = await response.json();
            if (result.success) {
                durationText.textContent = result.duration;
                createFirstClip();
            } else {
                durationText.textContent = 'Error loading duration';
                alert('Error: ' + result.message);
            }
        } else {
            durationText.textContent = 'Error loading duration';
            alert('Error loading video duration');
        }
    } catch (error) {
        durationText.textContent = 'Error loading duration';
        alert('Error: ' + error.message);
    }
}

async function clearAllClips() {
    if (!confirm('Are you sure you want to delete all clips? This cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch('/clear_clips', {
            method: 'POST'
        });
        
        if (response.ok) {
            location.reload(); // Refresh the page to show the updated clip list
        } else {
            alert('Error clearing clips');
        }
    } catch (error) {
        alert('Error clearing clips: ' + error.message);
    }
}

// Initialize on page load
window.onload = () => {
    clipCounter = 0;
    segmentCounters = {};
    
    // Handle video source selection
    document.querySelectorAll('input[name="video_source"]').forEach(radio => {
        radio.addEventListener('change', function() {
            const fileSection = document.getElementById('file-input-section');
            const urlSection = document.getElementById('url-input-section');
            const existingSection = document.getElementById('existing-clip-section');
            const durationText = document.getElementById('duration-text');
            
            // Hide all sections first
            fileSection.style.display = 'none';
            urlSection.style.display = 'none';
            existingSection.style.display = 'none';
            
            // Clear required attributes
            document.getElementById('video-file').required = false;
            document.getElementById('video-url').required = false;
            document.getElementById('existing-clip').required = false;
            
            if (this.value === 'file') {
                fileSection.style.display = 'block';
                document.getElementById('video-file').required = true;
            } else if (this.value === 'url') {
                urlSection.style.display = 'block';
                document.getElementById('video-url').required = true;
            } else if (this.value === 'existing') {
                existingSection.style.display = 'block';
                document.getElementById('existing-clip').required = true;
            }
            
            // Hide duration and reset clips when switching sources
            
            durationText.textContent = '--:--:--.---';
            resetClipsUI();
        });
    });
    
    // Handle file selection to show video duration
    document.getElementById('video-file').addEventListener('change', async function(event) {
        const file = event.target.files[0];
        if (file) {
            await loadVideoFile(file);
        }
    });
    
    // Handle form submission to show progress
    document.querySelector('form').addEventListener('submit', function(event) {
        const submitButton = event.target.querySelector('input[type="submit"]');
        submitButton.value = '⚙️ Processing Clips...';
        submitButton.disabled = true;
        
        // Create progress overlay
        const progressOverlay = document.createElement('div');
        progressOverlay.id = 'progress-overlay';
        progressOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        `;
        progressOverlay.innerHTML = `
            <div style="background: white; padding: 30px; border-radius: 10px; text-align: center; max-width: 500px; width: 90%;">
                <h3 style="margin: 0 0 1rem 0; color: var(--foreground);">🎬 Clip Processing Progress</h3>
                <div class="progress" style="margin: 1rem 0;">
                    <div class="progress-bar" id="processing-progress" style="width: 0%;">0%</div>
                </div>
                <div id="processing-status">Processing clips...</div>
                <p style="margin-top: 1rem; color: #666; font-size: 14px;">This may take a few minutes depending on the video size and number of clips.</p>
            </div>
        `;
        document.body.appendChild(progressOverlay);
        
        // Start progress monitoring
        setTimeout(() => {
            const eventSource = new EventSource('/processing_progress');
            
            eventSource.onmessage = function(event) {
                const data = JSON.parse(event.data);
                const progressBar = document.getElementById('processing-progress');
                const statusDiv = document.getElementById('processing-status');
                
                if (progressBar && statusDiv) {
                    const percentage = Math.round(data.percentage || 0);
                    progressBar.style.width = percentage + '%';
                    progressBar.textContent = percentage + '%';
                    statusDiv.textContent = data.message || 'Processing...';
                    
                    if (data.status === 'completed' || data.status === 'error') {
                        eventSource.close();
                        setTimeout(() => {
                            window.location.reload();
                        }, 2000);
                    }
                }
            };
            
            eventSource.onerror = function() {
                eventSource.close();
            };
        }, 500);
    });
};