from utils import log


class MangaTatoException(Exception):
    class Base(Exception):
        """Base class for all MangaTatoException"""

    class ChapterIdNotFound(Base):
        def __init__(self, ctx=None):
            if ctx:
                super().__init__(log(f"Can't locate chapter id in the url: {ctx}",
                                     "error", _return=True))
            else:
                super().__init__(log(f"Can't locate chapter id in the url",
                                     "error", _return=True))

    class TitleNotFound(Base):
        def __init__(self, ctx=None):
            if ctx:
                super().__init__(log(f"Can't locate title in chapter html: {ctx}",
                                     "error", _return=True))
            else:
                super().__init__(log(f"Can't locate title in chapter html",
                                     "error", _return=True))

    class ImageSrcListNotFound(Base):
        def __init__(self, ctx=None):
            if ctx:
                super().__init__(log(f"Chapter list not in the json Data: {ctx}",
                                     "error", _return=True))
            else:
                super().__init__(log(f"Chapter list not in the json Data",
                                     "error", _return=True))

    class BodyNotFoundInHtml(Base):
        def __init__(self, ctx=None):
            if ctx:
                super().__init__(log(f"Body tag can not be found in the HTML response: {ctx}",
                                     "error", _return=True))
            else:
                super().__init__(log(f"Body tag can not be found in the HTML response",
                                     "error", _return=True))

    class MangaIdNotFound(Base):
        def __init__(self, ctx=None):
            if ctx:
                super().__init__(log(f"Manga ID can't find in the HTML response: {ctx}",
                                     "error", _return=True))
            else:
                super().__init__(log(f"Manga ID can't find in the HTML response",
                                     "error", _return=True))

    class InvalidJsonResponse(Base):
        def __init__(self, ctx=None):
            if ctx:
                super().__init__(log(f"Invalid Json response: {ctx}", "error", _return=True))
            else:
                super().__init__(log(f"Invalid Json response", "error", _return=True))

    class ChapterUrlNotFound(Base):
        def __init__(self, ctx=None):
            if ctx:
                super.__init__(log(f"The chapter count is less than 1 or is missing: {ctx}", "error", _return=True))
            else:
                super.__init__(log(f"The chapter count is less than 1 or is missing", "error", _return=True))


