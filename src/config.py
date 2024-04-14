import main
import utils
import channel

import argparse
import yt_dlp
import copy
import json
import sys
import os
import jsonpickle


DEFAULT_ARCHIVE_PATH = "archive.txt"
DEFAULT_CONFIG_PATH  = "config.json"
DEFAULT_COOKIE_PATH  = "cookies.txt"

DEFAULT_CHANNEL_PATH  = "channels"
DEFAULT_PLAYLIST_PATH = "playlists"

def init():
    handle_args()

    # load and set config file to persistent
    global persistent
    persistent = load_persistent(cmd_args.conf)
    utils.printv(str(persistent))


def handle_args():
    parser = argparse.ArgumentParser(prog="yt-manager", description="manages the downloading and tracking of channels and playlists")
    parser.add_argument("--ac", "--add-channel",    help="add a channel to scan")
    parser.add_argument("--ap", "--add-playlist",   help="add a playlist to scan")
    parser.add_argument("--conf",       help="custom path for config",  default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--archive",    help="custom path for archive", default=DEFAULT_ARCHIVE_PATH)
    parser.add_argument("--dv", "--download-video", help="download video")
    parser.add_argument("--c",  "--cookies",        help="cookie file", default=DEFAULT_COOKIE_PATH)

    parser.add_argument("--nc", "--no-confirm", action="store_true", help="do not confirm before downloading video")
    parser.add_argument("--nb", "--no-browser", action="store_true", help="do not open browser to show link")
    parser.add_argument("--nf", "--no-format" , action="store_true", help="do not ask the format to download a video in")
    parser.add_argument("--lc", "--list-channels", action="store_true", help="list all the channels")
    parser.add_argument("--lp", "--list-playlists",action="store_true", help="list all the playlists")
    parser.add_argument("--rf", "--reset-formats", action="store_true", help="reset the formats in config file")
    parser.add_argument("-v", "--verbose", action="store_true", help="extra output for debugging and stuff")
    args = parser.parse_args()

    global cmd_args
    cmd_args = args

    utils.printv("passed in arguments:")
    utils.printv(cmd_args)


DEFAULT_FORMATS = {
    "240": {
         'format': '(bv+(250/251/ba))',
         'format_sort': ['vcodec:vp9', 'acodec', 'res:240'],
         'prefer_free_formats': True,
    },
    "default": {
         'format': '(bv+(250/251/ba))[filesize<?50M][filesize_approx<?100M]',
         'format_sort': ['vcodec:vp9', 'acodec', 'res:480'],
         'prefer_free_formats': True,
    },
    "720": {
         'format': '(bv+(250/251/ba))',
         'format_sort': ['vcodec:vp9', 'acodec', 'res:720'],
         'prefer_free_formats': True,
    },
    "1080": {
         'format': '(bv+(250/251/ba))',
         'format_sort': ['vcodec:vp9', 'acodec', 'res:1080'],
         'prefer_free_formats': True,
    }
}


class ConfigFile:
    def __init__(self):
        self.opts = []
        self.formats = DEFAULT_FORMATS
        self.playlists = []
        self.channels = []

    def __repr__(self):
        a = (
                "{}(\n"
                "options:   {}\n"
                "formats:   {}\n"
                "playlists: {}\n"
                "channels:  {}\n)"
            ).format(self.__class__.__name__, self.opts, jsonpickle.encode(self.formats, indent=2), self.playlists, self.channels)
        return a

    def __str__(self):
        a = (
                "{}(\n"
                "options:   {}\n"
                "formats:   {}\n"
                "playlists: {}\n"
                "channels:  {}\n)"
            ).format(self.__class__.__name__, self.opts, list(self.formats.keys()), self.playlists, self.channels)
        return a
    
    def list_channels(self):
        for i in range(len(self.channels)):
            print(str(i) + "\t" + str(self.channels[i]))

    def list_playlists(self):
        for playlist in self.playlists:
            print(playlist)

    def reset_formats(self):
        self.formats = DEFAULT_FORMATS

    def check_make_channel_nicks(self):
        for channel in self.channels:
            if channel.dir == "":
                channel.dir = channel.nick

    def check_make_dirs(self):
        folders = []
        for root, dirs, files in os.walk("."):
            folders.append(root)
        for channel in self.channels:
            if not channel.dir in folders:
                channel.make_dir()
         
    def do_checks(self):
        self.check_make_channel_nicks()
        self.check_make_dirs()

    def check_format_exists(self, format_name):
        format_name in self.formats


def load_persistent(path = DEFAULT_CONFIG_PATH):
    utils.printv("loading configuration from {}\nfyi the config file is known as persistent in code".format(path))
    if not os.path.exists(path):
        try:
            f = open(path, "x")
            f.close()
            with open(path, "r+") as f:
                f.write(jsonpickle.encode(ConfigFile(), indent=4))
            return ConfigFile()
        except e:
            printe(e)
            printe("could not create configuration file:  {}".format(path), file=sys.stderr)
            sys.exit(1)

    conf = None
    with open(path, "r") as f:
        conf = jsonpickle.decode(f.read())
    return conf
