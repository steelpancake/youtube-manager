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
    string = string.format(type=type, title=dictionary["title"], id=dictionary["id"],url=dictionary["webpage_url"], uploader=dictionary["uploader"])
    print(string)
    return y_n_to_bool(input("confirm? "))
