import os
import cv2
import argparse
from glob import glob
from time import time, sleep

parser = argparse.ArgumentParser()

parser.add_argument('--infile', type=str, required=True, 
                    help="input file in .mp4, .avi, .mov, or .mkv format")

parser.add_argument('--fps', type=int, default=None, 
                    help="video replay frame rate, frames per second (default=60 fps)")

parser.add_argument('--rotate_right', action='store_true', 
                    help="Rotate image by 90 deg clockwise")

parser.add_argument('--rotate_left', action='store_true', 
                    help="Rotate image by 90 deg anticlockwise")

parser.add_argument('--info', action='store_true', 
                    help="output video information")


##### Helper functions #####
def get_fps(vfile):
    if not os.path.isdir(vfile):
        cap = cv2.VideoCapture(vfile)
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"File spec FPS ={fps}")
        cap.release()
        return fps
    else:
        return None


def get_frame(vfile):
    if os.path.isdir(vfile):
        images = glob(os.path.join(vfile, '*.jp*'))
        if not images:
            images = glob(os.path.join(vfile, '*.png'))
        assert images, f"No image file (*.jpg or *.png) found in {vfile}"        

        images = sorted(images,
                        key=lambda x: int(x.split('/')[-1].split('.')[0]))
        for img in images:
            frame = cv2.imread(img)
            yield frame

    else:
        cap = cv2.VideoCapture(vfile)
        while True:
            ret, frame = cap.read()
            if ret:
                yield frame
            else:
                cap.release()
                break
                
        
if __name__ == '__main__': 
    args = parser.parse_args()

    vfile = args.infile

    if args.fps is not None:
        fps = args.fps
    else:
        fps = get_fps(vfile) 
        if fps is None:
            fps = 60 

    spf = float(1.0/fps)

    n_frames = 0
    width,height = 0,0
    current = 0.0
    start = time()

    for frame in get_frame(vfile):
        timediff = time() - current

        if timediff < spf: 
            sleep(spf - timediff)

        current = time()
         
        height,width = frame.shape[:2]
        n_frames += 1

        if args.rotate_left:
            frame = cv2.rotate(frame,cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif args.rotate_right:
            frame = cv2.rotate(frame,cv2.ROTATE_90_CLOCKWISE)

        cv2.imshow('frame',frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    #cap.release()
    cv2.destroyAllWindows()

    actual_fps = n_frames / (time() - start)

    if args.info:
        print(f"Number of frames: {n_frames}")
        print(f"Width x height = ({width},{height})")
        print(f"Actual replay speed = {actual_fps:.3f}/s")
