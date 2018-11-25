#!/usr/bin/env python3

import re
import time
import sys
import random
import argparse
from pathlib import Path

import numpy as np
from PIL import Image
import cv2
import imageio


def random_mutate(img_str):
    """
    for not this just randomely mutatest a random bytes
    one could ckeck that no critical byte is overwirtten
    or one could test if jpeg is still valid aver mutation
    """
    mut = random.randint(0, len(img_str)-1)
    new_img_str = bytearray(img_str)
    new_img_str[mut] = random.randint(0, 255)
    return new_img_str


def mutate(n_mutations, img_str):
    for _ in range(n_mutations):
        img_str = random_mutate(img_str)
    return img_str


def display(img_np):
    cv2.imshow('Press Any Key to Exit', img_np)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def save_file(img_np):
    ext = ".png"
    outdir = "output/"
    out = outdir + str(int(time.time())) + ext
    Image.fromarray(img_np).save(out)
    print("saved images as: {}".format(out))


def save_vid(frames, fps):
    ext = ".mp4"
    outdir = "output/"
    out = outdir + str(int(time.time())) + ext
    writer = imageio.get_writer(out, fps=fps)
    for frame in frames:
        if frame is None:
            continue
        writer.append_data(frame)
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
    print("Video mode: fps={}, rounds={}, steps_per_round={}, glitch_per_step={}.".format(
        fps, rounds, steps_per_round, glitch_per_step))

    frames = []
    org_img_str = img_str[:]
    for _ in range(rounds):
        img_str = org_img_str[:]
        for _ in range(steps_per_round):
            np_frombuff = np.frombuffer(img_str, np.uint8)
            frames.append(cv2.imdecode(np_frombuff, cv2.IMREAD_COLOR))
            img_str = mutate(glitch_per_step, img_str)

    save_vid(frames, fps)
    # display_vid()


def validate_cmd_arguments(args):
    vid_limits = {
        "fps": {"mi": 0.5, "ma": 60},
        "rounds": {"mi": 1, "ma": 100},
        "steps_per_round": {"mi": 1, "ma": 100},
        "glitch_per_step": {"mi": 1, "ma": 100}
    }
    img_limits = {
        "nglitch": {"mi": 0, "ma": 100}
    }
    default_source_image = 'input/einstein.jpg'

    # print(args)

    if not args.source:
        args.source = default_source_image

    if args.action == 'vid':
        for value, limits in vid_limits.items():
            #print("validating: ", value, getattr(args, value))
            if not limits["mi"] <= getattr(args, value) <= limits["ma"]:
                print("Bad cmd argument or out of range.")
                print("Try: {} <= {} <= {}".format(
                    limits["mi"], value, limits["ma"]))
                sys.exit()
        return args

    elif args.action == 'img':
        #print("validating nglitch: ", args.nglitch)
        if str(args.nglitch).isdigit():
            args.nglitch = int(args.nglitch)
            mi, ma = img_limits["nglitch"]["mi"], img_limits["nglitch"]["ma"]
            if not mi <= args.nglitch <= ma:
                print("Bad cmd argument or out of range.")
                print("Try: {} <= {} <= {}".format(mi, args.nglitch, ma))
                sys.exit()
            if args.nglitch == 0:
                args.nglitch = random.randint(img_limits["nglitch"]["mi"], img_limits["nglitch"]["ma"])
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
    example = ('examples:\n  ./rjg.py img --nglitch=70\n'
               '  ./rjg.py vid  --fps=8 --steps-per-round=10 \n'
               '  ./rjg.py vid  --rounds=30 --steps-per-step=10')
    parser = argparse.ArgumentParser(epilog=example, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--source', default=False, type=str, help='source image file')

    subparser = parser.add_subparsers(dest='action', required=True)
    img_parser = subparser.add_parser('img', help='create image')
    img_parser.add_argument('--nglitch', default=0, help='count or range of mutations per image. default: random.')
    vid_parser = subparser.add_parser('vid', help='create animationb')
    vid_parser.add_argument("--fps", default=1, type=float, help="frames per second")

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
