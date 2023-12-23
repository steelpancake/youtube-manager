import json
import os
import sys
import jsonpickle
import main
import copy


class Config:
    def __init__(self):
        self.channels = []
        self.opts = []
        self.playlists = []
        self.formats = {
                "default": {
                     'format': '(bv+(250/251))[filesize<?50M][filesize_approx<?100M]',
                     'format_sort': ['vcodec:vp9', 'acodec', 'res:480'],
                }
        }


class Channel:
    import main
    def __init__(self):
        self.url = ""
        self.nick = ""
        self.dir = ""
        self.ignore = False
        self.deleted = False
        self.ignored_videos = []
        self.info_dict = {}
        self.preferred_format = "default"

    def __repr__(self):
        return "<Channel nick: % s, url: % s>" % (self.nick, self.url)

    def from_dict(self, dictionary):
        self.url = dictionary["url"]
        self.nick = dictionary["nick"]
        self.dir = dictionary["dir"]
        self.ignore = dictionary["ignore"]
        self.deleted = dictionary["deleted"]
        self.ignored_videos = dictionary["ignored_videos"]
        self.info_dict = dictionary["info_dict"]
        return self

    def from_info_dict(self, info):
        self.url = Channel.url_from_id(info["channel_id"])
        self.nick = input("any nickname for this channel? (leave blank for no) ") or info["uploader"]
        self.dir = self.nick
        self.info_dict = info
        self.ignore = False
        self.deleted = False
        self.ignored_videos = {}
        return self

    def url_from_id(url: str):
        return ("https://www.youtube.com/channel/" + url)

    def playlist_url_from_id(id: str):
        string = id[2:]
        return "https://www.youtube.com/playlist?list=" + "UU" + string

    def is_url_in_list(url: str, arr):
        for entry in arr:
            if entry.url == url:
                return True
        return False

    def find_in_list(url: str, arr=None):
        arr = [arr]
        if not arr[0]:
            import main
            arr[0] = main.globs.conf.channels
        arr = arr[0]
        for i in range(len(arr)):
            if arr[i].url == url:
                return i

    def opts_with_preferred_format(self, opts: dict):
        import main
        opts = copy.copy(opts)
        format = main.this.globs.conf.formats[self.preferred_format]
        opts['format'] = format['format']
        opts['format_sort'] = format['format_sort']
        return opts


class Video:
    def __init__(self):
        pass

    def is_video(info):
        try:
            return info["webpage_url_basename"] == "watch"
        except:
            return False


# converts a raw config into one containing the class versions
def raw_to_parsed(conf):
    channels = []
    for entry in conf["channels"]:
        channel = Channel().from_dict(entry)
        channels.append(channel)
    conf["channels"] = channels


def check_make_archive(path="archive.txt"):
    if not os.path.exists(path):
        try:
            f = open(path, "x")
            f.close()
        except:
            print(format("could not create archive file:  {}", path), file=sys.stderr)
            sys.exit(1)


def get(path = "config.json"):
    if not os.path.exists(path):
        try:
            f = open(path, "x")
            f.close()
            with open(path, "r+") as f:
                f.write(jsonpickle.encode(Config(), indent=4))
            return Config()
        except:
            print(format("could not create configuration file:  {}", path), file=sys.stderr)
            sys.exit(1)

    conf = None
    with open(path, "r") as f:
        conf = jsonpickle.decode(f.read())
    print(conf)
    return conf


def save(conf, path = "config.json"):
    with open(path, "w") as f:
        f.write(jsonpickle.encode(conf, indent=4))


def add_channel(conf, channel):
    if not Channel.is_url_in_list(channel.url, conf.channels):
        conf.channels.append(channel)
