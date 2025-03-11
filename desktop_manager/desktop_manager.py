import pyautogui
import time
import sys
import os
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import envision

def trigger_swipe(direction):
    if direction == "left":
        pyautogui.hotkey("ctrl", "left")  # Switch to previous desktop
    elif direction == "right":
        pyautogui.hotkey("ctrl", "right")  # Switch to next desktop
    elif direction == "up":
        pyautogui.hotkey("f9")  # Open Mission Control
    elif direction == "down":
        pyautogui.hotkey("ctrl", "down")  # Open App Exposé

def handle_detection(detection):

    if "right_gesture" in detection:
        if detection['right_gesture'] == "Victory":
            print("Switching to next desktop...")
            trigger_swipe("right")
        elif detection['right_gesture'] == "Open_Palm":
            print("Opening Mission Control...")
            trigger_swipe("up")

    time.sleep(0.5)  # Small delay to prevent rapid execution

if __name__ == "__main__":

    envision = envision.Envision()
    envision.set_callback(handle_detection)

    envision_thread = threading.Thread(target=envision.start, daemon=True)
    envision_thread.start()

    # Keep the main thread alive
    try:
        envision_thread.join()
    except KeyboardInterrupt:
        print("Exiting program...")
        envision.stop()