from handRecognition import gestureEngine 
import threading
import time

class Envision:
    def __init__(self):
        self.engine = gestureEngine()
        self.left_hand_gesture = ""
        self.right_hand_gesture = ""
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

    def leftIsThumbsUp(self):
        return self.engine.checkLeftGesture("Thumb_Up")

    def leftIsThumbsDown(self):
        return self.engine.checkLeftGesture("Thumb_Down")
    
    def leftIsPointingUp(self):
        return self.engine.checkLeftGesture("Pointing_Up")

    def leftIsVictory(self):
        return self.engine.checkLeftGesture("Victory")

    def leftIsOpenPalm(self):
        return self.engine.checkLeftGesture("Open_Palm")

    def leftIsClosedFist(self):
        return self.engine.checkLeftGesture("Closed_Fist")

    def leftIsILoveYou(self):
        return self.engine.checkLeftGesture("ILoveYou")
    
    def rightIsThumbsUp(self):
        return self.engine.checkRightGesture("Thumb_Up")

    def rightIsThumbsDown(self):
        return self.engine.checkRightGesture("Thumb_Down")
    
    def rightIsPointingUp(self):
        return self.engine.checkRightGesture("Pointing_Up")

    def rightIsVictory(self):
        return self.engine.checkRightGesture("Victory")

    def rightIsOpenPalm(self):
        return self.engine.checkRightGesture("Open_Palm")

    def rightIsClosedFist(self):
        return self.engine.checkRightGesture("Closed_Fist")

    def rightIsILoveYou(self):
        return self.engine.checkRightGesture("ILoveYou")
    
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
                #Note: Uses the opposite hand because camera is mirrored
                left_gesture = self.engine.getRightHandGesture()
                right_gesture = self.engine.getLeftHandGesture()
                landmarks_list = self.engine.getCurrentLandmarks()

                detection = {}
                if left_gesture:
                    detection["left_gesture"] = left_gesture
                if right_gesture:
                    detection["right_gesture"] = right_gesture

                # Extract and include landmarks for each hand
                if landmarks_list:
                    left_landmarks, right_landmarks = [], []
                    for hand_index, hand_landmarks in enumerate(landmarks_list[0].hand_landmarks):
                        handedness = landmarks_list[0].handedness[hand_index][0].category_name
                        landmarks = [(landmark.x, landmark.y, landmark.z) for landmark in hand_landmarks]
                        
                        if handedness == "Left":
                            left_landmarks = landmarks
                        if handedness == "Right":
                            right_landmarks = landmarks

                    # Swap because camera is mirrored
                    detection["left_landmarks"] = right_landmarks
                    detection["right_landmarks"] = left_landmarks

                # Trigger callback if gestures are detected
                if detection and self.callback:
                    self.callback(detection)

                    # Trigger callback only if there is new data
                    if detection and self.callback:
                        self.callback(detection)

            except Exception as e:
                print(f"Callback processing error: {e}")
            time.sleep(0.025)

def handle_detection(detection):
    """Handle detection results (gestures or landmarks)."""

    if "left_gesture" in detection:
        print(f"Left Hand Gesture: {detection['left_gesture']}")
    if "right_gesture" in detection:
        print(f"Right Hand Gesture: {detection['right_gesture']}")
    if "left_landmarks" in detection:
        print(f"Left Hand Landmarks: {detection['left_landmarks']}")
    if "right_landmarks" in detection:
        print(f"Right Hand Landmarks: {detection['right_landmarks']}")

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
    