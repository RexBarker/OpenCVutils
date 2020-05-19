import os
import cv2
import argparse
import warnings
from PIL import Image
from glob import glob
from time import time, sleep

if cv2.__version__ < '4.1.0':
    warnings.warn("cv2 version < 4.1.0, script not tested for earlier versions",
                  UserWarning)

fontconfig = {
    "font"         : cv2.FONT_HERSHEY_SIMPLEX,
    "rel_coords"   : (0.8, 0.05),
    "cornercoords" : (10,500),
    "minY"         : 30,
    "fontScale"    : 1, 
    "fontColor"    : (0,255,0),
    "lineType"     : 2
}

parser = argparse.ArgumentParser()

parser.add_argument('--infile', type=str, required=None, 
                    help="input file in .mp4, .avi, .mov, or .mkv format")

parser.add_argument('--maskdir', type=str, required=None, 
                    help="mask directory (*.jpg or *.png), total must be same as frame count")

parser.add_argument('--fps', type=int, default=None, 
                    help="video replay frame rate, frames per second (default=60 fps)")

parser.add_argument('--rotate_right', action='store_true', 
                    help="Rotate image by 90 deg clockwise")

parser.add_argument('--rotate_left', action='store_true', 
                    help="Rotate image by 90 deg anticlockwise")

parser.add_argument('--frame_num', action='store_true', 
                    help="display frame number")

parser.add_argument('--start', type=int, default= 0, help="start from frame#")

parser.add_argument('--finish', type=int, default= None, help="finish at frame#")

parser.add_argument('--outvideo', type=str, default = None, 
                    help="Output selected sequence to video (.mp4, .avi, .mov)")
                    
parser.add_argument('--outgif', type=str, default = None, 
                    help="Output selected sequence to gif (.gif)")

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


def get_nframes(vfile):
    if not os.path.isdir(vfile):
        cap = cv2.VideoCapture(vfile)
        n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"File spec n_frames ={n_frames}")
        cap.release()
    else:
        images = glob(os.path.join(vfile, '*.jp*'))
        if not images:
            images = glob(os.path.join(vfile, '*.png')) 
        assert images, f"No image file (*.jpg or *.png) found in {vfile}"        
        n_frames = len(images)

    return n_frames 


def get_WidthHeight(vfile):
    if not os.path.isdir(vfile):
        cap = cv2.VideoCapture(vfile)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
    else:
        images = glob(os.path.join(vfile, '*.jp*'))
        if not images:
            images = glob(os.path.join(vfile, '*.png')) 
        assert images, f"No image file (*.jpg or *.png) found in {vfile}"        
        img = cv2.imread(images[0])
        height,width = img.shape[:2]

    return (width, height) 


def get_frame(vfile, n_frames, startframe=0, finishframe=None):
    if os.path.isdir(vfile):
        images = glob(os.path.join(vfile, '*.jp*'))
        if not images:
            images = glob(os.path.join(vfile, '*.png'))
        assert images, f"No image file (*.jpg or *.png) found in {vfile}"        

        assert len(images) == n_frames, \
            f"Mismatch in number of mask files versus number of frames\n" + \
            f"n_frames={n_frames}, n_masks={len(images)}"

        images = sorted(images,
                        key=lambda x: int(x.split('/')[-1].split('.')[0]))

        if finishframe is None:
            finishframe = n_frames        

        images = images[startframe:finishframe]

        for img in images:
            frame = cv2.imread(img)
            yield frame

    else:
        cap = cv2.VideoCapture(vfile)

        # start frame is indexed
        # stop frame is set by controlling loop (caller)
        if startframe != 0:
            cap.set(cv2.CAP_PROP_POS_FRAMES, startframe)
        
        while True:
            ret, frame = cap.read()
            
            if ret:
                yield frame
            else:
                cap.release()
                break

