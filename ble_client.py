import asyncio
from bleak import BleakClient, BleakScanner
import base64
import struct

# Device and characteristic information
DEVICE_NAME = "envision"
DEVICE_ADDRESS = "2C:CF:67:0A:8A:F1"
SERVICE_UUID = "00000000-0000-0000-0000-0000feedc0de"
GESTURE_CHAR_UUID = "00000000-0000-0000-0000-0000feedc0df"
LANDMARK_CHAR_UUID = "00000000-0000-0000-0000-0000feedc0dd"

async def gesture_notification_handler(sender, data):
    print(f"Gesture: {data.decode("utf-8")}")

async def landmark_notification_handler(sender, data):
    print(f"Notification received from {sender}: {data.decode("utf-8")}")

    binary_data = base64.b64decode(data)
    num_floats = len(binary_data) // 4
    floats = struct.unpack(f'{num_floats}f', binary_data)
    print([tuple(floats[i:i+3]) for i in range(0, num_floats, 3)])

def discon_callback(client):
    print("Disconnected")
    print(client)
    
async def run():
    
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
            await client.start_notify(GESTURE_CHAR_UUID, gesture_notification_handler)

            print(f"Subscribing to characteristic {LANDMARK_CHAR_UUID}...")
            print(await client.read_gatt_char(LANDMARK_CHAR_UUID));
            await client.start_notify(LANDMARK_CHAR_UUID, landmark_notification_handler)
            
            print("Subscribed! Waiting for notifications (press Ctrl+C to stop)...")
            
            # Keep the program running to receive notifications
            while True:
                await asyncio.sleep(1)
            print("Finished infinite loop")
            
                
    except asyncio.CancelledError:
        # Handle clean exit with Ctrl+C
        print("Program cancelled")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
