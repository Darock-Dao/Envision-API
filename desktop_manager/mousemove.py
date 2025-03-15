import pyautogui
import sys
import os
import time
import subprocess

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import envisionhardware

frame_count = 0

def handle_update(e, type):
    global frame_count

    if type == "landmarks":

        # g.check_input(e.right_gesture, e.right_landmarks[8][:2], (1920, 1080))
        pointer = e.right_landmarks[8]
        #print(pointer)
        x = int(1440 - (pointer[0] * 1440))
        y = int(pointer[1] * 900)
        print(f"X: {x}, Y: {y}")
        #subprocess.run(["sudo", "ydotool", "mousemove", "-a", "-x" , str(x), "-y", str(y)])
        if frame_count == 3:
            pyautogui.moveTo(x, y)
            frame_count = 0
        else:
            frame_count += 1

if __name__ == "__main__":
    envision = envisionhardware.Envision()
    envision.set_update_callback(handle_update)
    envision.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Exiting program")
        envision.stop()
