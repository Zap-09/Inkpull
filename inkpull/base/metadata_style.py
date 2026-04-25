from inkpull.base.helper_mixin import HelperMixin


class StyleMixin(HelperMixin):
    STYLES = {}

    @classmethod
    def register_style(cls, name: str):
        def decorator(func):
            cls.STYLES[name] = func
            return func

        return decorator

    def _build_metadata(self, style: str, **kwargs) -> dict:
        fn = self.STYLES.get(style)

        if not fn:
            available = ", ".join(self.STYLES.keys())
            raise ValueError(f"Unknown style '{style}'. Available: {available}")

        return fn(self, **kwargs)


@StyleMixin.register_style("mihon")
def mihon_style(ctx: StyleMixin, **kwargs):
    status_dict = {
        "unknown": "0",
        "ongoing": "1",
        "completed": "2",
        "complete": "2",
        "end": "2",
        "ended": "2",
        "finished": "2",
        "finish": "2",
        "licensed": "3",
        "publishing finished": "4",
        "cancelled": "5",
        "on hiatus": "6"
    }

    def get_status_code(name):
        try:
            name = int(name)
        except (ValueError, TypeError):
            pass

        if isinstance(name, int):
            if name in {0, 1, 2, 3, 4, 5, 6}:
                return name
            return 0

        if isinstance(name, str):
            return status_dict.get(name.lower(), 0)

        return 0

    title = kwargs.get("title") or "Unknown Title"
    author = kwargs.get("author") or "Unknown Author"
    artist = kwargs.get("artist") or "Unknown Artist"
    tags = kwargs.get("tags") or []
    description = kwargs.get("description") or "No description"
    status = kwargs.get("status", "0")

    _KNOWN_KEYS = {"title", "author", "artist", "tags", "description", "status"}

    extra = {}
    for key in kwargs:
        if key not in _KNOWN_KEYS:
            value = kwargs.get(key)
            if value is not None:
                extra[key] = value

    if extra:
        other_info = []

        for key in extra:
            value = extra[key]

            pretty_key = key.replace("_", " ").title()

            line = f"{pretty_key}: {value}"
            other_info.append(line)

        description += "\n\n\n\n"
        description += "\n".join(ctx.flatten(other_info))

    return {
        "title": title,
        "author": ctx.make_list_str(author),
        "artist": ctx.make_list_str(artist),
        "genre": tags,
        "description": description,
        "status": get_status_code(status)
    }
