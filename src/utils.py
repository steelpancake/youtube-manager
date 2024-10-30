import sys
import io
import os
import config
import error
import webbrowser
import questionary

verbose = True
args = None

def y_n_to_bool(str):
    return str == "y"


def clean_entries(dictionary, delete = ["entries", "formats", "requested_formats", "thumbnail", "thumbnails", "automatic_captions"]):
    dictionary = dict(dictionary)
    for idx in delete:
        try:
            del dictionary[idx]
        except KeyError as e:
            pass
    return dictionary


def print_dict(dictionary):
    for key in dictionary.keys():
        print(key)


def get_infodict_type(infodict, intype=None):
    if intype:
        return intype
    try:
        type = infodict["_type"]
    except:
        type = lambda : 'video' if infodict['fps'] else 'UNKNOWN TYPE'
        type = type()
    return type


def ask_confirm_string(dictionary, intype=None):
    type = get_infodict_type(dictionary, intype)
    string = (
        "\nPlease confirm this {type}"
        "\ntitle:\t{title}"
        "\nid:\t{id}"
        "\nurl:\t{url}"
        "\nuploader:\t{uploader}\n"
    )
    return string


def ask_confirm(dictionary, intype=None):
    type = get_infodict_type(dictionary, intype)
    string = ask_confirm_string(dictionary, intype=type)
    
    tmp = {}
    try:
        tmp["url"] = dictionary["webpage_url"]
    except:
        tmp["url"] = dictionary["url"]

    if not args.nb:
        webbrowser.open(tmp["url"])

    string = string.format( type=type, title=dictionary["title"], id=dictionary["id"],
            url=tmp["url"], uploader=dictionary["uploader"])
    print(string)

    question = "What do you want to do?"
    if type == "channel":
        return questionary.rawselect(
            question,
            choices=[
            "add channel",
            "add and ignore channel"
            ]).unsafe_ask()
    elif type == "video":
        return questionary.rawselect(
            question,
            choices=[
            "queue to download",
            "queue and ignore this uploader from channel crawls",
            "ignore this",
            "ignore this and all later videos in the playlist",
            "ignore this uploader from channel crawls",
            "skip this",
            "skip this and all later videos in the playlist"
            ]).unsafe_ask()
    elif type == "single video":
        return questionary.rawselect(
            question,
            choices=[
            "queue to download",
            "queue and ignore this uploader from channel crawls",
            "ignore this",
            "ignore this uploader from channel crawls",
            "skip this"
            ]).unsafe_ask()
    elif type == "playlist":
        return questionary.rawselect(
            question,
            choices=[
            "add playlist",
            "add and ignore playlist",
            "do not add playlist",
            ]).unsafe_ask()
    else: raise error.YTManager("unknown type provided to ask_confirm")


# taken from
# https://stackoverflow.com/questions/9793631/creating-a-relative-symlink-in-python-without-using-os-chdir
def relative_symlink(src, dst):
    dir = os.path.dirname(dst)
    src = os.path.relpath(src, dir)
    return os.symlink(src, dst)


def log(message):
    if verbose:
        print("LOG: " + str(message), file=sys.stderr)

def log_error(message):
    print("ERROR: " + str(message), file=sys.stderr)


def log_warn(message):
    print("WARN: " + str(message), file=sys.stderr)

