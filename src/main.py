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
    parser.add_argument("--dv", "--download-video", help="download video")
    parser.add_argument("--c",  "--cookies", help="cookie file", default="cookies.txt")

    parser.add_argument("--nc", "--no-confirm", action="store_true", help="do not confirm before downloading video")
    parser.add_argument("--nb", "--no-browser", action="store_true", help="do not open browser to show link")
    parser.add_argument("--nf", "--no-format" , action="store_true", help="do not ask the format to download a video in")
    parser.add_argument("--nl", "--no-log"    , action="store_true", help="prevent LOG:")
    parser.add_argument("--lc", "--list-channels", action="store_true", help="list all the channels")
    parser.add_argument("--lp", "--list-playlists",action="store_true", help="list all the playlists")
    parser.add_argument("--rf", "--reset-formats", action="store_true", help="reset the formats in config file")


    parser.add_argument("--cc", "--crawl-channel", help="download video")
    parser.add_argument("--cp", "--crawl-playlist", help="download video")

    args = parser.parse_args()
    this.globs.args = args
    utils.args = args
    print(args)


def main():
    handle_args()
    config.check_make_archive(this.globs.args.archive)
    this.globs.conf = config.get(path = this.globs.args.conf)

    args = this.globs.args
    this.globs.conf.do_checks()

    if args.nl:
        utils.verbose=False

    if args.ac:
        add_channel(url = args.ac)
    elif args.ap:
        add_playlist(url = args.ap)
    elif args.dv:
        download_video(url = args.dv)
    elif args.lc:
        utils.verbose=False
        this.globs.conf.list_channels()
    elif args.lp:
        utils.verbose=False
        this.globs.conf.list_playlists()
    elif args.rf:
        utils.verbose=False
        this.globs.conf.reset_formats()
    elif args.cp:
        crawl_playlist(args.cp)
    else:
        crawl()
    config.save(this.globs.conf, path = this.globs.args.conf)

    utils.log(str(this.globs.conf))


def fetch_info(url):
    opts = {
        "extract_flat": True,
        "cookiefile": this.globs.args.c,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=False, process=True)


def add_channel(url):
    utils.log("add_channel run with url: "+url)
    opts = {
        "extract_flat": True,
    }
    info = [fetch_info(url)]
    with yt_dlp.YoutubeDL(opts) as ydl:
        # get channel from video
        if config.Video.is_video(info[0]):
            utils.log("url was video id: "+info[0]['id']+" and channel_id: "+info[0]['channel_id'])
            info[0] = fetch_info(config.Channel.url_from_id(info[0]["channel_id"]))

        info = ydl.sanitize_info(info[0])
        print(info)

        channel = config.Channel.find_in_list(url=info["webpage_url"])
        if channel:
            utils.log_error("channel already in list")
            os.exit()
            return channel
        
        channel = config.Channel().from_info_dict(info)

        if this.globs.args.nc or not utils.ask_confirm(info):
            # name will show up as "Name - Videos" but the " - Videos" will not be present
            return

        channel.ask_nickname()
        channel.make_dir()

        config.add_channel(this.globs.conf, channel)
        print(channel)
        return channel


def add_playlist(url):
    opts = {
        "extract_flat": True,
    }
    info = fetch_info(url)
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.sanitize_info(info)
        print(info)
        if not config.Playlist.is_playlist(info):
            utils.log_error("the playlist url you gave is not a playlist url")
            os.exit()

        playlist = config.Playlist.find_in_list(url=info["webpage_url"])
        if playlist:
            utils.log_error("playlist already in list")
            os.exit()
            return playlist
        
        playlist = config.Playlist().from_info_dict(info)

        if this.globs.args.nc or not utils.ask_confirm(info):
            return

        playlist.ask_nickname()
        playlist.make_dir()

        config.add_playlist(this.globs.conf, playlist)
        print(playlist)
        return playlist


