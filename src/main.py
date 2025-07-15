import config
import utils
import argparse
import yt_dlp
import copy
import json
import sys
import jsonpickle
import webbrowser
import re
import os
import error
from glob import glob, iglob
from pathlib import Path

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
    parser.add_argument("--ncc","--no-confirm-channel", action="store_true", help="do not confirm before adding channel")
    parser.add_argument("--nb", "--no-browser", action="store_true", help="do not open browser to show link")
    parser.add_argument("--nf", "--no-format" , action="store_true", help="do not ask the format to download a video in")
    parser.add_argument("--nl", "--no-log"    , action="store_true", help="prevent LOG:")
    parser.add_argument("--lc", "--list-channels", action="store_true", help="list all the channels")
    parser.add_argument("--lp", "--list-playlists",action="store_true", help="list all the playlists")
    parser.add_argument("--rf", "--reset-formats", action="store_true", help="reset the formats in config file")


    parser.add_argument("--cc", "--crawl-channel",  help="download video")
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
    elif args.cc:
        crawl_channel(args.cc)
    else:
        crawl()
    config.save(this.globs.conf, path = this.globs.args.conf)

    utils.log(str(this.globs.conf))


def fetch_info(url, process=True):
    opts = {
        "extract_flat": True,
        "cookiefile": this.globs.args.c,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=False, process=process)


def get_channel(entry):
    channel_url = config.Channel.channel_url_from_id(entry["channel_id"])
    try:
        return globs.conf.channels[config.Channel.find_in_list(channel_url)]
    except TypeError:
        utils.log("channel is not added yet for " + entry["id"])
        return add_channel(channel_url)


def add_channel(url):
    # TODO: add option to ignore channel while adding it
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

        if this.globs.args.ncc:
            channel.auto_nickname()
        else:
            response = utils.ask_confirm(info, intype="channel")
            match response:
                case "add channel":
                    channel.ask_nickname()
                case "add and ignore channel":
                    channel.ask_nickname()
                    channel.ignore = True
        channel.make_dir()

        config.add_channel(this.globs.conf, channel)
        print(channel)
        config.save(this.globs.conf, path = this.globs.args.conf)
        return channel


def entry_in_archive(entry, archive = None, negate: bool = False):
    """
    checks a single entry to see if it's in the archive
    """
    def check_archive():
        if archive == None:
            return this.globs.args.archive
        else:
            return archive
    archive = check_archive()
    info_opts = {
        "download_archive": archive
    }

    ydl = yt_dlp.YoutubeDL(info_opts)

    def myfilter(i):
        if negate:
            return not ydl.in_download_archive(i)
        else:
            return ydl.in_download_archive(i)
    output: bool = myfilter(entry)

    if negate:
        pass
    elif output:
        string = "{id} has already been recorded in archive".format(id = entry["id"])
        utils.log(string)
    return output


def entries_in_archive(entries, archive = None, negate: bool = False):
    """
    checks list of video entries  which is a list of video info_dicts (hopefully) 
    and returns whichever ones are or aren't already in the archive
    """
    return list(filter(lambda i: entry_in_archive(i, negate=negate, archive=archive), entries))
    

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

        if this.globs.args.ncc:
            playlist.auto_nickname()
        else:
            response = utils.ask_confirm(info, intype="playlist")
            match response:
                case "add playlist":
                    playlist.ask_nickname()
                case "add and ignore playlist":
                    playlist.ask_nickname()
                    playlist.ignore = True
                case "do not add playlist":
                    return
        playlist.make_dir()

        config.add_playlist(this.globs.conf, playlist)
        print(playlist)
        config.save(this.globs.conf, path = this.globs.args.conf)
        return playlist


