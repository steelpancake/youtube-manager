import config
import utils
import argparse
import yt_dlp
import copy
import json
import sys
import jsonpickle
import webbrowser

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
    parser.add_argument("--nc", "--no-confirm", action="store_true", help="do not confirm before downloading video")
    parser.add_argument("--nb", "--no-browser", action="store_true", help="do not open browser to show link")
    parser.add_argument("--nf", "--no-format" , action="store_true", help="do not ask the format to download a video in")
    parser.add_argument("--lc", "--list-channels", action="store_true", help="list all the channels")
    parser.add_argument("--lp", "--list-playlists",action="store_true", help="list all the playlists")
    parser.add_argument("--rf", "--reset-formats", action="store_true", help="reset the formats in config file")
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
    elif args.lc:
        this.globs.conf.list_channels()
    elif args.lp:
        this.globs.conf.list_playlists()
    elif args.rf:
        this.globs.conf.reset_formats()
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
        
        channel = config.Channel().from_info_dict(info)

        if config.Channel().find_in_list(channel.url) != None:
            utils.log_warn("channel already in list")
            return

        if not (this.globs.args.nc or utils.ask_confirm(info, type="channel")):
            return

        channel.ask_nickname()
        channel.make_dir()

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
        crawl_playlist_url(url, channel)


def crawl_playlist_url(playlist, in_channel: config.Channel = None):
    selected_videos = []
    info_opts = {
        "extract_flat": True,
        "download_archive": this.globs.args.archive,
        'outtmpl': {'default': '%(upload_date)s %(title)s - %(id)s.%(ext)s'},
        "sleep_interval": 0.3,
        "sleep_interval_requests": 0.3
    }
    ydl = yt_dlp.YoutubeDL(info_opts)
    try:
        info = ydl.extract_info(playlist, download=False, process=True)
    except:
        return

    ignore_all  = [False]
    skip_all    = [False]
    for entry in info["entries"]:
        if ignore_all[0]:
            ydl.record_download_archive(entry)
            continue

        if skip_all[0]:
            break

        channel = [in_channel]
        if not channel[0]:
            channel[0] = globs.conf.channels[config.Channel.find_in_list(entry["channel_url"])]
        entry["manager_channel"] = channel[0]

        if this.globs.args.nc:
            entry["manager_selected_format"] = channel[0].preferred_format
            selected_videos.append(entry)
            continue

        while True:
            response = utils.ask_confirm(entry, type="video entry")
            if response == "no":
                break
            elif response == "yes":
                entry["manager_selected_format"] = get_user_format(entry["manager_channel"])
                selected_videos.append(entry)
                break
            elif response == "ignore all":
                ydl.record_download_archive(entry)
                ignore_all[0] = True
                break
            elif response == "ignore":
                ydl.record_download_archive(entry)
                break
            elif response == "skip":
                skip_all[0] = True
                break
            print("invalid response")

    for entry in selected_videos:
        channel = entry["manager_channel"]
        
        dl_opts = {
            "extract_flat": True,
            "download_archive": this.globs.args.archive,
            'outtmpl': {'default': "{}/".format(channel.dir) + '%(upload_date)s %(title)s - %(id)s.%(ext)s'},
            "sleep_interval": 0.1,
            "sleep_interval_requests": 0.1,
            'concurrent_fragment_downloads': 25,
            'writeinfojson': True
        }
        tmp_opts = this.globs.conf.formats[entry["manager_selected_format"]]
        print(jsonpickle.encode(tmp_opts, indent=4))
        dl_opts.update(tmp_opts)
        print(jsonpickle.encode(dl_opts, indent=4))

        ydl_dl = yt_dlp.YoutubeDL(dl_opts)
        try:
            output = ydl_dl.download(entry["url"])
        except yt_dlp.utils.DownloadError as e:
            utils.log_error(e)


def get_user_format(channel=None):
    format = []
    while True:
        print("available formats:")
        for k, v in this.globs.conf.formats.items():
            print(k + "\t" + jsonpickle.encode(v, indent=4))

        req = input("which format?(leave blank for channel default) ")
        if not req in this.globs.conf.formats.keys() and req != "":
            print('selected format "{}" not in keys'.format(req))
            continue
        elif req == "":
            if not channel:
                raise "this function cannot find default format if a channel isnt given"
            format.append(channel.preferred_format)
            break
        format.append(req)
        break
    return format[0]

