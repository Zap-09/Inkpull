from .helper_funcs import flatten


def mihon_style(
        title: str,
        author: str | None,
        artist: str | None,
        tags: list | None,
        description: str | None,
        status: str | None,
        other_info: tuple | list | None):
    status_dict = {
        "unknown": "0",
        "ongoing": "1",
        "completed": "2",
        "complete": "2",
        "licensed": "3"
    }
    desc = description or "No description."
    desc += "\n\n\n\n"

    if other_info:
        desc += "\n".join(flatten(other_info))

    metadata = {
        "title": title,
        "author": author,
        "artist": artist,
        "tags": tags,
        "description": desc,
        "status": status_dict.get(status.lower(), "0"),
    }

    return metadata

