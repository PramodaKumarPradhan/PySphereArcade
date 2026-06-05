import os
import sys
import time
import cv2
import numpy as np
import pyautogui

def record_desktop(output_file="desktop_recording.avi", fps=20.0):
    """
    Captures the local desktop screen at a specified frame rate and compiles
    it into an AVI video file. Shows a small, resizeable preview window.
    Press 'q' in the preview window to stop.
    """
    # Verify screen size
    screen_width, screen_height = pyautogui.size()
    screen_size = (screen_width, screen_height)
    
    # Define video codec ('XVID' is standard and works well on Windows/macOS/Linux)
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(output_file, fourcc, fps, screen_size)
    
    print("\n" + "="*50)
    print("            NEXUS DESKTOP SCREEN RECORDER")
    print("="*50)
    print(f"[*] Resolution: {screen_width}x{screen_height}")
    print(f"[*] Target FPS: {fps}")
    print(f"[*] Output File: {os.path.abspath(output_file)}")
    print("-"*50)
    print("[!] INSTRUCTIONS:")
    print("    - A small preview window will open shortly.")
    print("    - Keep this terminal running in the background.")
    print("    - Click on the preview window and press 'q' to STOP recording.")
    print("="*50 + "\n")
    
    # Preview Window setup
    window_name = "Nexus Screen Recorder - Recording..."
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 480, 270) # Small scaled down preview window
    
    frame_delay = 1.0 / fps
    start_time = time.time()
    frames_written = 0
    
    try:
        while True:
            loop_start = time.time()
            
            # 1. Grab screenshot
            screenshot = pyautogui.screenshot()
            
            # 2. Convert to numpy array
            frame = np.array(screenshot)
            
            # 3. Convert from RGB (pyautogui) to BGR (OpenCV)
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # 4. Write frame to file
            out.write(frame_bgr)
            frames_written += 1
            
            # 5. Show preview frame
            cv2.imshow(window_name, frame_bgr)
            
            # Calculate elapsed time and print stats periodically
            elapsed = time.time() - start_time
            if frames_written % 40 == 0:
                print(f"[*] Recorded {frames_written} frames ({elapsed:.1f}s elapsed)...", end="\r")
            
            # 6. Stop if 'q' is pressed in OpenCV window
            # We wait for the remainder of the frame duration to enforce FPS pacing
            processing_time = time.time() - loop_start
            sleep_time = max(1, int((frame_delay - processing_time) * 1000))
            
            if cv2.waitKey(sleep_time) & 0xFF == ord('q'):
                print("\n[+] Recording stopped via key command.")
                break
                
    except KeyboardInterrupt:
        print("\n[!] Recording interrupted by terminal command.")
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
    finally:
        # Clean up resources safely
        out.release()
        cv2.destroyAllWindows()
        print("-"*50)
        print(f"[+] Screen Recorder Shutdown Cleanly.")
        print(f"[+] Total frames recorded: {frames_written}")
        print(f"[+] Final Video Saved: {os.path.abspath(output_file)}")
        print("="*50 + "\n")

if __name__ == "__main__":
    # Allow passing custom filename via command line args
    output_name = sys.argv[1] if len(sys.argv) > 1 else "desktop_recording.avi"
    record_desktop(output_file=output_name)