def download_video(url, in_channel = None):
    outtmpl =  '%(upload_date)s %(title)s - %(id)s.%(ext)s'
    info_opts = {
        "extract_flat": True,
        #"download_archive": this.globs.args.archive,
        "cookiefile": this.globs.args.c,
        "outtmpl": {'default': outtmpl},
        "sleep_interval": 0.3,
        "sleep_interval_requests": 0.3
    }
    archive_opts = {
        "download_archive": this.globs.args.archive
    }
    ydl = yt_dlp.YoutubeDL(info_opts)
    ydl_archive = yt_dlp.YoutubeDL(archive_opts)
    try:
        entry = ydl.extract_info(url, download=False, process=True)
    except:
        return
    assert utils.get_infodict_type(entry) == "video"

    is_deja_downloaded: bool = entry_in_archive(entry)

    if is_deja_downloaded:
        return
    
    channel = [in_channel]
    if not channel[0]:
        channel[0] = get_channel(entry)
    channel = channel[0]

    if channel.ignore:
        utils.log("this channel is ignored from channel crawls {}".format(channel))
        
    response = utils.ask_confirm(entry, intype="single video")
    match response:
        case "queue to download":
            pass
        case "queue and ignore this uploader from channel crawls":
            channel.ignore = True
        case "ignore this":
            ydl_archive.record_download_archive(entry)
            return
        case "ignore this uploader from channel crawls":
            channel.ignore = True
            pass
        case "skip this":
            return

    entry["manager_selected_format"] = get_user_format(channel)

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


def crawl_playlist(index):
    utils.log("crawling playlist number "+index)
    # input may be provided as string
    index = int(index)
    playlist = this.globs.conf.playlists[index]
    crawl_playlist_url(playlist.url)


def crawl_channel(index):
    utils.log("crawling channel number "+index)
    # input may be provided as string
    index = int(index)
    channel = this.globs.conf.channels[index]
    crawl_playlist_url(config.Channel.playlist_url_from_id(channel.info_dict["channel_id"]), in_channel=channel)


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
            crawl_playlist_url(url, in_channel=channel)


def crawl_playlists():
    pass


def find_deja_downloaded(entry):
    utils.log("find_deja_downloaded run with video id {}".format(entry["id"]))
    matches = []
    for direntry in iglob("./**", recursive=True):
        if not os.path.isfile(direntry):
            continue
        result1 = re.search("{}.*$".format(entry["id"]), direntry)
        result2 = re.search(".*playlist.*", direntry)
        if result1 and not result2:
            utils.log("while searching for matching ids, we found {}".format(direntry))
            matches.append(direntry)
    
    def filter_infojson(i, log=True):
        utils.log("checking for .info.json "+i)
        if i.endswith(".info.json"):
            if log: utils.log("found two matches while searching for already downloaded id {id}, "
                              "one of them is an info json: {i}`\nthe other one will be symlinked"
                              " to".format(id=entry["id"], i=i))
        elif i.endswith(".description"):
            pass
        elif i.endswith(".jpg"):
            pass
        elif i.endswith(".webp"):
            pass
        else:
            return True

    utils.log("while running find_deja_downloaded, {} matches were found".format(len(matches)))
    if len(matches) >= 2:
        matches = list(filter(filter_infojson, matches))
        if len(matches) == 2:
            raise error.YTManager("while filtering two matched files with id: {id} neither were "
                                  ".info.json and therefore could not be narrowed down into one"
                                  .format(id=entry["id"]))
    if len(matches) == 1:
        matches = list(filter(lambda i: filter_infojson(i, log=False), matches))
        if len(matches) == 1:
            return matches[0]
        else:
            raise error.YTManager("only found an info json while searching for already downloaded "
                                  "video files. id: {}".format(entry["id"]))


