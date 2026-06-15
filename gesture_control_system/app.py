import os
import cv2
import time
import json
import threading
from flask import Flask, render_template, Response, request, jsonify
from flask_cors import CORS

from gesture_detector import GestureDetector
from system_controller import SystemController

app = Flask(__name__)
CORS(app)

# Global instances
detector = GestureDetector()
controller = SystemController()

frame_lock = threading.Lock()
latest_frame = None
latest_data = {
    "gesture": "None",
    "label": "None",
    "confidence": 0.0,
    "pointer_raw": [0.5, 0.5],
    "pointer_smoothed": [0.5, 0.5],
    "action": "None",
    "system_control_enabled": False,
    "timestamp": 0,
    "simulated": False
}

camera_running = True
camera_connected = False

def camera_processing_thread():
    """
    Background thread that captures video frames, performs hand gesture recognition,
    triggers OS actions, and updates the states shared with Flask.
    """
    global latest_frame, latest_data, camera_connected, camera_running
    
    # Attempt to open default webcam (camera index 0)
    cap = cv2.VideoCapture(0)
    
    if cap.isOpened():
        camera_connected = True
        print("[SYSTEM] Camera successfully opened.")
        # Set camera resolution (standard 640x480 for speed)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    else:
        print("[SYSTEM] Camera not detected or busy. Running in simulated demo mode.")
        camera_connected = False
        cap.release()
        
    dummy_width, dummy_height = 640, 480
    sim_t = 0.0
    
    while camera_running:
        if camera_connected:
            ret, frame = cap.read()
            if not ret:
                print("[SYSTEM] Webcam frame read error. Retrying...")
                time.sleep(0.1)
                continue
                
            # Flip frame horizontally to create a natural "selfie" view (mirroring)
            frame = cv2.flip(frame, 1)
            
            # Detect hand and recognize gestures
            annotated_frame, hand_data = detector.process_frame(frame)
            
            # Perform system interactions based on recognized gestures
            action = "None"
            if hand_data:
                action = controller.execute_action(hand_data)
            else:
                controller._reset_mouse_state()
                
            # Compress the output frame into JPEG format
            ret, jpeg = cv2.imencode('.jpg', annotated_frame)
            if ret:
                with frame_lock:
                    latest_frame = jpeg.tobytes()
                    
            # Package state data
            with frame_lock:
                if hand_data:
                    latest_data = {
                        "gesture": hand_data["gesture"],
                        "label": hand_data["label"],
                        "confidence": hand_data["confidence"],
                        "pointer_raw": hand_data["pointer_raw"],
                        "pointer_smoothed": hand_data["pointer_smoothed"],
                        "action": action,
                        "system_control_enabled": controller.enabled,
                        "timestamp": time.time(),
                        "simulated": False
                    }
                else:
                    latest_data = {
                        "gesture": "None",
                        "label": "None",
                        "confidence": 0.0,
                        "pointer_raw": [0.5, 0.5],
                        "pointer_smoothed": [0.5, 0.5],
                        "action": "None",
                        "system_control_enabled": controller.enabled,
                        "timestamp": time.time(),
                        "simulated": False
                    }
        else:
            # Emulated fall-back loop if webcam is absent/busy.
            # Draws an interactive demo canvas.
            sim_frame = np.zeros((dummy_height, dummy_width, 3), dtype=np.uint8)
            
            # Draw a subtle tech grid in the background
            for x in range(0, dummy_width, 40):
                cv2.line(sim_frame, (x, 0), (x, dummy_height), (18, 18, 28), 1)
            for y in range(0, dummy_height, 40):
                cv2.line(sim_frame, (0, y), (dummy_width, y), (18, 18, 28), 1)
                
            # Add text markers
            cv2.putText(sim_frame, "DEMO MODE: CAMERA DISCONNECTED", (90, 45), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 160, 255), 2, cv2.LINE_AA)
            cv2.putText(sim_frame, "Simulating path & gesture cycles...", (180, 75), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (130, 130, 140), 1, cv2.LINE_AA)
            
            # Simulate a sweeping circular hand movement coordinate
            sim_t += 0.05
            px = 0.5 + 0.24 * np.cos(sim_t)
            py = 0.5 + 0.18 * np.sin(sim_t * 0.8)
            
            # Rotate gestures every 5 seconds to demo features
            gestures = ["Open Palm", "Fist", "Pointing", "Pinch", "Victory", "Thumbs Up", "OK"]
            gesture_index = int((sim_t // 5) % len(gestures))
            sim_gesture = gestures[gesture_index]
            
            # Render a simulated tracking point on the canvas
            cx, cy = int(px * dummy_width), int(py * dummy_height)
            color = (52, 211, 153) if sim_gesture != "Fist" else (248, 113, 113)
            
            # Draw radar circles
            cv2.circle(sim_frame, (cx, cy), 18, color, 2)
            cv2.circle(sim_frame, (cx, cy), 6, color, -1)
            cv2.putText(sim_frame, f"Emu: {sim_gesture}", (cx + 25, cy + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
            
            # Encode simulated frame
            ret, jpeg = cv2.imencode('.jpg', sim_frame)
            if ret:
                with frame_lock:
                    latest_frame = jpeg.tobytes()
                    
            with frame_lock:
                latest_data = {
                    "gesture": sim_gesture,
                    "label": "Right",
                    "confidence": 0.99,
                    "pointer_raw": [px, py],
                    "pointer_smoothed": [px, py],
                    "action": "Simulated Drag" if sim_gesture == "Pinch" else "Demo Coordinates Sent",
                    "system_control_enabled": False,  # Keep safety off in simulation
                    "timestamp": time.time(),
                    "simulated": True
                }
                
        # Frequency cap at ~33Hz (30ms per frame) to prevent thrashing
        time.sleep(0.03)
        
    if cap.isOpened():
        cap.release()
    print("[SYSTEM] Camera thread terminated.")

# Start Background Thread
processing_thread = threading.Thread(target=camera_processing_thread, daemon=True)
processing_thread.start()

# Flask Endpoints
@app.route('/')
def index():
    """
    Renders the primary web dashboard.
    """
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """
    MJPEG stream endpoint for the webcam display.
    """
    def generate():
        while camera_running:
            with frame_lock:
                if latest_frame is None:
                    time.sleep(0.01)
                    continue
                frame_bytes = latest_frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.03)
            
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/data_stream')
def data_stream():
    """
    Server-Sent Events (SSE) endpoint to broadcast JSON gesture packets.
    """
    def event_stream():
        while camera_running:
            with frame_lock:
                data_payload = json.dumps(latest_data)
            yield f"data: {data_payload}\n\n"
            time.sleep(0.04)  # ~25Hz data updates
            
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/api/settings', methods=['POST'])
def api_settings():
    """
    Updates the system controller options.
    """
    data = request.json or {}
    enabled = data.get('enabled', False)
    sensitivity = data.get('sensitivity', 0.5)
    
    controller.update_settings(enabled, sensitivity)
    
    return jsonify({
        "status": "success",
        "system_control_enabled": controller.enabled,
        "sensitivity": sensitivity
    })

@app.route('/api/status', methods=['GET'])
def api_status():
    """
    Returns system status.
    """
    return jsonify({
        "camera_connected": camera_connected,
        "system_control_enabled": controller.enabled
    })

@app.route('/api/shutdown', methods=['POST'])
def api_shutdown():
    """
    Stops background thread safely.
    """
    global camera_running
    camera_running = False
    return jsonify({"status": "shutting_down"})

if __name__ == '__main__':
    # Flask application launcher
    print("[SYSTEM] Starting Flask Web Server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
