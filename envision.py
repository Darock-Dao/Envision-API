from handRecognition import gestureEngine 
import threading
import time

class Envision:
    def __init__(self):
        self.engine = gestureEngine()
        self.current_gesture = ""
        self.current_landmarks = []
        self.callback = None
        self._running = False
        self._callback_thread = None
    
    def start(self):
        self._running = True
        self._callback_thread = threading.Thread(target=self._process_callbacks)
        self._callback_thread.start()
        self.engine.main()

    def stop(self):
        self._running = False
        if self._callback_thread and self._callback_thread.is_alive():
            self._callback_thread.join()

    def set_callback(self, callback_func):
        """Optional: set a callback to run when a gesture is detected."""
        self.callback = callback_func

    def isThumbsUp(self):
        return self.engine.check_gesture("Thumb_Up")

    def isThumbsDown(self):
        return self.engine.check_gesture("Thumb_Down")
    
    def isPointingUp(self):
        return self.engine.check_gesture("Pointing_Up")

    def isVictory(self):
        return self.engine.check_gesture("Victory")

    def isOpenPalm(self):
        return self.engine.check_gesture("Open_Palm")

    def isClosedFist(self):
        return self.engine.check_gesture("Closed_Fist")

    def isILoveYou(self):
        return self.engine.check_gesture("ILoveYou")
    
    def run_with_gesture_callback(self):
        """Run the recognizer and trigger the callback when gestures are detected."""
        while self._running:
            if self.callback and self.engine.getCurrentGesture() != self.current_gesture:
                self.current_gesture = self.engine.getCurrentGesture()
                self.callback(self.current_gesture)
            time.sleep(0.1)

    def _process_callbacks(self):
        """Process callbacks for both gestures and landmarks."""
        while self._running:
            try:
                # Retrieve current gesture and landmarks
                new_gesture = self.engine.getCurrentGesture()
                new_landmarks = self.engine.getCurrentLandmarks()

                # Create a detection payload with both gesture and landmarks
                detection = {}
                if new_gesture != self.current_gesture:
                    self.current_gesture = new_gesture
                    detection["gesture"] = new_gesture
                else:   
                    detection["gesture"] = self.current_gesture

                if new_landmarks != self.current_landmarks:
                    self.current_landmarks = new_landmarks
                    detection["landmarks"] = new_landmarks
                else:
                    detection["landmarks"] = self.current_landmarks

                # Trigger callback only if there is new data
                if detection and self.callback:
                    self.callback(detection)

            except Exception as e:
                print(f"Callback processing error: {e}")
            time.sleep(0.025)

def print_gesture(gesture):
    print(f"Detected gesture: {gesture}")

def handle_detection(detection):
    """Handle detection results (gestures or landmarks)."""

    if "gesture" in detection:
        print(f"Detected gesture: {detection['gesture']}")
    if "landmarks" in detection:
        print(f"Detected landmarks: {detection['landmarks']}")

if __name__ == '__main__':
    envision = Envision()
    envision.set_callback(handle_detection)
    
    try:
        envision.start()  # This will run the OpenCV loop in the main thread
    except KeyboardInterrupt:
        print("Stopping Envision...")
        envision.stop()
    finally:
        envision.stop() # Ensure cleanup if other exceptions occur
    