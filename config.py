import json
import os
import sys


default_config = {
    "channels" : [],
    "opts" : [],
    "playlists" : []
}


class Channel:
    def __init__(self):
        self.url = ""
        self.nick = ""
        self.dir = ""
        self.ignore = False
        self.deleted = False
        self.ignored_videos = []
        self.info_dict = {}

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



def get(path = "config.json"):
    if not os.path.exists(path):
        try:
            f = open(path, "x")
            f.close()
            with open(path, "r+") as f:
                f.write(json.dumps(default_config, indent=4))
            return default_config
        except:
            print(format("could not create configuration file:  {}", path), file=sys.stderr)

    conf = None
    with open(path, "r") as f:
        conf = json.loads(f.read())
    raw_to_parsed(conf)
    print(conf)
    return conf


def save(conf, path = "config.json"):
    print(json.dumps(conf, indent=2))


def add_channel(globs, channel):
    globs.conf["channels"].append(channel)
