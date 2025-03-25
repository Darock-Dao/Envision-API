import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2
from picamera2 import Picamera2
from mediapipe import Image, ImageFormat
from mediapipe.tasks.vision import (
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
    if os.path.exists("/tmp/gesture-ipc.sock"):
        gesture_client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        gesture_client.connect("/tmp/gesture-ipc.sock")
    else:
        raise Exception("Couldn't connect to /tmp/gesture-ipc.sock")

    if os.path.exists("/tmp/landmark-ipc.sock"):
        landmark_client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        landmark_client.connect("/tmp/landmark-ipc.sock")
    else:
        raise Exception("Couldn't connect to /tmp/landmark-ipc.sock")

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
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BRG2RGB)
    return Image(data=rgb_image, image_format=ImageFormat.SRGB)

current_gesture = None
def process_result(sockets, result, output_image):

    ( gesture_socket, landmark_socket ) = sockets
    if result.gestures: # At least one hand exists
        top_gesture = result.gestures[0][0]
        gesture_name = top_gesture.category_name
        hand_landmarks = result.hand_landmarks[0]

        if gesture_name != current_gesture:
            print(f"Gesture: {gesture_name}")
            if gesture_socket:
                gesture_socket.sendall(f"{gesture_name}\n".encode())

        if landmark_socket:
            binary_data = struct.pack(f"{len(hand_landmarks) * 3}",
                                      *(v for d in hand_landmarks for v in (d.x, d.y, d.z)))
            landmark_socket.sendall(base64.b64encode(binary_data) + b'\n')

def run_recognition():

    cam = start_camera()
    sockets = setup_sockets()
    options = GestureRecognizerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=MODEL_ASSET_PATH),
        running_mode=RunningMode.LIVE_STREAM,
        result_callback=functools.partial(process_result, sockets))

    with GestureRecognizer.create_from_options(options) as recognizer:

        while cam.is_open: # This line is pi camera specific
            mp_image = capture_frame(cam)

            recognizer.recognize_async(mp_image, time.time_ns() // 1_000_000)
