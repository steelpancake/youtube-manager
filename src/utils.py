import sys
import io
import webbrowser

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


def ask_confirm(dictionary, intype=None):
    type = get_infodict_type(dictionary, intype)
    string = (
        "\nPlease confirm this {type}"
        "\ntitle:\t{title}"
        "\nid:\t{id}"
        "\nurl:\t{url}"
        "\nuploader:\t{uploader}\n"
    )
    tmp = {}
    try:
        tmp["url"] = dictionary["webpage_url"]
    except:
        tmp["url"] = dictionary["url"]

    print(args)
    if not args.nb:
        webbrowser.open(tmp["url"])

    string = string.format(type=type, title=dictionary["title"], id=dictionary["id"],url=tmp["url"], uploader=dictionary["uploader"])
    print(string)
    response = input("confirm?(Yes/No/Ignore) leave blank for no ").lower()
    if response == "i":
        return "ignore"
    elif response == "ia":
        return "ignore all"
    elif response == "n":
        return "no"
    elif response == "y":
        return "yes"
    elif response == "skip":
        return "skip"
    return response

def log(message):
    if verbose:
        print("LOG: " + str(message), file=sys.stderr)

def log_error(message):
    print("ERROR: " + str(message), file=sys.stderr)


def log_warn(message):
    print("WARN: " + str(message), file=sys.stderr)

