import argparse
import numpy as np
import cv2
import tkinter as tk
from PIL import Image, ImageTk

#get arguments
parser = argparse.ArgumentParser()

parser.add_argument('--infile', type=str, required=True,
                    help="input file in .mp4, .avi, .mov, or .mkv format")

parser.add_argument('--fps', type=int, default=60,
                    help="video replay frame rate, frames per second")

parser.add_argument('--info', action='store_true',
                    help="output video information")

args = parser.parse_args()
vfile = args.infile

fps = args.fps
spf = float(1.0/fps)

cap = cv2.VideoCapture(vfile)

#Set up GUI
window = tk.Tk()  #Makes main window
window.wm_title("Digital Microscope")
window.config(background="#FFFFFF")

#Graphics window
imageFrame = tk.Frame(window, width=600, height=500)
imageFrame.grid(row=0, column=0, padx=10, pady=2)

#Capture video frames
lmain = tk.Label(imageFrame)
lmain.grid(row=0, column=0)
#cap = cv2.VideoCapture(0)

def show_frame():
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    if frame is None: return 
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(10, show_frame) 



#Slider window (slider controls stage position)
sliderFrame = tk.Frame(window, width=600, height=100)
sliderFrame.grid(row = 600, column=0, padx=10, pady=2)


show_frame()  #Display 2
window.mainloop()  #Starts GUI
