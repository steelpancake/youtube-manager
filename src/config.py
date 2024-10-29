import json
import os
import sys
import jsonpickle
import main
import copy
import utils


class Config:
    def __init__(self):
        self.opts = []
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
        self.channels = []
        self.playlists = []

    def __repr__(self):
        output = ""
        for format in self.formats:
            output = output + str(format) + "\n"
        for channel in self.channels:
            output = output + str(channel) + "\n"
        for playlist in self.playlists:
            output = output + str(playlist) + "\n"
        return output


    def list_channels(self):
        for i in range(len(self.channels)):
            print(str(i) + "\t" + str(self.channels[i]))

    def list_playlists(self):
        for i in range(len(self.playlists)):
            print(str(i) + "\t" + str(self.playlists[i]))

    def reset_formats(self):
        new_conf = Config()
        self.formats = new_conf.formats

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
        for playlist in self.playlists:
            playlist.make_dir()
         
    def do_checks(self):
        self.check_make_channel_nicks()
        self.check_make_dirs()


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
        return "<Channel nick: '% s'\n\tdir: '% s'\n\turl: % s>" % (self.nick, self.dir, self.url)

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
        opts.update(format)
        return opts

    def make_dir(self):
        path = os.path.join(os.getcwd(), self.dir)
        os.makedirs(path, exist_ok=True)
        print("made directory for channel:\t", self.nick, "\tat  ", str(path))


class Playlist:
    def __init__(self):
        self.url = ""
        self.nick = ""
        self.dir = ""
        self.ignore = False
        self.deleted = False
        self.info_dict = {}
        self.preferred_format = "default"

    def from_info_dict(self, info):
        self.url = Playlist.playlist_url_from_id(info["id"])
        self.dir = self.nick
        self.info_dict = info
        self.ignore = False
        self.deleted = False
        return self

    def __repr__(self):
        return "<Playlist nick: '% s'\n\tdir: '% s'\n\turl: % s>" % (self.nick, self.dir, self.url)

    def is_playlist(info):
        if info["_type"] == "playlist":
            return True
        return False

    def find_in_list(url: str, arr=None):
        arr = [arr]
        if not arr[0]:
            import main
            arr[0] = main.globs.conf.playlists
            utils.log("using config playlists arr for list")
        arr = arr[0]
        utils.log("finding " + url + " in " + str(arr))
        for i in range(len(arr)):
            if arr[i].url == url:
                return i

    def is_url_in_list(url: str, arr):
        for entry in arr:
            if entry.url == url:
                return True
        return False

    def ask_nickname(self):
        self.nick = input("any nickname for this playlist? (leave blank for no) ") or self.info_dict["title"]
        self.dir = self.nick

    def playlist_url_from_id(id: str):
        return 'https://www.youtube.com/playlist?list=' + id

    def make_dir(self):
        path = os.path.join(os.getcwd(), "playlists", self.dir)
        os.makedirs(path, exist_ok=True)
        print("made directory for playlist:\t", self.nick, "\tat  ", str(path))


class Video:
    def __init__(self):
        pass

    def is_video(info):
        try:
            return info["webpage_url_basename"] == "watch"
        except:
            return False


def check_make_archive(path):
    if not os.path.exists(path):
        try:
            f = open(path, "x")
            f.close()
        except:
            print(format("could not create archive file:  {}", path), file=sys.stderr)
            sys.exit(1)


def get(path):
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
    print(str(conf))
    return conf


def save(conf, path):
    with open(path, "w") as f:
        f.write(jsonpickle.encode(conf, indent=4))


def add_channel(conf, channel):
    if not Channel.is_url_in_list(channel.url, conf.channels):
        conf.channels.append(channel)


def add_playlist(conf, playlist):
    if not Playlist.is_url_in_list(playlist.url, conf.playlists):
        conf.playlists.append(playlist)
