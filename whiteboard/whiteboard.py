from tkinter import *
from tkinter.colorchooser import askcolor
from tkinter import ttk
import tkinter as tk

import sys
import os



# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import envisionhardware

root = Tk()
root.title("White Board")
root.geometry("1050x570+150+50")
root.configure( bg="#f2f3f5")
root.resizable(False,False)

current_x = 0
current_y = 0
color = 'black'


def locate_xy(work):

    global current_x, current_y
    #current_x = work.x
    #current_y = work.y
    current_x = x
    current_y = y

def addLine(work):
    global current_x, current_y

    canvas.create_line((current_x,current_y,x,y),width=get_current_value(),fill=color,
                       capstyle=ROUND, smooth=TRUE)
    current_x, current_y = x, y

def show_color(new_color):
    global color
     
    color = new_color

def new_canvas():

    canvas.delete('all')
    display_pallette()

#icon
image_icon= PhotoImage(file="logo.png")
root.iconphoto(False, image_icon)

color_box = PhotoImage(file = "color_section.png")
Label(root, image=color_box,bg="#f2f3f5").place(x=10,y=20)

eraser=PhotoImage(file="eraser.png")
Button(root, image=eraser, bg="#f2f3f5", command=new_canvas).place(x=30,y=400)

colors= Canvas(root,bg="#ffffff",width=37,height=300,bd=0)
colors.place(x=30, y=60)

def display_pallette():
    id = colors.create_rectangle((10,10,30,30),fill="black")
    colors.tag_bind(id, '<Button-1>', lambda x: show_color('black'))

    id = colors.create_rectangle((10,40,30,60),fill="gray")
    colors.tag_bind(id, '<Button-1>', lambda x: show_color('gray'))

    id = colors.create_rectangle((10,70,30,90),fill="brown4")
    colors.tag_bind(id, '<Button-1>', lambda x: show_color('brown4'))

    id = colors.create_rectangle((10,100,30,120),fill="red")
    colors.tag_bind(id, '<Button-1>', lambda x: show_color('red'))

    id = colors.create_rectangle((10,130,30,150),fill="orange")
    colors.tag_bind(id, '<Button-1>', lambda x: show_color('orange'))

    id = colors.create_rectangle((10,160,30,180),fill="yellow")
    colors.tag_bind(id, '<Button-1>', lambda x: show_color('yellow'))

    id = colors.create_rectangle((10,190,30,210),fill="green")
    colors.tag_bind(id, '<Button-1>', lambda x: show_color('green'))

    id = colors.create_rectangle((10,220,30,240),fill="blue")
    colors.tag_bind(id, '<Button-1>', lambda x: show_color('blue'))

    id = colors.create_rectangle((10,250,30,270),fill="purple")
    colors.tag_bind(id, '<Button-1>', lambda x: show_color('purple'))
 
display_pallette()


canvas= Canvas(root,width=930, height=500, background="white",cursor="hand2")
canvas.place(x=100, y=10)

canvas.bind('<Button-1>', locate_xy)
canvas.bind('<B1-Motion>', addLine)

########SLIDER########
current_value = tk.DoubleVar()

def get_current_value():
    return '{: .2f}'.format(current_value.get())

def slider_changed(event):
    value_label.configure(text=get_current_value())

slider = ttk.Scale(root, from_=0,to=100, orient="horizontal",command=slider_changed, variable=current_value)
slider.place(x=30,y=530)

#value label
value_label = ttk.Label(root,text = get_current_value())
value_label.place(x=27,y=550)

"""THE FOLLOWING CODE CONTAINS THE INTEGRATION OF ENVISION
    AND IS SEPARATE FROM THE BASE WHITEBOARD APP."""

def map_to_canvas(norm_x, norm_y):
    canvas_width = 930
    canvas_height = 500
    x = int(norm_x * canvas_width)
    y = int(norm_y * canvas_height)
    return x, y

'''def get_coordinates():
    landmarks = envision.get_right_landmarks()
    x, y = 0, 0
    if landmarks:
        index_tip = landmarks[8]  # Index finger tip
        global x, y
        x, y = int(index_tip[0] * 930), int(index_tip[1] * 500)
    return x,y '''

drawing = False  # Track whether we're actively drawing

def handle_detection(_, __):
    """Handle detection results (gestures or landmarks) as a moving cursor."""
    global cursor_dot, current_x, current_y, drawing
    landmarks = envision.right_landmarks
    
    if landmarks:
        index_tip = landmarks[8]  # Index finger tip
        global x, y
        x, y = int(930 - (index_tip[0] * 930)), int(index_tip[1] * 500)  # Scale to canvas size
        # Remove the previous dot before drawing the new one
        canvas.delete("cursor_dot")
        cursor_dot = canvas.create_oval(x-5, y-5, x+5, y+5, fill=color, tags="cursor_dot")

        if envision.right_gesture == "Pointing_Up":
            if not drawing:  # If starting a new drawing, reset the previous position
                current_x, current_y = x, y
                drawing = True  # Now in drawing mode
            addLine(1)
        else:
            drawing = False  # Reset when hand is lifted

        if envision.right_gesture == "Open_Palm":
            new_canvas()

envision = envisionhardware.Envision()

# Start Envision in a new thread
envision.start()
envision.set_update_callback(handle_detection)


root.mainloop()
envision.stop()
