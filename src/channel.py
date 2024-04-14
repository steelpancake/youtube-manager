import main
import utils
import config

class Channel:
    def __init__(self):
        self.url = ""
        self.nick = ""
        self.dir = ""
        self.ignore = False
        self.deleted = False
        self.ignored_videos = []
        self.info_dict = {}
        self.preferred_format = "default"

    def checks(self):
        if not check_preferred_format_exists():
            utils.printe(format("preferred_format for {} does not exist in configuration, setting to 'default'"))
        self.preferred_format = "default"

    def check_preferred_format_exists(self):
        config.persistent.check_format_exists(self.preferred_format)
