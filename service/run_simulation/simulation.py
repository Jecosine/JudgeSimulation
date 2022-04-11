import os
import argparse

parser = None


def init_argparse():
    global parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/", help="dir to store data files")
    return parser.parse_args()
