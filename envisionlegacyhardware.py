import asyncio
import struct
import base64
from bleak import BleakClient

DEVICE_NAME = "envision"
DEVICE_ADDRESS = "2C:CF:67:0A:8A:F1"
SERVICE_UUID = "00000000-0000-0000-0000-0000feedc0de"
GESTURE_CHAR_UUID = "00000000-0000-0000-0000-0000feedc0df"
LANDMARK_CHAR_UUID = "00000000-0000-0000-0000-0000feedc0dd"

class Envision:
    def __init__(self):
        self.left_hand_gesture = ""
        self.right_hand_gesture = ""
        self.left_landmarks = []
        self.right_landmarks = []
        self._running = False
        self.debug = True
        self.callback = None

    def start(self):
        self._running = True
        asyncio.run(self.run())

    def stop(self):
        pass

    def get_right_landmarks(self):
        return self.right_landmarks

    def rightIsPointingUp(self):
        return self.right_hand_gesture == "Pointing_Up"

    def set_callback(self, func):
        self.callback = func

    #### BLE INTEGRATION
    async def run(self):
        try:
            async with BleakClient(DEVICE_ADDRESS) as client:
                print(f"Connected to {client.address}")

                # Check if the service exists
                #services = await client.get_services()
                #if SERVICE_UUID.lower() not in [service.uuid.lower() for service in services]:
                #    print(f"Service {SERVICE_UUID} not found on device")
                #    return

                # Start notification
                print(f"Subscribing to characteristic {GESTURE_CHAR_UUID}...")
                print(await client.read_gatt_char(GESTURE_CHAR_UUID));
                await client.start_notify(GESTURE_CHAR_UUID, self._gesture_notification_handler)

                print(f"Subscribing to characteristic {LANDMARK_CHAR_UUID}...")
                print(await client.read_gatt_char(LANDMARK_CHAR_UUID));
                await client.start_notify(LANDMARK_CHAR_UUID, self._landmark_notification_handler)

                print("Subscribed! Waiting for notifications (press Ctrl+C to stop)...")

                # Keep the program running to receive notifications
                while self._running:
                    await asyncio.sleep(.05)
                    if self.callback:
                        self.callback(None)
                print("Finished infinite loop")

        except asyncio.CancelledError:
            # Handle clean exit with Ctrl+C
            print("Program cancelled")
        except Exception as e:
            print(f"Error: {e}")

    async def _gesture_notification_handler(self, sender, data):
        self.right_hand_gesture = data.decode("utf-8")

        if self.debug:
            print(f"Gesture: {self.right_hand_gesture}")

    async def _landmark_notification_handler(self, sender, data):
        binary_data = base64.b64decode(data)
        num_floats = len(binary_data) // 4
        floats = struct.unpack(f'{num_floats}f', binary_data)
        self.right_landmarks = [tuple(floats[i:i+3]) for i in range(0, num_floats, 3)]