def download_video(url):
    channel = [0]
    while True:
        channel[0] = add_channel(url)
        if channel[0]:
            break
    channel = channel[0]

    info = fetch_info(url)
    info["manager_channel"] = channel

    if this.globs.args.nc:
        info["manager_selected_format"] = channel.preferred_format
        selected_videos.append(entry)

    selected = [False]
    while True:
        response = utils.ask_confirm(info)
        if response == "no":
            break
        elif response == "yes":
            info["manager_selected_format"] = get_user_format(info["manager_channel"])
            selected[0] = True
            break
        elif response == "ignore all":
            ydl.record_download_archive(info)
            ignore_all[0] = True
            break
        elif response == "ignore":
            ydl.record_download_archive(info)
            break
        print("invalid response")

    if selected[0]:
        channel = info["manager_channel"]
        
        dl_opts = {
            "extract_flat": True,
            "download_archive": this.globs.args.archive,
            'outtmpl': {'default': "{}/".format(channel.dir) + '%(upload_date)s %(title)s - %(id)s.%(ext)s'},
            "sleep_interval": 0.1,
            "sleep_interval_requests": 0.1,
            'concurrent_fragment_downloads': 25,
            'writeinfojson': True,
            'cookiefile': this.globs.args.c,
        }
        tmp_opts = this.globs.conf.formats[info["manager_selected_format"]]
        print(jsonpickle.encode(tmp_opts, indent=4))
        dl_opts.update(tmp_opts)
        print(jsonpickle.encode(dl_opts, indent=4))

        ydl_dl = yt_dlp.YoutubeDL(dl_opts)
        try:
            output = ydl_dl.download(url)
        except yt_dlp.utils.DownloadError as e:
            utils.log_error(e)


def crawl_playlist(index):
    utils.log("crawling playlist number "+index)
    # input may be provided as string
    index = int(index)
    playlist = this.globs.conf.playlists[index]
    crawl_playlist_url(playlist.url)


def crawl():
    crawl_channels()
    crawl_playlists()


def crawl_channels():
    opts = {
        "extract_flat": True,
        "download_archive": this.globs.args.archive
    }
    for channel in this.globs.conf.channels:
        if channel.ignore == False:
            url = config.Channel.playlist_url_from_id(channel.info_dict["channel_id"])
            crawl_playlist_url(url, channel)


def crawl_playlists():
    pass


def crawl_playlist_url(playlist, in_channel: config.Channel = None):
    # TODO: extract playlist twice, once with and once without archive, to symlink videos
    #       or you could manually check by extracting once without and then using ydl builtins
    selected_videos = []
    outtmpl =  '%(upload_date)s %(title)s - %(id)s.%(ext)s'
    info_opts = {
        "extract_flat": True,
        "download_archive": this.globs.args.archive,
        "cookiefile": this.globs.args.c,
        'outtmpl': {'default': outtmpl},
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
        entry = fetch_info(entry["url"])
        entry["manager_output"] = ydl.evaluate_outtmpl(outtmpl, entry)
        utils.log(entry)
        if ignore_all[0]:
            ydl.record_download_archive(entry)
            continue

        if skip_all[0]:
            break

        channel = [in_channel]
        if not channel[0]:
            try:
                channel[0] = globs.conf.channels[config.Channel.find_in_list(entry["channel_url"])]
            except TypeError:
                utils.log("channel is not added yet for " + entry["id"])
                add_channel(entry["webpage_url"])
        entry["manager_channel"] = channel[0]

        if this.globs.args.nc:
            entry["manager_selected_format"] = channel[0].preferred_format
            selected_videos.append(entry)
            continue

        while True:
            response = utils.ask_confirm(entry)
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
            'outtmpl': {'default': "{}/".format(channel.dir) + outtmpl},
            "sleep_interval": 0.1,
            "sleep_interval_requests": 0.1,
            'concurrent_fragment_downloads': 25,
            'writeinfojson': True,
            'cookiefile': this.globs.args.c,
        }
        tmp_opts = this.globs.conf.formats[entry["manager_selected_format"]]
        print(jsonpickle.encode(tmp_opts, indent=4))
        dl_opts.update(tmp_opts)
        print(jsonpickle.encode(dl_opts, indent=4))

        ydl_dl = yt_dlp.YoutubeDL(dl_opts)
        try:
            output = ydl_dl.download(entry["webpage_url"])
        except yt_dlp.utils.DownloadError as e:
            utils.log_error(e)

        if in_channel != None:
            pass


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
                raise "this function cannot find default format if a channel isnt given. notify the developer or try fixing it urself smh"
            format.append(channel.preferred_format)
            break
        format.append(req)
        break
    return format[0]

