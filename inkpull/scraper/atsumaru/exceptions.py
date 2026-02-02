from utils import log

class AtsumaruException(Exception):
    class Base(Exception):
        pass

    class MangaIDNotFound(Base):
        def __init__(self,ctx = None):
            if ctx:
                super().__init__(log(f"Manga ID not found. Context: '{ctx}'",
                                     "error",_return=True))
            else:
                super().__init__(log("Manga ID not found. Context",
                                     "error",_return=True))

    class MangaAndChapterIDNotFound(Base):
        def __init__(self,ctx = None):
            if ctx:
                super().__init__(log(f"Manga ID or Chapter ID Not Found. Context: '{ctx}'",
                                     "error",_return=True))
            else:
                super().__init__(log("Manga ID or Chapter ID Not Found. Context",
                                     "error",_return=True))
    class UnexpectedJsonStructure(Base):
        def __init__(self,ctx = None):
            if ctx:
                super().__init__(log(f"Unexpected Json Structure. Context: {ctx}",
                                     "error",_return=True))

    class NoChaptersToDownload(Base):
        def __init__(self,ctx = None):
            if ctx:
                super().__init__(log(f"No chapters to download. Context: {ctx}",
                                     "error",_return=True))
            else:
                super().__init__(log("No chapters to download",
                                     "error",_return=True))