def get_mask(maskdir,n_frames, startframe=0, finishframe=None):
    assert os.path.isdir(maskdir), \
        "Use masks specified, however supplied path was not a directory:\n{maskdir}"
    
    images = glob(os.path.join(maskdir, '*.jp*'))
    if not images:
        images = glob(os.path.join(maskdir, '*.png'))
    assert images, f"No mask files (*.jpg or *.png) found in {maskdir}"        
    assert len(images) == n_frames, \
        f"Mismatch in number of mask files versus number of frames\n" + \
        f"n_frames={n_frames}, n_masks={len(images)}"

    images = sorted(images,
                    key=lambda x: int(x.split('/')[-1].split('.')[0]))
    
    if finishframe is None:
        finishframe = n_frames
    
    images = images[startframe:finishframe]

    for img in images:
        mask = cv2.imread(img)
        yield mask 
        

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

    n_frames = get_nframes(vfile) 
    width,height = get_WidthHeight(vfile) 
    current = 0.0

    startframe = 0
    if args.start:
        assert abs(args.start) < n_frames, \
            f"Invalid 'start'={startframe} frame specified, exceeds number of frames ({n_frames})"

        startframe = args.start if args.start >= 0 else n_frames + args.start  # negative indicates from end
    
    finishframe = n_frames
    if args.finish is not None:
        assert abs(args.finish) < n_frames, \
            f"Invalid 'finish'={finishframe} frame specified, exceeds number of frames({n_frames})"

        finishframe = args.finish if args.finish >= 0 else n_frames + args.finish  # negative indicates from end 
    
    assert finishframe > startframe, f"Invalid definition of 'start'={startframe} and 'finish'={finishframe}, start > finish"

    replay = 1 

    # Write out edited video file?
    outvid = None
    if args.outvideo:
        outvideofile = args.outvideo
        
        if outvideofile.endswith(".mp4"):
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        elif outvideofile.endswith(".avi"):
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
        else:
            assert False, f"Could not determine the video output type from {outvideofile}"
        
        outvid = cv2.VideoWriter(outvideofile, fourcc, fps, (width,height) )

    # Write out edited GIF file?
    outgif = None
    outimgs = []
    if args.outgif:
        outgif = args.outgif

    while replay:
        start = time()
    
        frame_gen = get_frame(vfile, n_frames, startframe, finishframe)
        mask_gen = get_mask(args.maskdir,n_frames, startframe, finishframe) if args.maskdir else None
 
        i_frames = 0
        for i in range(startframe,finishframe): 
            frame = next(frame_gen)
            mask = next(mask_gen) if mask_gen else None 

            timediff = time() - current

            if timediff < spf: 
                sleep(spf - timediff)

            current = time()
         
            ### optional add mask
            # modify existing frame to include mask
            if mask is not None:
                if len(mask.shape) == 3:
                    mask = mask[:,:,0]
                frame[:, :, 2] = (mask > 0) * 255 + (mask == 0) * frame[:, :, 2]

            ### optional rotations
            if args.rotate_left:
                frame = cv2.rotate(frame,cv2.ROTATE_90_COUNTERCLOCKWISE)
            elif args.rotate_right:
                frame = cv2.rotate(frame,cv2.ROTATE_90_CLOCKWISE)

            ### add frame number to image
            if args.frame_num:
                real_x = round(fontconfig["rel_coords"][0] * width)
                real_y = max(round(fontconfig["rel_coords"][1] * height), fontconfig['minY'])
                cv2.putText(frame, str(i), 
                            (real_x, real_y),
                            fontconfig['font'],
                            fontconfig['fontScale'],
                            fontconfig['fontColor'],
                            fontconfig['lineType'] )

            ### optional: write video of frames
            if outvid is not None:
                outvid.write(frame)

            ### optional: write frames to gif
            if outgif is not None:
                outimgs.append(frame) 

            ### show image
            cv2.imshow('frame',frame)

            ### look for a way out
            keycode = cv2.waitKey(10)
            if keycode & 0xFF == ord('p'):  # pause
                while True:
                    keycode = cv2.waitKey(0)
                    if keycode & 0xFF == ord('p'): 
                        break

            if keycode & 0xFF == ord('q'):  # quit (immediately)
                if outvid is not None or outgif is not None:
                    print("Cannot stop now..writing video. Try on next loop")
                else:
                    replay = 0
                    break
            elif keycode & 0xFF == ord('e'):  # end (eventually)
                replay = 0
            elif keycode & 0xFF == ord('r'):  # restart
                if outvid is not None or outgif is not None:
                    print("Cannot rewind now..writing video. Try on next loop")
                else:
                    replay = 1
                    break

            i_frames += 1

        # close video output if open
        if outvid is not None:
            outvid.release()
            print(f"Successfully wrote {i_frames} frames to videofile file as={args.outvideo}") 
            outvid = None
        
        # write gif if requested
        if outgif is not None:
            duration = round(spf * 1000)
            imgs = [Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)) for img in outimgs]
            with Image.new(mode=imgs[0].mode,size=imgs[0].size) as img:
                img.save(outgif, format='GIF',
                         append_images=imgs, 
                         save_all=True, duration= duration, loop=0)

            print(f"Successfully wrote {i_frames} frames to .gif file as={args.outgif}") 
            outimgs = []
            outgif = None

        # End While loop

    cv2.destroyAllWindows()

    actual_fps = i_frames / (time() - start)

    if args.info:
        print(f"Number of frames: {n_frames}")
        print(f"Width x height = ({width},{height})")
        print(f"Actual replay speed = {actual_fps:.3f}/s")
