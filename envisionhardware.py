import asyncio
import threading
import struct
import base64
from bleak import BleakClient, BleakScanner
import contextlib

DEVICE_NAME = "envision"
DEVICE_ADDRESS = "2C:CF:67:0A:8A:F1"
SERVICE_UUID = "00000000-0000-0000-0000-0000feedc0de"
GESTURE_CHAR_UUID = "00000000-0000-0000-0000-0000feedc0df"
LANDMARK_CHAR_UUID = "00000000-0000-0000-0000-0000feedc0dd"

class Envision:
    def __init__(self):
        # Define accessible gestures
        self.left_gesture = ""
        self.right_gesture = ""
        self.left_landmarks = []
        self.right_landmarks = []
        self.right_pinch_strength = 0

        # Bluetooth utils
        self.quit_event = asyncio.Event()
        self.debug = True
        self.update_callback = None
        self.thread = None

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

    def set_update_callback(self, func):
        self.update_callback = func

    async def _run(self):

        scan = BleakScanner()
        device = await scan.find_device_by_name(DEVICE_NAME)
        if device is None:
            print(f"Device {DEVICE_NAME} not found")
            return

        try:
            async with BleakClient(device) as client:

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

        if self.update_callback:
            self.update_callback(self, "landmarks")

        if self.debug:
            #print("Updated landmarks")
            #print(self.right_landmarks)
            pass
