import os
import urllib.request
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import HandLandmarksConnections
from mediapipe.tasks.python.vision import drawing_utils as mp_drawing
from mediapipe.tasks.python.vision import drawing_styles as mp_drawing_styles

class GestureDetector:
    def __init__(self, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7):
        """
        Initializes the MediaPipe Tasks HandLandmarker and internal states.
        """
        # Resolve absolute path for the model file in the same directory as this script
        self.model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hand_landmarker.task")
        model_url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        
        # Download the model from Google if it doesn't exist locally
        if not os.path.exists(self.model_path):
            print(f"[SYSTEM] Neural model not found. Downloading Hand Landmarker task model from:\n{model_url}")
            try:
                # Setup custom user agent to avoid blockage
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
                urllib.request.install_opener(opener)
                
                urllib.request.urlretrieve(model_url, self.model_path)
                print(f"[SYSTEM] Model downloaded successfully and saved to: {self.model_path}")
            except Exception as e:
                print(f"[ERROR] Failed to download MediaPipe Hand model: {e}")
                # We raise to let the server report the error
                raise e
                
        # Initialize detector options
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=min_tracking_confidence,
            running_mode=vision.RunningMode.IMAGE
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        
        # Exponential Moving Average smoothing for pointer coordinates
        self.prev_x, self.prev_y = None, None
        self.smoothing = 0.70  # Lower value = more responsive, Higher value = smoother (less jitter)

    def process_frame(self, frame):
        """
        Processes a single BGR camera frame. Returns the annotated frame and hand gesture data dict.
        """
        # Convert BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert RGB image to MediaPipe Image object
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Run synchronous inference
        result = self.detector.detect(mp_image)
        
        hand_data = None
        
        if result.hand_landmarks:
            for hand_landmarks, handedness in zip(result.hand_landmarks, result.handedness):
                # Retrieve labels safely
                category = handedness[0]
                label = category.category_name if hasattr(category, "category_name") else getattr(category, "display_name", "Right")
                score = category.score
                
                # Extract normalized coordinates (x, y, z) for all 21 landmarks
                landmarks = [[lm.x, lm.y, lm.z] for lm in hand_landmarks]
                
                # Classify the hand gesture
                gesture = self._classify_gesture(landmarks, label)
                
                # Pointer coordinates track the index finger tip (landmark 8)
                pointer_raw = (landmarks[8][0], landmarks[8][1])
                pointer_smoothed = self._smooth_pointer(pointer_raw)
                
                # Draw hand landmarks
                try:
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        HandLandmarksConnections.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )
                except Exception as e:
                    # Fallback manually draw joint dots in case of representation differences
                    h, w, _ = frame.shape
                    for lm in landmarks:
                        cx, cy = int(lm[0] * w), int(lm[1] * h)
                        cv2.circle(frame, (cx, cy), 4, (16, 185, 129), -1)
                
                # Draw gesture name on the frame
                h, w, _ = frame.shape
                cv2.putText(
                    frame, 
                    f"{label} Hand: {gesture}", 
                    (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.8, 
                    (0, 255, 100), 
                    2, 
                    cv2.LINE_AA
                )
                
                hand_data = {
                    "label": label,
                    "confidence": float(score),
                    "landmarks": landmarks,
                    "gesture": gesture,
                    "pointer_raw": pointer_raw,
                    "pointer_smoothed": pointer_smoothed
                }
                
                # We prioritize the first detected hand for touchless OS controls
                break
                
        else:
            # Reset pointer coordinates smoothing filter when no hand is detected
            self.prev_x, self.prev_y = None, None
            
        return frame, hand_data

    def _classify_gesture(self, lm, label):
        """
        Classifies the active hand gesture using geometric heuristics.
        lm is a list of 21 points: [x, y, z] normalized.
        """
        # Coordinates: Y increases downwards. So Y_tip < Y_knuckle means pointing UP.
        
        # 1. Check open/closed status for individual fingers
        # Index: Tip (8) vs PIP (6)
        index_open = lm[8][1] < lm[6][1]
        
        # Middle: Tip (12) vs PIP (10)
        middle_open = lm[12][1] < lm[10][1]
        
        # Ring: Tip (16) vs PIP (14)
        ring_open = lm[16][1] < lm[14][1]
        
        # Pinky: Tip (20) vs PIP (18)
        pinky_open = lm[20][1] < lm[18][1]
        
        # Thumb: We verify horizontal extension by comparing X coordinate of tip (4) with IP joint (3).
        # MediaPipe handedness label might be swapped due to selfie camera mirroring.
        if label == "Right":
            thumb_open = lm[4][0] > lm[3][0]
        else:
            thumb_open = lm[4][0] < lm[3][0]
            
        # Euclidean distance between Thumb Tip (4) and Index Tip (8)
        pinch_dist = np.linalg.norm(np.array(lm[4]) - np.array(lm[8]))
        
        # 2. Heuristics classification rules:
        
        # A. Pinch (Thumb + Index Tip touching)
        # Note: Checked first so it overrides other classifications
        if pinch_dist < 0.045:
            return "Pinch"
            
        # B. OK Gesture (Pinch + Middle, Ring, Pinky extended open)
        if pinch_dist < 0.065 and middle_open and ring_open and pinky_open:
            return "OK"
            
        # C. Thumbs Up (Thumb open upwards, others tightly curled)
        # Y coordinate of thumb tip (4) is higher (smaller value) than thumb base/joints and wrist.
        if lm[4][1] < lm[2][1] - 0.02 and not index_open and not middle_open and not ring_open and not pinky_open:
            return "Thumbs Up"
            
        # D. Thumbs Down (Thumb open downwards, others curled)
        # Y coordinate of thumb tip (4) is lower (larger value) than thumb base/joints.
        if lm[4][1] > lm[2][1] + 0.02 and not index_open and not middle_open and not ring_open and not pinky_open:
            return "Thumbs Down"
            
        # E. Fist (All fingers curled)
        if not index_open and not middle_open and not ring_open and not pinky_open:
            return "Fist"
            
        # F. Open Palm (All fingers extended)
        if index_open and middle_open and ring_open and pinky_open:
            return "Open Palm"
            
        # G. Pointing (Only index finger extended)
        if index_open and not middle_open and not ring_open and not pinky_open:
            return "Pointing"
            
        # H. Victory / Peace Sign (Index and Middle extended, Ring and Pinky curled)
        if index_open and middle_open and not ring_open and not pinky_open:
            return "Victory"
            
        return "Unknown"

    def _smooth_pointer(self, raw_coords):
        """
        Smooths coordinates using an Exponential Moving Average.
        """
        rx, ry = raw_coords
        if self.prev_x is None or self.prev_y is None:
            self.prev_x, self.prev_y = rx, ry
            return rx, ry
            
        smoothed_x = self.prev_x + (rx - self.prev_x) * (1.0 - self.smoothing)
        smoothed_y = self.prev_y + (ry - self.prev_y) * (1.0 - self.smoothing)
        
        self.prev_x, self.prev_y = smoothed_x, smoothed_y
        return smoothed_x, smoothed_y