def crawl_playlist_url(playlist, in_channel: config.Channel = None):
    # TODO: make --nc work
    outtmpl =  '%(upload_date)s %(title)s - %(id)s.%(ext)s'
    info_opts = {
        "extract_flat": True,
        #"download_archive": this.globs.args.archive,
        "cookiefile": this.globs.args.c,
        "outtmpl": {'default': outtmpl},
        "sleep_interval": 0.3,
        'extractor_args': {'youtube': {'player_client': 'web_embedded'}},
        "sleep_interval_requests": 0.3
    }
    archive_opts = {
        "download_archive": this.globs.args.archive
    }
    ydl = yt_dlp.YoutubeDL(info_opts)
    ydl_archive = yt_dlp.YoutubeDL(archive_opts)
    print("Getting info for playlist {}\n\n\n\n".format(playlist))
    try:
        info = ydl.extract_info(playlist, download=False, process=True)
    except:
        return
    assert info["_type"] == "playlist"

    entries = info["entries"]
    for entry in entries:
        pass
    deja_downloaded = entries_in_archive(info["entries"])
    utils.log("{} videos from playlist {} were already downloaded"
              .format(len(deja_downloaded), playlist))
    not_deja_downloaded = [x for x in info["entries"] if x not in deja_downloaded]
    utils.log("{} videos from playlist {} were NOT already downloaded"
              .format(len(not_deja_downloaded), playlist))

    selected_videos = []
    ignore_all  = [False]
    skip_all    = [False]

    def symlink_playlist(entry):
        try:
            entry_file = find_deja_downloaded(entry)
        except Exception as e:
            utils.log_error(str(e))
            input("press <Enter> to continue")
            return 
        utils.log(entry_file)
        playlist_dir = this.globs.conf.playlists[config.Playlist.find_in_list(
                                                url=info["webpage_url"])
                                                ].dir
        # ^ channel - name.ext
        try:
            sym_name = str(Path(entry_file).parent) + " - " + os.path.basename(entry_file)
            utils.relative_symlink(entry_file,
                                   os.path.join("playlists",
                                                playlist_dir,
                                                sym_name))
        except FileExistsError:
            utils.log("symlink for {} already exists in {}, skipping"
                      .format(entry_file, playlist_dir))
        except TypeError:
            utils.log("video was in archive but not in filesystem")

    if not in_channel:
        # runs when playlist and not channel is the input
        utils.log("crawl_playlist() run as playlist, not channel")
        for entry in deja_downloaded:
            symlink_playlist(entry)

    for entry in not_deja_downloaded:
        if ignore_all[0]:
            utils.log("recording id {} into archive because ignore_all is true".format(id))
            ydl.record_download_archive(entry)
            continue

        if skip_all[0]:
            utils.log("skipping {} because skip_all is true".format(id))
            continue

        try:
            entry = fetch_info(entry["url"])
        except:
            utils.log_error("error fetching info, skipping")
            continue

        channel = [in_channel]
        if not channel[0]:
            channel[0] = get_channel(entry)
        entry["manager_channel"] = channel[0]

        if this.globs.args.nc:
            entry["manager_selected_format"] = channel[0].preferred_format
            selected_videos.append(entry)
            continue

        response = utils.ask_confirm(entry, intype="video")
        match response:
            case "queue to download":
                entry["manager_selected_format"] = get_user_format(entry["manager_channel"])
                selected_videos.append(entry)
            case "queue and ignore this uploader from channel crawls":
                entry["manager_channel"].ignore = True
                entry["manager_selected_format"] = get_user_format(entry["manager_channel"])
                selected_videos.append(entry)
            case "ignore this":
                ydl_archive.record_download_archive(entry)
            case "ignore this and all later videos in the playlist":
                ydl_archive.record_download_archive(entry)
                ignore_all[0] = True
            case "ignore this uploader from channel crawls":
                entry["manager_channel"].ignore = True
            case "skip this":
                pass
            case "skip this and all later videos in the playlist":
                skip_all[0] = True
        continue

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
            'extractor_args': {'youtube': {'player_client': 'web_embedded'}}
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

        if not in_channel:
            symlink_playlist(entry)


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
                raise   ("this function cannot find default format if a channel isnt given."
                        "notify the developer or try fixing it urself smh")
            format.append(channel.preferred_format)
            break
        format.append(req)
        break
    return format[0]

