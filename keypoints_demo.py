from tkinter import *
from tkinter import ttk
import tkinter as tk
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import envisionhardware

# Main window setup
root = Tk()
root.title("Keypoints Demo")
root.geometry("1050x570+150+50")
root.configure(bg="#f2f3f5")
root.resizable(True, True)  # Allow window resizing
root.attributes('-topmost', True)

# Constants
KEYPOINT_COLORS = {
    # WRIST
    0: "red",
    # THUMB
    1: "blue", 2: "blue", 3: "blue", 4: "blue",
    # INDEX FINGER
    5: "green", 6: "green", 7: "green", 8: "green",
    # MIDDLE FINGER
    9: "purple", 10: "purple", 11: "purple", 12: "purple",
    # RING FINGER
    13: "orange", 14: "orange", 15: "orange", 16: "orange",
    # PINKY
    17: "cyan", 18: "cyan", 19: "cyan", 20: "cyan"
}

# Create the canvas for drawing keypoints
canvas = Canvas(root, width=930, height=500, background="white")
canvas.place(x=0, y=10)

# # Create color section box like in whiteboard
# color_box = PhotoImage(file="whiteboard/color_section.png")
# Label(root, image=color_box, bg="#f2f3f5").place(x=10, y=20)

# Create a clear button
clear_button = Button(root, text="Clear", bg="#f2f3f5", command=lambda: canvas.delete("keypoints"))
clear_button.place(x=30, y=400)

# Variables to track the keypoints being displayed
keypoint_ids = []
connection_ids = []

def clear_keypoints():
    """Clear all keypoints from the canvas."""
    canvas.delete("keypoints")
    keypoint_ids.clear()

def clear_connections():
    """Clear all connections from the canvas."""
    canvas.delete("connections")
    connection_ids.clear()


def draw_keypoints(landmarks):
    """Draw all keypoints on the canvas."""
    # Clear previous keypoints
    clear_keypoints()
    
    
    if not landmarks:
        return
    
    # Canvas dimensions
    canvas_width = 930
    canvas_height = 500
    
    # Draw each keypoint
    for i, landmark in enumerate(landmarks):
        if i >= 21:  # Only draw the 21 hand landmarks
            break
            
        # Map coordinates to canvas size
        # Invert X coordinate to mirror the hand
        x = int(canvas_width - (landmark[0] * canvas_width))
        y = int(landmark[1] * canvas_height)
        
        # Get color for this keypoint
        color = KEYPOINT_COLORS.get(i, "black")
        
        # Draw the keypoint as a small circle
        keypoint = canvas.create_oval(
            x-5, y-5, x+5, y+5, 
            fill=color, 
            outline="black",
            tags="keypoints"
        )
        keypoint_ids.append(keypoint)
        
        # Add keypoint label
        canvas.create_text(
            x, y-15, 
            text=str(i), 
            fill="black",
            font=("Arial", 8),
            tags="keypoints"
        )

def draw_connections(landmarks):
    """Draw lines connecting related keypoints."""
    # Clear previous connections
    clear_connections()
    
    if not landmarks:
        return
        
    # Finger connections
    connections = [
        # Thumb
        (0, 1), (1, 2), (2, 3), (3, 4),
        # Index finger
        (0, 5), (5, 6), (6, 7), (7, 8),
        # Middle finger
        (0, 9), (9, 10), (10, 11), (11, 12),
        # Ring finger
        (0, 13), (13, 14), (14, 15), (15, 16),
        # Pinky
        (0, 17), (17, 18), (18, 19), (19, 20),
        # Palm
        (0, 5), (5, 9), (9, 13), (13, 17)
    ]
    
    canvas_width = 930
    canvas_height = 500
    
    for start_idx, end_idx in connections:
        if start_idx < len(landmarks) and end_idx < len(landmarks):
            start = landmarks[start_idx]
            end = landmarks[end_idx]
            
            # Map coordinates to canvas size
            start_x = int(canvas_width - (start[0] * canvas_width))
            start_y = int(start[1] * canvas_height)
            end_x = int(canvas_width - (end[0] * canvas_width))
            end_y = int(end[1] * canvas_height)
            
            # Draw the connection
            connection_ids.append(canvas.create_line(
                start_x, start_y, end_x, end_y,
                width=2,
                fill="gray",
                tags="connections"
            ))
            

def handle_detection(_, event_type):
    """Handle detection of gestures or landmarks."""
    if event_type == "landmarks":
        landmarks = envision.right_landmarks
        
        # Draw connections first (so they appear behind the keypoints)
        draw_connections(landmarks)
        
        # Then draw the keypoints
        draw_keypoints(landmarks)
        
        # Display information about the gesture
        gesture_label.config(text=f"Gesture: {envision.right_gesture}")
        
        # Display the number of landmarks detected
        count_label.config(text=f"Landmarks: {len(landmarks)}")

# Initialize Envision
envision = envisionhardware.Envision()

# Create labels for information display
info_frame = Frame(root, bg="#f2f3f5")
info_frame.place(x=30, y=450)

gesture_label = Label(info_frame, text="Gesture: None", bg="#f2f3f5")
gesture_label.pack(anchor="w")

count_label = Label(info_frame, text="Landmarks: 0", bg="#f2f3f5")
count_label.pack(anchor="w")

# Start Envision in a new thread
envision.start()
envision.set_update_callback(handle_detection)

# Main loop
root.mainloop()

# Cleanup on exit
envision.stop()
