from utils import log

class WeebCentralException(Exception):
    class Base(Exception):
        """Base class for all ToonilyExceptions"""

    class SeriesIdNotFound(Base):
        def __init__(self,ctx = None):
            if ctx:
                super().__init__(log(f"Can't find comic ID on: '{ctx}'",
                                     "error",_return=True))
            else:
                super().__init__(log("Can't find comic ID on",
                                     "error",_return=True))

    class ChapterIdNotFound(Base):
        def __init__(self,ctx = None):
            if ctx:
                super().__init__(log(f"Can't find comic ID on: '{ctx}'",
                                     "error",_return=True))
            else:
                super().__init__(log("Can't find comic ID on",
                                     "error",_return=True))

    class ChapterImagesNotFound(Base):
        def __init__(self, ctx = None):
            if ctx:
                super().__init__(log(f"Images Not Found. On Comic '{ctx}'",
                                     "error", _return=True))
            else:
                super().__init__(log("Images Not Found",
                                     "error",_return=True))

    class TitleAndChapterNotFound(Base):
        def __init__(self, ctx = None):
            if ctx:
                super().__init__(log(f"Title and Chapter was not found. On Comic '{ctx}'",
                                     "error", _return=True))
            else:
                super().__init__(log("Title and Chapter was not found",
                                     "error",_return=True))

    class TitleNotFound(Base):
        def __init__(self,entry_title = None):
            if entry_title:
                super().__init__(log(f"Title Not Found. On Comic '{entry_title}'",
                                      "error",_return=True))
            else:
                super().__init__(log("Title Not Found",
                                     "error",_return=True))



    # User input Exceptions

    class UrlNotProvided(Base):
        def __init__(self):
            super().__init__(log("Url not Provided",
                                 "error",_return=True))

    class InvalidArgs(Base):
        def __init__(self):
            super().__init__(log("Chapter Invalid Args",))
