from utils import log


class MangakatanaException(Exception):
    class Base(Exception):
        pass

    class ImageUrlsNotFound(Base):
        def __init__(self, ctx=None):
            if ctx:
                super().__init__(log(f"Could not find image urls. Context: '{ctx}'",
                                     "error", _return=True))
            else:
                super().__init__(log(f"Could not find image urls",
                                     "error", _return=True))

    class ComicNameNotFound(Base):
        def __init__(self, ctx=None):
            if ctx:
                super().__init__(log(f"Comic Title not found. Context: '{ctx}'",
                                     "error", _return=True))
            else:
                super().__init__(log(f"Comic Title not found",
                                     "error", _return=True))

    class ChapterNameNotFound(Base):
        def __init__(self, ctx=None):
            if ctx:
                super().__init__(log(f"Chapter Title not found. Context: '{ctx}'",
                                     "error", _return=True))
            else:
                super().__init__(log(f"Chapter Title not found",
                                     "error", _return=True))
    class ChapterUrlsNotFound(Base):
        def __init__(self, ctx=None):
            if ctx:
                super().__init__(log(f"Chapter list not found: '{ctx}'",
                                     "error", _return=True))
            else:
                super().__init__(log(f"Chapter list not found",
                                     "error", _return=True))

    class SeriesNameNotFound(Base):
        def __init__(self, ctx=None):
            if ctx:
                super().__init__(log(f"Series name not found: '{ctx}'",
                                     "error", _return=True))
            else:
                super().__init__(log(f"Series name not found",
                                     "error", _return=True))