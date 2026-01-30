from utils import log

class ToonilyException(Exception):
    class Base(Exception):
        """Base class for all ToonilyExceptions"""

    class ChapterListNotFound(Base):
        def __init__(self,entry_title = None):
            if entry_title:
                super().__init__(log(f"Chapter List Not Found. On Comic '{entry_title}'",
                                     "error",_return=True))
            else:
                super().__init__(log("Chapter List Not Found",
                                     "error",_return=True))

    class ChapterBoxNotFound(Base):
        def __init__(self,entry_title = None):
            if entry_title:
                super().__init__(log(f"Chapter Box Not Found. On Comic '{entry_title}'",
                                     "error",_return=True))
            else:
                super().__init__(log("Chapter Box Not Found",
                                     "error",_return=True))

    class ImageBoxNotFound(Base):
        def __init__(self,entry_title = None):
            if entry_title:
                super().__init__(log(f"Image Box Not Found. On Comic '{entry_title}'",
                                     "error",_return=True))
            else:
                super().__init__(log("Image Box Not Found",
                                     "error",_return=True))

    class ImagesNotFound(Base):
        def __init__(self,entry_title = None):
            if entry_title:
                super().__init__(log(f"Image Box Was Found But no Image. On Comic '{entry_title}'",
                                     "error",_return=True))
            else:
                super().__init__(log("Image Box Was Found But no Image",
                                     "error",_return=True))

    class TitleNotFound(Base):
        def __init__(self,entry_title = None):
            if entry_title:
                super().__init__(log(f"Title Not Found. On Comic '{entry_title}'",
                                      "error",_return=True))
            else:
                super().__init__(log("Title Not Found",
                                     "error",_return=True))

    class ChapterNameNotFound(Base):
        def __init__(self,url = None):
            if url:
                super().__init__(log(f"Chapter Name Not Found. On Url '{url}'"
                                     "error",_return=True))
            else:
                super().__init__(log("Chapter Name Not Found",
                                     "error",_return=True))

    class TitleNameNotFoundInChapter(Base):
        def __init__(self,url = None):
            if url:
                super().__init__(log(f"Series Name Not Found. On Url '{url}'"
                                     "error", _return=True))
            else:
                super().__init__(log("Series Name Not Found",
                                     "error", _return=True))

    # User input Exceptions

    class UrlNotProvided(Base):
        def __init__(self):
            super().__init__(log("Url not Provided",
                                 "error",_return=True))

    class InvalidArgs(Base):
        def __init__(self):
            super().__init__(log("Chapter Invalid Args",))
