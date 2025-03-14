import pyautogui
import time
import sys
import os
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import envisionhardware

held_keys = []

def trigger_swipe(direction):
    global held_keys

    if direction == "left":
        pyautogui.hotkey("ctrl", "left")  # Switch to previous desktop
    elif direction == "right":
        pyautogui.hotkey("ctrl", "right")  # Switch to next desktop
    elif direction == "up":
        # Open Mission Control
        pyautogui.keyDown("f9")  # Hold F9 indefinitely
        print("Opening Mission Control...")
        if "f9" not in held_keys:
            held_keys.append("f9")
    elif direction == "down":
        pyautogui.hotkey("ctrl", "down")  # Open App Exposé

def handle_detection(envision, update_type):

    if update_type != "gesture":
        return
    
    if envision.right_gesture == "Victory":
        print("Switching to next desktop...")
        trigger_swipe("right")
    elif envision.right_gesture == "Thumb_Up":
        print("Switching to previous desktop...")
        trigger_swipe("left")
    elif envision.right_gesture == "Open_Palm":
        print("Opening Mission Control...")
        trigger_swipe("up")
    elif envision.right_gesture == "Closed_Fist":  # Close fist to release all held keys
        print("Releasing all held keys...")
        for key in held_keys:
            pyautogui.keyUp(key)  # Release all keys
        held_keys.clear()  # Clear the list of held keys

if __name__ == "__main__":

    envision = envisionhardware.Envision()
    envision.set_update_callback(handle_detection)

    envision.start()

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting program...")
        envision.stop()
