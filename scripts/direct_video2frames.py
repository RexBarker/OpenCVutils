# Direct frames to video using FFMPEG executable

import os
import cv2
import argparse
from glob import glob
import numpy as np
import subprocess as sp

def createVideoClip(clip, outputfile, fps, size=[256, 256]):

    vf = clip.shape[0]
    command = ['ffmpeg',
               '-y',  # overwrite output file if it exists
               '-f', 'rawvideo',
               '-s', '%dx%d' % (size[1], size[0]),  # '256x256', # size of one frame
               '-pix_fmt', 'rgb24',
               '-r', '25',  # frames per second
               '-an',  # Tells FFMPEG not to expect any audio
               '-i', '-',  # The input comes from a pipe
               '-vcodec', 'libx264',
               '-b:v', '1500k',
               '-vframes', str(vf),  # 5*25
               '-s', '%dx%d' % (size[1], size[0]),  # '256x256', # size of one frame
               outputfile]
    # sfolder+'/'+name
    pipe = sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE)
    out, err = pipe.communicate(clip.tostring())
    pipe.wait()
    pipe.terminate()
    print(err)

if __name__ == "__main__":

    parser= argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, required=True, default=None,
                        help="input directory of frames (assuming numeric ordering)")
    parser.add_argument('--fps', type=int, default=25, 
            help="frames per second encoding speed (default=25 fps)")

    parser.add_argument('--output_file', type=str, default=None,
                        help="name of output mp4 file (default = input directory name")

    args = parser.parse_args()

    resultfiles = sorted(glob(os.path.join(args.input_dir,"*.png")))
    clip = [ cv2.imread(f)[:, :, ::-1] for f in resultfiles]
    
    h,w = clip[0].shape[:2]
    clippack = np.stack(clip)

    createVideoClip(clippack, args.output_file, args.fps, [h,w])
    print("Done")
