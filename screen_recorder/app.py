import streamlit as st
import streamlit.components.v1 as components
import os

# Page configurations
st.set_page_config(
    page_title="Nexus Screen Recorder",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom layout CSS styling
st.markdown("""
<style>
    .main {
        background-color: #0a0c10;
        color: #ffffff;
    }
    h1, h2, h3 {
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    .card {
        background-color: #121625;
        border: 1px solid #232d4b;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        margin-bottom: 20px;
    }
    .stAlert {
        background-color: #1a1510;
        border-color: #ffaa00;
        color: #ffaa00;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar layout
st.sidebar.title("🎥 Nexus Recorder")
st.sidebar.markdown("---")
st.sidebar.info("""
**Dual Operation Modes**:
1. **Web Browser Recorder (Current)**:
   - Records your screen client-side using standard HTML5 browser APIs.
   - Deploys and runs perfectly on Streamlit Community Cloud.
2. **Local Desktop Recorder (Offline)**:
   - Runs locally on your machine via OpenCV and PyAutoGUI.
   - Captures high frame-rate native screen recordings.
""")
st.sidebar.markdown("---")
st.sidebar.caption("Powered by Python, Streamlit, HTML5 and MediaStream APIs.")

# Main app title
st.title("Nexus Screen Recorder")
st.caption("A premium screen capture tool for both local desktop offline recording and global browser access.")

# Main screen grid
col_main, col_sidebar = st.columns([2, 1])

with col_main:
    st.subheader("🎥 Browser Screen Recorder")
    st.write("Click the **Start Recording** button inside the panel below, select which tab, window, or monitor to record, and save it directly to your device.")
    
    # Custom HTML5/JS Web Screen Recorder Widget
    recorder_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background-color: #121625;
                color: #ffffff;
                padding: 15px;
                display: flex;
                flex-direction: column;
                gap: 15px;
                overflow: hidden;
            }
            .recorder-box {
                background: rgba(18, 22, 37, 0.85);
                border: 1px solid rgba(0, 102, 255, 0.2);
                border-radius: 12px;
                padding: 20px;
                display: flex;
                flex-direction: column;
                gap: 15px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
            }
            .header-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                padding-bottom: 12px;
            }
            .status-indicator {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                padding: 4px 10px;
                border-radius: 12px;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: #a0a5c0;
            }
            .status-indicator.ready {
                color: #00ff88;
                border-color: rgba(0, 255, 136, 0.2);
                background: rgba(0, 255, 136, 0.05);
            }
            .status-indicator.recording {
                color: #ff3366;
                border-color: rgba(255, 51, 102, 0.2);
                background: rgba(255, 51, 102, 0.05);
            }
            .status-indicator.recorded {
                color: #ffaa00;
                border-color: rgba(255, 170, 0, 0.2);
                background: rgba(255, 170, 0, 0.05);
            }
            .indicator-dot {
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background: #a0a5c0;
            }
            .status-indicator.ready .indicator-dot {
                background: #00ff88;
                box-shadow: 0 0 6px #00ff88;
            }
            .status-indicator.recording .indicator-dot {
                background: #ff3366;
                box-shadow: 0 0 8px #ff3366;
                animation: blink 1.2s infinite;
            }
            .status-indicator.recorded .indicator-dot {
                background: #ffaa00;
                box-shadow: 0 0 6px #ffaa00;
            }
            @keyframes blink {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.2; }
            }
            .toggle-group {
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 12px;
                color: #a0a5c0;
                cursor: pointer;
            }
            .toggle-group input {
                cursor: pointer;
            }
            .preview-container {
                position: relative;
                width: 100%;
                height: 280px;
                background-color: #080a10;
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
            }
            video {
                width: 100%;
                height: 100%;
                object-fit: contain;
                z-index: 2;
            }
            .overlay-message {
                position: absolute;
                font-size: 13px;
                color: #707280;
                z-index: 5;
                pointer-events: none;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                text-align: center;
                padding: 10px;
            }
            .controls-row {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }
            .btn {
                font-family: inherit;
                font-size: 12px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                padding: 10px 18px;
                border-radius: 6px;
                border: none;
                cursor: pointer;
                transition: all 0.2s ease;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                color: #ffffff;
            }
            .btn:disabled {
                background: #2a2e45 !important;
                color: #707280 !important;
                border-color: transparent !important;
                cursor: not-allowed;
            }
            .btn-start {
                background: #0066ff;
            }
            .btn-start:hover:not(:disabled) {
                background: #3385ff;
                box-shadow: 0 0 10px rgba(0, 102, 255, 0.3);
            }
            .btn-stop {
                background: #ff3366;
            }
            .btn-stop:hover:not(:disabled) {
                background: #ff668c;
                box-shadow: 0 0 10px rgba(255, 51, 102, 0.3);
            }
            .btn-download {
                background: #00ff88;
                color: #0a0c10;
                text-decoration: none;
            }
            .btn-download:hover:not(:disabled) {
                background: #33ff9e;
                box-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
            }
        </style>
    </head>
    <body>

    <div class="recorder-box">
        <div class="header-row">
            <div class="status-indicator ready" id="statusIndicator">
                <div class="indicator-dot"></div>
                <span id="statusText">Ready</span>
            </div>
            
            <label class="toggle-group">
                <input type="checkbox" id="micToggle" checked>
                <span>Record Microphone Audio</span>
            </label>
        </div>

        <div class="preview-container">
            <video id="previewVideo" autoplay muted playsinline></video>
            <div class="overlay-message" id="overlayMsg">Click START RECORDING to choose a display screen</div>
        </div>

        <div class="controls-row">
            <button class="btn btn-start" id="startBtn">▶ Start Recording</button>
            <button class="btn btn-stop" id="stopBtn" disabled>■ Stop</button>
            <a class="btn btn-download" id="downloadBtn" style="display: none;">📥 Download Video</a>
        </div>
    </div>

    <script>
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const downloadBtn = document.getElementById('downloadBtn');
        const previewVideo = document.getElementById('previewVideo');
        const statusIndicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');
        const micToggle = document.getElementById('micToggle');
        const overlayMsg = document.getElementById('overlayMsg');

        let mediaRecorder = null;
        let recordedChunks = [];
        let screenStream = null;
        let audioStream = null;
        let combinedStream = null;

        function setStatus(state) {
            statusIndicator.className = 'status-indicator ' + state;
            if (state === 'recording') {
                statusText.innerText = 'Recording';
                startBtn.disabled = true;
                stopBtn.disabled = false;
                micToggle.disabled = true;
                downloadBtn.style.display = 'none';
                previewVideo.controls = false;
                overlayMsg.style.display = 'none';
            } else if (state === 'recorded') {
                statusText.innerText = 'Recording Saved';
                startBtn.disabled = false;
                stopBtn.disabled = true;
                micToggle.disabled = false;
            } else {
                statusText.innerText = 'Ready';
                startBtn.disabled = false;
                stopBtn.disabled = true;
                micToggle.disabled = false;
                downloadBtn.style.display = 'none';
                previewVideo.controls = false;
                overlayMsg.style.display = 'block';
                overlayMsg.innerText = 'Click START RECORDING to choose a display screen';
            }
        }

        function cleanupStreams() {
            if (screenStream) {
                screenStream.getTracks().forEach(track => track.stop());
            }
            if (audioStream) {
                audioStream.getTracks().forEach(track => track.stop());
            }
        }

        startBtn.onclick = async () => {
            recordedChunks = [];
            
            try {
                // 1. Capture Screen Stream
                screenStream = await navigator.mediaDevices.getDisplayMedia({
                    video: { cursor: "always" },
                    audio: true // Captures tab audio if selected
                });
                
                let tracks = [...screenStream.getVideoTracks()];
                
                // If system audio is captured from screen sharing, include it
                const screenAudioTracks = screenStream.getAudioTracks();
                if (screenAudioTracks.length > 0) {
                    tracks.push(screenAudioTracks[0]);
                }
                
                // 2. Capture Microphone Audio (if toggled)
                if (micToggle.checked) {
                    try {
                        audioStream = await navigator.mediaDevices.getUserMedia({
                            audio: {
                                echoCancellation: true,
                                noiseSuppression: true
                            }
                        });
                        tracks.push(audioStream.getAudioTracks()[0]);
                    } catch (err) {
                        console.warn("Microphone access denied or unavailable: ", err);
                    }
                }
                
                // 3. Combine Streams
                combinedStream = new MediaStream(tracks);
                
                // Set stream preview
                previewVideo.srcObject = combinedStream;
                previewVideo.muted = true; // prevent audio feedback loop during live preview
                previewVideo.controls = false;
                previewVideo.play();
                
                // 4. Select mimetype
                let options = { mimeType: 'video/webm; codecs=vp9' };
                if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                    options = { mimeType: 'video/webm; codecs=vp8' };
                    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                        options = { mimeType: 'video/webm' };
                    }
                }
                
                mediaRecorder = new MediaRecorder(combinedStream, options);
                
                mediaRecorder.ondataavailable = (e) => {
                    if (e.data && e.data.size > 0) {
                        recordedChunks.push(e.data);
                    }
                };
                
                mediaRecorder.onstop = () => {
                    // Create video blob and URL
                    const blob = new Blob(recordedChunks, { type: 'video/webm' });
                    const videoUrl = URL.createObjectURL(blob);
                    
                    // Put video in playback preview
                    previewVideo.srcObject = null;
                    previewVideo.src = videoUrl;
                    previewVideo.muted = false; // allow voice playback
                    previewVideo.controls = true;
                    
                    // Setup download button link
                    downloadBtn.href = videoUrl;
                    downloadBtn.download = `screencast_${Date.now()}.webm`;
                    downloadBtn.style.display = 'inline-flex';
                    
                    setStatus('recorded');
                    cleanupStreams();
                };
                
                // Hook trigger if browser's native sharing bar "Stop sharing" is clicked
                screenStream.getVideoTracks()[0].onended = () => {
                    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                        mediaRecorder.stop();
                    }
                };
                
                mediaRecorder.start(1000); // chunk size 1 second
                setStatus('recording');
                
            } catch (err) {
                console.error("Failed to start screen capture: ", err);
                overlayMsg.style.display = 'block';
                overlayMsg.innerText = "Error: " + err.message;
                setStatus('ready');
                cleanupStreams();
            }
        };

        stopBtn.onclick = () => {
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
            }
        };
    </script>
    </body>
    </html>
    """
    
    # Render iframe component in Streamlit
    components.html(recorder_html, height=450)

with col_sidebar:
    st.subheader("💻 Local Desktop Mode")
    st.write("""
    For high-performance offline recording directly on your local system, run our optimized desktop script.
    
    This records your screens locally and compiles frames using OpenCV.
    """)
    
    st.code("""
# 1. Open your terminal in the directory
cd screen_recorder

# 2. Run the desktop recorder script
python desktop_recorder.py
    """, language="powershell")
    
    st.markdown("""
**Key Commands (Desktop Script):**
- A preview window will appear when recording starts.
- Click the preview window and press **`q`** to stop recording cleanly and save the video file.
- Alternatively, press **`Ctrl+C`** in the terminal to cancel.
    """)
    
    st.markdown("---")
    st.subheader("🌐 GitHub Cloud Deployment")
    st.markdown("""
To deploy this screen recorder globally:
1. Pushed to your GitHub.
2. Connect to **[Streamlit Community Cloud](https://share.streamlit.io)**.
3. Deploy app choosing file **`screen_recorder/app.py`**.
4. The web-capture code runs client-side, making it fully operational in any browser!
    """)
