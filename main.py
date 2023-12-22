import config
import utils
import argparse
import yt_dlp
import copy
import json
import sys

# global vars that actually work
class Box:
    pass
this = sys.modules[__name__]
this.globs = Box()


def main():
    parser = argparse.ArgumentParser(prog="yt-manager", description="manages the downloading and tracking of channels and playlists")
    parser.add_argument("--ac", "--add-channel", help="add a channel to scan")
    parser.add_argument("--ap", "--add-playlist", help="add a playlist to scan")
    parser.add_argument("-f", "--no-confirm", action="store_true", help="do not confirm before downloading video")
    args = parser.parse_args()

    print(args)
    this.globs.conf = config.get()
    this.globs.args = args

    if args.ac:
        add_channel(url = args.ac)
        config.save(this.globs.conf)


def add_channel(url):
    opts = {
        "extract_flat": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = [ydl.extract_info(url, download=False)]

        # get channel from video
        if config.Video.is_video(info[0]):
            info[0] = ydl.extract_info(config.Channel.url_from_id(info[0]["channel_id"]), download=False)

        info = ydl.sanitize_info(info[0])
        info = utils.clean_entries(info)
        print(info)

        if not (this.globs.args.no_confirm or utils.ask_confirm(info, type="channel")):
            return

        channel = config.Channel().from_info_dict(info)
        config.add_channel(this.globs, channel)
    print(globs.conf)
