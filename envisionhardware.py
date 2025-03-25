import asyncio
import threading
import struct
import base64
from bleak import BleakClient, BleakScanner
import math
import contextlib

DEVICE_NAME = "envision"
DEVICE_ADDRESS = "2C:CF:67:0A:8A:F1"
SERVICE_UUID = "cb318b24-7544-49fb-941d-b921627de801"
GESTURE_CHAR_UUID = "cb318b24-7544-49fb-941d-f75f38cc4d72"
LANDMARK_CHAR_UUID = "cb318b24-7544-49fb-941d-d00ef2a11cb0"

class Envision:
    def __init__(self):
        # Define accessible gestures
        self.left_gesture = ""
        self.right_gesture = ""
        self.left_landmarks = []
        self.right_landmarks = []
        self.right_pinch_distance = 0

        # Bluetooth utils
        self.quit_event = asyncio.Event()
        self.debug = True
        self.update_callback = None
        self.thread = None
        self.tracking = []

    def start(self):
        self.quit_event.clear()
        self.thread = threading.Thread(target=lambda: asyncio.run(self._run()), daemon=True)
        self.thread.start()

    def stop(self):
        print("Setting quit")
        self.quit_event.set()
        print("Quit event is set, joining envision thread")
        if isinstance(self.thread, threading.Thread):
            self.thread.join()
        print("Joined")

    def start_tracking(self, property):
        if not property in self.tracking:
            self.tracking.append(property)

    def stop_tracking(self, property):
        try:
            self.tracking.remove(property)
        except ValueError:
            pass

    def distance(self, f1, f2):
        if type(f1) != type(f2):
            return False
        if isinstance(f1, int):
            f1 = self.right_landmarks[f1]
            f2 = self.right_landmarks[f2]
        # print(math.sqrt(sum((a-b)**2 for a, b in zip(f1, f2))))
        return math.sqrt(sum((a-b)**2 for a, b in zip(f1, f2)))

    def touching(self, f1, f2, threshold = 0.01):
        return self.distance(f1, f2) < threshold

    def set_update_callback(self, func):
        self.update_callback = func

    async def _run(self):

        # Connect to device
        attempt_count = 0
        devices = None
        print("Searching for device...", end="", flush=True)
        while attempt_count < 30 and not devices:
            devices = await BleakScanner.discover(timeout=0.5, service_uuids=[SERVICE_UUID])
            attempt_count += 1
            print(".", end="", flush=True)

        if devices:
            print("Found!")
            print(devices[0])
            device = devices[0]
        else:
            print("Unable to find device")
            return

        try:
            async with BleakClient(DEVICE_ADDRESS) as client:

                print(f"Connected to {client.address}")
                print(f"Subscribing to gesture characteristic")
                await client.start_notify(GESTURE_CHAR_UUID, self._gesture_notification_handler)

                print(f"Subscribing to landmark characteristic")
                await client.start_notify(LANDMARK_CHAR_UUID, self._landmark_notification_handler)
                print("Subscribed!")

                while not self.quit_event.is_set():
                    with contextlib.suppress(asyncio.TimeoutError):
                        await asyncio.wait_for(self.quit_event.wait(), timeout=1)
                print("Finished infinite loop")
        except Exception as e:
            print(f"Error in ble thread: {e}")

    async def _gesture_notification_handler(self, sender, data):
        self.right_gesture = data.decode("utf-8")
        if self.debug:
            print(f"Gesture: {self.right_gesture}")

        if self.update_callback:
            self.update_callback(self, "gesture")

    async def _landmark_notification_handler(self, sender, data):
        # Decode base64 data into list of 3d coords
        binary_data = base64.b64decode(data)
        num_floats = len(binary_data) // 4
        floats = struct.unpack(f'{num_floats}f', binary_data)
        self.right_landmarks = [tuple(floats[i:i+3]) for i in range(0, num_floats, 3)]

        # Various tracking properties
        for prop in self.tracking:
            if prop == "right_pinch_distance":
                self.right_pinch_distance = self.distance(4, 8)

        if self.update_callback:
            self.update_callback(self, "landmarks")

        if self.debug:
            #print("Updated landmarks")
            #print(self.right_landmarks)
            pass
