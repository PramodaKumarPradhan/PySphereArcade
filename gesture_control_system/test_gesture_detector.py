import unittest
import numpy as np
from gesture_detector import GestureDetector

class TestGestureDetector(unittest.TestCase):
    def setUp(self):
        self.detector = GestureDetector()
        
    def create_mock_landmarks(self, index_open=True, middle_open=True, ring_open=True, pinky_open=True, thumb_open=True, pinch=False):
        """
        Creates a list of mock 21 landmarks representing various finger states.
        MediaPipe landmark mapping:
        0: Wrist
        4: Thumb Tip, 3: Thumb IP, 2: Thumb MCP, 1: Thumb CMC
        8: Index Tip, 7: Index DIP, 6: Index PIP, 5: Index MCP
        12: Middle Tip, 11: Middle DIP, 10: Middle PIP, 9: Middle MCP
        16: Ring Tip, 15: Ring DIP, 14: Ring PIP, 13: Ring MCP
        20: Pinky Tip, 19: Pinky DIP, 18: Pinky PIP, 17: Pinky MCP
        """
        lm = [[0.5, 0.9, 0.0] for _ in range(21)] # Default to wrist location
        
        # 1. Helper to set a finger coordinates
        def set_finger(start_idx, open_state):
            # start_idx is MCP index: 5 (index), 9 (middle), 13 (ring), 17 (pinky)
            mcp = start_idx
            pip = start_idx + 1
            dip = start_idx + 2
            tip = start_idx + 3
            
            lm[mcp] = [0.5, 0.6, 0.0]
            if open_state:
                # Extended upwards (smaller y)
                lm[pip] = [0.5, 0.5, 0.0]
                lm[dip] = [0.5, 0.4, 0.0]
                lm[tip] = [0.5, 0.3, 0.0]
            else:
                # Curled downwards (larger y)
                lm[pip] = [0.5, 0.7, 0.0]
                lm[dip] = [0.5, 0.8, 0.0]
                lm[tip] = [0.5, 0.85, 0.0]

        # Set 4 standard fingers
        set_finger(5, index_open)
        set_finger(9, middle_open)
        set_finger(13, ring_open)
        set_finger(17, pinky_open)
        
        # 2. Set Thumb coordinates
        lm[1] = [0.5, 0.8, 0.0]
        lm[2] = [0.45, 0.75, 0.0]
        lm[3] = [0.42, 0.73, 0.0]
        
        if thumb_open:
            # Extended horizontally outwards for Right hand (smaller x)
            # Or Y is slightly upward
            lm[4] = [0.38, 0.71, 0.0]
        else:
            # Curled inwards (closer to palm)
            lm[4] = [0.46, 0.75, 0.0]
            
        # 3. Handle Pinch / OK state specifically
        if pinch:
            # Override index tip and thumb tip to be extremely close
            lm[4] = [0.4, 0.4, 0.0] # Thumb tip
            lm[8] = [0.41, 0.41, 0.0] # Index tip (very close to thumb tip)
            
        return lm

    def test_open_palm(self):
        # All open
        lm = self.create_mock_landmarks(index_open=True, middle_open=True, ring_open=True, pinky_open=True, thumb_open=True)
        gesture = self.detector._classify_gesture(lm, "Right")
        self.assertEqual(gesture, "Open Palm")

    def test_fist(self):
        # All closed
        lm = self.create_mock_landmarks(index_open=False, middle_open=False, ring_open=False, pinky_open=False, thumb_open=False)
        gesture = self.detector._classify_gesture(lm, "Right")
        self.assertEqual(gesture, "Fist")

    def test_pointing(self):
        # Only index open
        lm = self.create_mock_landmarks(index_open=True, middle_open=False, ring_open=False, pinky_open=False, thumb_open=False)
        gesture = self.detector._classify_gesture(lm, "Right")
        self.assertEqual(gesture, "Pointing")

    def test_victory(self):
        # Index and Middle open, others closed
        lm = self.create_mock_landmarks(index_open=True, middle_open=True, ring_open=False, pinky_open=False, thumb_open=False)
        gesture = self.detector._classify_gesture(lm, "Right")
        self.assertEqual(gesture, "Victory")

    def test_pinch(self):
        # Thumb and Index tip touching
        lm = self.create_mock_landmarks(pinch=True)
        gesture = self.detector._classify_gesture(lm, "Right")
        self.assertEqual(gesture, "Pinch")

if __name__ == '__main__':
    unittest.main()
