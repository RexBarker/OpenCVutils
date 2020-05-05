import cv2
import argparse
from time import time, sleep

parser = argparse.ArgumentParser()

parser.add_argument('--infile', type=str, required=True, 
                    help="input file in .mp4, .avi, .mov, or .mkv format")

parser.add_argument('--fps', type=int, default=60, 
                    help="video replay frame rate, frames per second")

parser.add_argument('--info', action='store_true', 
                    help="output video information")

args = parser.parse_args()
mp4file = args.infile 

fps = args.fps
spf = float(1.0/fps)

cap = cv2.VideoCapture(mp4file)

n_frames = 0
width,height = 0,0
current = 0.0
timesum = 0.0

while True:
    timediff = time() - current
    timesum += timediff

    if timediff < spf: 
        sleep(spf - timediff)

    current = time()
         
    ret, frame = cap.read()
    if frame is None: break

    height,width = frame.shape[:2]
    n_frames += 1

    cv2.imshow('frame',frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
         break

cap.release()
cv2.destroyAllWindows()

actual_fps = n_frames / timesum

if args.info:
    print(f"Number of frames: {n_frames}")
    print(f"Width x height = ({width},{height})")
    print(f"Actual replay speed = {actual_fps}/s")
