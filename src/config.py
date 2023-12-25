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

    def list_channels(self):
        for i in range(len(self.channels)):
            print(str(i) + "\t" + str(self.channels[i]))

    def list_playlists(self):
        for playlist in self.playlists:
            print(playlist)

    def reset_formats(self):
        new_conf = Config()
        self.formats = new_conf.formats


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
        return "<Channel nick: '% s', \turl: % s>" % (self.nick, self.url)

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
        self.dir = self.nick
        self.info_dict = info
        self.ignore = False
        self.deleted = False
        self.ignored_videos = {}
        return self

    def ask_nickname(self):
        self.nick = input("any nickname for this channel? (leave blank for no) ") or self.info_dict["uploader"]
        self.dir = self.nick

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

    def find_in_list(self, url: str, arr=None):
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
        opts.update(format)
        return opts

    def make_dir(self):
        path = os.path.join(os.getcwd(), self.dir)
        os.makedirs(path, exist_ok=True)


class Video:
    def __init__(self):
        pass

    def is_video(info):
        try:
            return info["webpage_url_basename"] == "watch"
        except:
            return False


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
