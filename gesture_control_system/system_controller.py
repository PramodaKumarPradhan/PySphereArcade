import time
import pyautogui
import numpy as np

# Configure PyAutoGUI to be fast and responsive
pyautogui.PAUSE = 0.001
pyautogui.FAILSAFE = True  # Move mouse to any corner to abort execution

class SystemController:
    def __init__(self):
        """
        Initializes the OS controller with default configurations and action rate-limiters.
        """
        self.enabled = False  # Global toggle for OS Control Mode
        
        # Get screen geometry
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Active zone bounds in the camera frame to make reaching corners easier
        # Coordinates outside this box will map directly to screen borders.
        self.active_x_min = 0.15
        self.active_x_max = 0.85
        self.active_y_min = 0.20
        self.active_y_max = 0.80
        
        # State tracking
        self.is_mouse_down = False
        self.last_volume_time = 0
        self.last_media_time = 0
        
        # Keep track of previous coordinates for motion-based gestures (scrolling)
        self.last_scroll_y = None

    def update_settings(self, enabled, sensitivity=None):
        """
        Updates controller settings from the web dashboard.
        """
        self.enabled = enabled
        if sensitivity is not None:
            # Adjust active zone based on sensitivity (higher sensitivity = smaller active zone)
            margin = 0.5 * (1.0 - np.clip(sensitivity, 0.1, 0.9))
            self.active_x_min = margin
            self.active_x_max = 1.0 - margin
            self.active_y_min = margin + 0.05
            self.active_y_max = 1.0 - margin - 0.05

    def execute_action(self, hand_data):
        """
        Executes an OS action based on the detected hand gesture and coordinates.
        """
        if not self.enabled or not hand_data:
            self._reset_mouse_state()
            return "Disabled/No Data"

        gesture = hand_data["gesture"]
        px, py = hand_data["pointer_smoothed"]
        curr_time = time.time()
        action_triggered = "None"
        
        try:
            # A. Cursor Control Mode (Pointing or Pinching/Dragging)
            if gesture in ["Pointing", "Pinch"]:
                # Map coordinates from the camera's active zone to screen bounds
                # Flip X coordinate since the camera is mirrored relative to user movements
                flipped_x = 1.0 - px
                
                screen_x = np.interp(flipped_x, [self.active_x_min, self.active_x_max], [0, self.screen_width])
                screen_y = np.interp(py, [self.active_y_min, self.active_y_max], [0, self.screen_height])
                
                # Clip to screen edges
                screen_x = int(np.clip(screen_x, 0, self.screen_width - 1))
                screen_y = int(np.clip(screen_y, 0, self.screen_height - 1))
                
                # Perform cursor movement
                pyautogui.moveTo(screen_x, screen_y)
                
                # Handle click & drag logic via pinch
                if gesture == "Pinch":
                    if not self.is_mouse_down:
                        pyautogui.mouseDown()
                        self.is_mouse_down = True
                        action_triggered = f"Mouse Down at ({screen_x}, {screen_y})"
                    else:
                        action_triggered = f"Dragging to ({screen_x}, {screen_y})"
                else:
                    if self.is_mouse_down:
                        pyautogui.mouseUp()
                        self.is_mouse_down = False
                        action_triggered = f"Mouse Up at ({screen_x}, {screen_y})"
                    else:
                        action_triggered = f"Moving Cursor to ({screen_x}, {screen_y})"
            else:
                # If we were dragging and changed gesture, release mouse
                self._reset_mouse_state()
                
            # B. Scrolling Mode (OK Gesture)
            if gesture == "OK":
                if self.last_scroll_y is not None:
                    dy = py - self.last_scroll_y
                    # If vertical movement exceeds threshold, trigger scroll
                    if abs(dy) > 0.005:
                        # Map dy to scroll speed. Negative dy = movement upwards = scroll UP (positive pyautogui scroll)
                        scroll_amount = int(-dy * 3000)
                        pyautogui.scroll(scroll_amount)
                        action_triggered = f"Scroll {scroll_amount}"
                self.last_scroll_y = py
            else:
                self.last_scroll_y = None
                
            # C. Volume Control (Thumbs Up / Thumbs Down)
            if gesture == "Thumbs Up" and (curr_time - self.last_volume_time > 0.25):
                pyautogui.press("volumeup")
                self.last_volume_time = curr_time
                action_triggered = "Volume Up"
                
            elif gesture == "Thumbs Down" and (curr_time - self.last_volume_time > 0.25):
                pyautogui.press("volumedown")
                self.last_volume_time = curr_time
                action_triggered = "Volume Down"
                
            # D. Media Play/Pause (Victory Gesture)
            if gesture == "Victory" and (curr_time - self.last_media_time > 1.2):
                pyautogui.press("playpause")
                self.last_media_time = curr_time
                action_triggered = "Toggle Play/Pause"
                
        except pyautogui.FailSafeException:
            # User triggered failsafe by slamming mouse into a screen corner
            self._reset_mouse_state()
            action_triggered = "Failsafe Triggered"
            
        return action_triggered

    def _reset_mouse_state(self):
        """
        Safely releases the mouse drag state if it's currently pressed.
        """
        if self.is_mouse_down:
            try:
                pyautogui.mouseUp()
            except pyautogui.FailSafeException:
                pass
            self.is_mouse_down = False
        self.last_scroll_y = None
