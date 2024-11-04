from handRecognition import gestureEngine 
import threading
import time

class Envision:
    def __init__(self):
        self.engine = gestureEngine()
    
    def runEngine(self):
        self.engine.main()

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


if __name__ == '__main__':
    envision = Envision()
    envision.runEngine()
    '''
    thumbUp_thread = threading.Thread(target=isThumbsUp, args=(engine,))
        
    thumbUp_thread.start()
    runEngine(engine)

    thumbUp_thread.join()
    '''
    