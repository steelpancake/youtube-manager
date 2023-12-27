import sys
import io
import webbrowser

def y_n_to_bool(str):
    return str == "y"


def clean_entries(dictionary):
    dictionary = dict(dictionary)
    try:
        del dictionary["entries"]
    except KeyError as e:
        pass

    try:
        del dictionary["formats"]
    except KeyError as e:
        pass

    try:
        del dictionary["requested_formats"]
    except KeyError as e:
        pass

    try:
        del dictionary["thumbnail"]
    except KeyError as e:
        pass

    try:
        del dictionary["thumbnails"]
    except KeyError as e:
        pass

    return dictionary


def ask_confirm(dictionary, type="<PLACEHOLDER>"):
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

    webbrowser.open(tmp["url"])

    string = string.format(type=type, title=dictionary["title"], id=dictionary["id"],url=tmp["url"], uploader=dictionary["uploader"])
    print(string)
    response = input("confirm?(Yes/No/Ignore) ").lower()
    if response == "i":
        return "ignore"
    elif response == "ia":
        return "ignore all"
    elif response == "n":
        return "no"
    elif response == "y":
        return "yes"
    return response


def log_error(message):
    print("ERROR: " + str(message), file=sys.stderr)


def log_warn(message):
    print("WARN: " + str(message), file=sys.stderr)

