import config
import utils

import argparse
import yt_dlp
import copy
import json
import sys
import jsonpickle

def init():
    handle_args()


def handle_args():
    parser = argparse.ArgumentParser(prog="yt-manager", description="manages the downloading and tracking of channels and playlists")
    parser.add_argument("--ac", "--add-channel",    help="add a channel to scan")
    parser.add_argument("--ap", "--add-playlist",   help="add a playlist to scan")
    parser.add_argument("--conf",       help="custom path for config",  default="config.json")
    parser.add_argument("--archive",    help="custom path for archive", default="archive.txt")
    parser.add_argument("--dv", "--download-video", help="download video")
    parser.add_argument("--c",  "--cookies", help="cookie file", default="cookies.txt")

    parser.add_argument("--nc", "--no-confirm", action="store_true", help="do not confirm before downloading video")
    parser.add_argument("--nb", "--no-browser", action="store_true", help="do not open browser to show link")
    parser.add_argument("--nf", "--no-format" , action="store_true", help="do not ask the format to download a video in")
    parser.add_argument("--lc", "--list-channels", action="store_true", help="list all the channels")
    parser.add_argument("--lp", "--list-playlists",action="store_true", help="list all the playlists")
    parser.add_argument("--rf", "--reset-formats", action="store_true", help="reset the formats in config file")
    args = parser.parse_args()
    global cmd_args
    cmd_args = args
