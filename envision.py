from handRecognition import gestureEngine 
import threading
import time

def runEngine(engine):
    engine.main()
    
def isThumbsUp(engine):
    return engine.check_gesture("Thumb_Up")

def isThumbsDown(engine):
    return engine.check_gesture("Thumb_Down")

def isVictory(engine):
    return engine.check_gesture("Victory")

def isOpenPalm(engine):
    return engine.check_gesture("Open_Palm")

def isClosedFist(engine):
    return engine.check_gesture("Closed_Fist")

def isILoveYou(engine):
    return engine.check_gesture("ILoveYou")


if __name__ == '__main__':
    engine = gestureEngine()    
    thumbUp_thread = threading.Thread(target=isThumbsUp, args=(engine,))
        
    thumbUp_thread.start()
    runEngine(engine)


    thumbUp_thread.join()
    
    