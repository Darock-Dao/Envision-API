import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2
from picamera2 import Picamera2
from mediapipe import Image, ImageFormat
from mediapipe.tasks.python.vision import (
    GestureRecognizer, GestureRecognizerOptions,
    GestureRecognizerResult, RunningMode
)
import cv2

import time
import threading
import os
import socket
import base64
import struct
import functools

MODEL_ASSET_PATH = "../gesture_recognizer.task"

def setup_sockets():
    if os.path.exists("/tmp/envision-gesture.sock"):
        gesture_client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        gesture_client.connect("/tmp/envision-gesture.sock")
    else:
        raise Exception("Couldn't connect to /tmp/envision-gesture.sock")

    if os.path.exists("/tmp/envision-landmark.sock"):
        landmark_client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        landmark_client.connect("/tmp/envision-landmark.sock")
    else:
        raise Exception("Couldn't connect to /tmp/envision-landmark.sock")

    return gesture_client, landmark_client

def start_camera():
    picam = Picamera2()
    picam_config = picam.create_preview_configuration(
        main={
            'size':(640,480),
            'format': 'RGB888'
        },
    )
    picam.configure(picam_config)
    picam.start()

    return picam


def capture_frame(cam):
    image = cam.capture_array("main")
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return Image(data=rgb_image, image_format=ImageFormat.SRGB)

current_gesture = [None, None]
def process_result(sockets, result, output_image, timestamp):

    ( gesture_socket, landmark_socket ) = sockets
    assigned = [False, False] # Only assign the first left hand and first right hand
    if result.gestures: # At least one hand exists
        for gestures, hand_landmarks, handedness in zip(result.gestures, result.hand_landmarks, result.handedness):

            hand = handedness[0].category_name[0].lower() # 'l' or 'r'
            hand_index = 0 if hand == 'l' else 1
            gesture_name = gestures[0].category_name

            if gesture_name != current_gesture[hand_index]:
                print(f"Gesture: {hand}:{gesture_name}")
                if gesture_socket:
                    gesture_socket.sendall(f"{hand}:{gesture_name}\n".encode())

            if landmark_socket:
                binary_data = struct.pack(f"{len(hand_landmarks) * 3}f",
                                          *(v for d in hand_landmarks for v in (d.x, d.y, d.z)))
                landmark_socket.sendall(hand.encode() + base64.b64encode(binary_data) + b'\n')

def run_recognition():

    sockets = setup_sockets()
    cam = start_camera()
    options = GestureRecognizerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=MODEL_ASSET_PATH),
        running_mode=RunningMode.LIVE_STREAM,
        result_callback=functools.partial(process_result, sockets))

    with GestureRecognizer.create_from_options(options) as recognizer:

        while cam.is_open: # This line is pi camera specific
            mp_image = capture_frame(cam)

            recognizer.recognize_async(mp_image, time.time_ns() // 1_000_000)

run_recognition()
