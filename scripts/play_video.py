import os
import cv2
import argparse
from glob import glob
from time import time, sleep

fontconfig = {
    "font"         : cv2.FONT_HERSHEY_SIMPLEX,
    "rel_coords"   : (0.8, 0.05),
    "cornercoords" : (10,500),
    "fontScale"    : 1, 
    "fontColor"    : (0,255,0),
    "lineType"     : 2
}

parser = argparse.ArgumentParser()

parser.add_argument('--infile', type=str, required=None, 
                    help="input file in .mp4, .avi, .mov, or .mkv format")

parser.add_argument('--fps', type=int, default=None, 
                    help="video replay frame rate, frames per second (default=60 fps)")

parser.add_argument('--rotate_right', action='store_true', 
                    help="Rotate image by 90 deg clockwise")

parser.add_argument('--rotate_left', action='store_true', 
                    help="Rotate image by 90 deg anticlockwise")

parser.add_argument('--frame_num', action='store_true', 
                    help="display frame number")

parser.add_argument('--info', action='store_true', 
                    help="output video information")

parser.add_argument('other', nargs=argparse.REMAINDER) # catch unnamed arguments


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

    if args.infile:
        vfile = args.infile 
    elif args.other:
        vfile = args.other[0]
    else:
        assert False,"No input file was specified"

    assert os.path.exists(vfile), f"Input file was not found: {vfile}"

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
    for i,frame in enumerate(get_frame(vfile)):
        timediff = time() - current

        if timediff < spf: 
            sleep(spf - timediff)

        current = time()
         
        height,width = frame.shape[:2]

        real_x = round(fontconfig["rel_coords"][0] * width)
        real_y = round(fontconfig["rel_coords"][1] * height)

        n_frames += 1

        ### optional rotations
        if args.rotate_left:
            frame = cv2.rotate(frame,cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif args.rotate_right:
            frame = cv2.rotate(frame,cv2.ROTATE_90_CLOCKWISE)

        ### add frame number to image
        if args.frame_num:
            cv2.putText(frame, str(i), 
                        (real_x, real_y),
                        fontconfig['font'],
                        fontconfig['fontScale'],
                        fontconfig['fontColor'],
                        fontconfig['lineType'] )

        ### show image
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
