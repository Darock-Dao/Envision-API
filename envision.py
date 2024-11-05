from handRecognition import gestureEngine 
import threading
import time

class Envision:
    def __init__(self):
        self.engine = gestureEngine()
        self.current_gesture = ""
        self.callback = None
        self._running = False
        self._callback_thread = None
    
    def start(self):
        self._running = True
        self._callback_thread = threading.Thread(target=self.run_with_callback)
        self._callback_thread.start()
        self.engine.main()

    def stop(self):
        self._running = False
        if self._callback_thread:
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
    
    def run_with_callback(self):
        """Run the recognizer and trigger the callback when gestures are detected."""
        while True:
            if self.callback and self.engine.getCurrentGesture() != self.current_gesture:
                self.current_gesture = self.engine.getCurrentGesture()
                self.callback(self.current_gesture)
            time.sleep(0.1)

def handle_gesture(gesture):
    print(f"Detected gesture: {gesture}")
    
if __name__ == '__main__':
    envision = Envision()
    envision.set_callback(handle_gesture)
    
    try:
        envision.start()  # This will run the OpenCV loop in the main thread
    except KeyboardInterrupt:
        print("Stopping Envision...")
        envision.stop()
    finally:
        envision.stop()  # Ensure cleanup if other exceptions occur
    