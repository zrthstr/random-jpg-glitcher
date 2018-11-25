#!/usr/bin/env python3

import re
import cv2
import time
import sys
import numpy as np
import random
import imageio
import argparse
from PIL import Image
from pathlib import Path

def random_mutate(img_str):
    """
    for not this just randomely mutatest a random bytes
    one could ckeck that no critical byte is overwirtten
    or one could test if jpeg is still valid aver mutation
    """
    mut = random.randint(0, len(img_str)-1)
    new_img_str = bytearray(img_str)
    new_img_str[mut] = random.randint(0,255)
    return new_img_str

def mutate(n_mutations, img_str):
    for e in range(n_mutations):
        img_str = random_mutate(img_str)
    return img_str

def display(img_np):
    cv2.imshow('Press Any Key to Exit',img_np)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def save_file(img_np):
    ext = ".png"
    outdir = "output/"
    out = outdir + str(int(time.time())) + ext
    im = Image.fromarray(img_np)
    im.save(out)
    print("saved images as: {}".format(out))

def save_vid(frames, fps ):
    ext = ".mp4"
    outdir = "output/"
    out = outdir + str(int(time.time())) + ext
    writer = imageio.get_writer(out, fps=2)
    for im in frames:
        #print(type(im))
        if im is None:
            continue
        writer.append_data(im)
    writer.close()
    print("saved video as: {}".format(out))

def get_source(source):
    if not Path(source).is_file():
        print("Source file not found.")
        sys.exit()
    print("Using source: {}".format(source))
    with open(source, 'rb') as fd:
        return fd.read()

def img_mutate(img_str, n_mutations):
    #n_mutations = parse_mutation_count(mutations)
    print("Mutating image. Mutations: {}".format(n_mutations))
    img_str = mutate(n_mutations, img_str)
    nparr = np.frombuffer(img_str, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    save_file(img_np)
    display(img_np)


def vid_mutate(img_str, fps, rounds, steps_per_round, glitch_per_step):
    print("Video mode: fps={}, rounds={}, steps_per_round={}, glitch_per_step={}.".format(fps, rounds, steps_per_round, glitch_per_step))

    frames = []
    org_img_str = img_str[:]
    for seq in range(rounds):
        img_str = org_img_str[:]
        for step in range(steps_per_round):
            frames.append(cv2.imdecode(np.frombuffer(mutate(glitch_per_step, img_str), np.uint8), cv2.IMREAD_COLOR))
    #print(frames)
    save_vid(frames, fps)
    #display_vid()

def parse_mutation_count_2(mut):
    """ n can be: 0, > 1, x-z"""
    mini = 3
    maxi = 70
    total_maxi = 10000

    if not mut:
        return random.randint(mini, maxi)
    if str(mut).isdigit():
        mut = int(mut)
        if 0 < mut < total_maxi:
            return mut
        print("mutations must be > 0 > {}".format(total_maxi))
        sys.exit()
    if isinstance(mut, str):
        print("IS ISNT")
        # this should allow any positive int, '-', then any positive int
        if re.match(r'^[1-9]\d*-[1-9]\d*$', mut):
            mini, maxi = mut.split('-')
            mini, maxi = int(mini), int(maxi)
            if 0 < mini < maxi < total_maxi:
                return random.randint(mini, maxi)
    print("bad paramter: mutattions")
    print("options: unset, 0 < mutation < {}, min-max".format(total_maxi))
    sys.exit()


def validate_cmd_arguments(args):
    vid_limits = {
        "fps": {"mi": 0.5 , "ma": 60},
        "rounds": {"mi": 1,  "ma": 100},
        "steps_per_round": {"mi": 1,  "ma": 100},
        "glitch_per_step": {"mi": 1,  "ma": 100}
    }
    img_limits = {
        "nglitch": {"mi": 0,  "ma": 100}
    }
    default_source_image = 'input/einstein.jpg'

    print(args)

    if not args.source:
        args.source = default_source_image

    if args.action == 'vid':
        for value, limits in vid_limits.items():
            print("validating: ", value, getattr(args, value))
            if not limits["mi"] <= getattr(args, value) <= limits["ma"]:
                print("Bad cmd argument or out of range.")
                print("Try: {} <= {} <= {}".format(limits["mi"] ,value , limits["ma"]))
                sys.exit()
            print("ok")
        return args


    elif args.action == 'img':
        print("validating nglitch: ", args.nglitch)
        if str(args.nglitch).isdigit():
            args.nglitch = int(args.nglitch)
            mi, ma = img_limits["nglitch"]["mi"], img_limits["nglitch"]["ma"]
            if not mi <= args.nglitch <= ma:
                print("Bad cmd argument or out of range.")
                print("Try: {} <= {} <= {}".format(mi, args.nglitch, ma))
                sys.exit()
            return args
        else:
            # this should allow stings consiting of positive int, '-', then any positive int
            if isinstance(mut, str):
                if re.match(r'^[1-9]\d*-[1-9]\d*$', mut):
                    mini, maxi = mut.split('-')
                    mini, maxi = int(mini), int(maxi)
                    if 0 < mini < maxi < total_maxi:
                        args.nglitch = random.randint(mini, maxi)
                        return args

        print("Bad cmd argument or out of range.")
        print("Try: {} <= {} <= {}".format(mi, "--nglitch", ma))
        print("OR: range as in n-m where 0 < n < m < 100 example: 12-42")
        sys.exit()
            
    

def parse_cmd_arguments():
    example=('examples:\n  ./rjg.py img\n'
                '  OLD ./rjg.py vid --mspf=133\n'
                '  OLD ./rjg.py vid --mode prog --mut-pf=1000 \n'
                '  OLD ./rjg.py vid --mode seq --seq-rounds=10')
    parser = argparse.ArgumentParser(epilog=example, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--source', default=False, type=str, help='source image file')

    subparser = parser.add_subparsers(dest='action', required=True)
    img_parser = subparser.add_parser('img', help='create image')
    img_parser.add_argument('--nglitch', default=0, help='count or range of mutations per image. default: random.')
    ## todo process this..

    vid_parser = subparser.add_parser('vid', help='create animationb')
    vid_parser.add_argument("--fps", default=1, type=float,  help="ms per frame. 0.5-30")
    ## todo envorce this..

    vid_parser.add_argument('--rounds', default=1, type=int, help='rounds of seperate mutations')
    vid_parser.add_argument('--steps-per-round', default=10, type=int, help='mutation steps per round')
    vid_parser.add_argument('--glitch-per-step', default=1, type=int, help='number of mutations per step')

    args = parser.parse_args()
    validate_cmd_arguments(args)
    return args 



if __name__ == '__main__':
    args = parse_cmd_arguments()
    img_str = get_source(args.source)

    if args.action == 'img':
        img_mutate(img_str, args.nglitch)
    elif args.action == 'vid':
        vid_mutate(img_str, args.fps, args.rounds, args.steps_per_round, args.glitch_per_step)


