import config
import utils
import argparse
import yt_dlp
import copy
import json
import sys
import jsonpickle

# global vars that actually work
class Box:
    pass
this = sys.modules[__name__]
this.globs = Box()


def handle_args():
    parser = argparse.ArgumentParser(prog="yt-manager", description="manages the downloading and tracking of channels and playlists")
    parser.add_argument("--ac", "--add-channel",    help="add a channel to scan")
    parser.add_argument("--ap", "--add-playlist",   help="add a playlist to scan")
    parser.add_argument("--conf",       help="custom path for config",  default="config.json")
    parser.add_argument("--archive",    help="custom path for archive", default="archive.txt")
    parser.add_argument("-f", "--no-confirm", action="store_true", help="do not confirm before downloading video")
    args = parser.parse_args()

    this.globs.args = args
    print(args)


def main():
    handle_args()
    config.check_make_archive(this.globs.args.archive)
    this.globs.conf = config.get()

    args = this.globs.args

    if args.ac:
        add_channel(url = args.ac)
        config.save(this.globs.conf)
    else:
        crawl()


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
        config.add_channel(this.globs.conf, channel)


def crawl():
    crawl_channels()


def crawl_channels():
    opts = {
        "extract_flat": True,
        "download_archive": "archive.txt"
    }
    for channel in this.globs.conf.channels:
        url = config.Channel.playlist_url_from_id(channel.info_dict["channel_id"])
        crawl_playlist_url(url)


def crawl_playlist_url(playlist):
    selected_videos = []
    info_opts = {
        "extract_flat": True,
        "download_archive": this.globs.args.archive,
        'outtmpl': {'default': '%(upload_date)s %(title)s - %(id)s.%(ext)s'},
        "sleep_interval": 0.3,
        "sleep_interval_requests": 0.3
    }
    ydl = yt_dlp.YoutubeDL(info_opts)
    info = ydl.extract_info(playlist, download=False, process=True)
    for entry in info["entries"]:
        if this.globs.args.no_confirm:
            selected_videos.append(entry)
            continue
        response = utils.ask_confirm(entry, type="video entry")
        if response == "no":
            continue
        elif response == "yes":
            selected_videos.append(entry)
            continue
        elif response == "ignore":
            ydl.record_download_archive(entry)
            continue


    for entry in selected_videos:
        channel = globs.conf.channels[config.Channel.find_in_list(entry["channel_url"])]
        dir = channel.dir
        
        dl_opts = {
            "extract_flat": True,
            "download_archive": this.globs.args.archive,
            'outtmpl': {'default': "{}/".format(dir) + '%(upload_date)s %(title)s - %(id)s.%(ext)s'},
            "sleep_interval": 0.1,
            "sleep_interval_requests": 0.1,
            'concurrent_fragment_downloads': 25
        }
        dl_opts = channel.opts_with_preferred_format(dl_opts)
        print(jsonpickle.encode(dl_opts, indent=4))

        ydl_dl = yt_dlp.YoutubeDL(dl_opts)
        output = ydl_dl.download(entry["url"])

