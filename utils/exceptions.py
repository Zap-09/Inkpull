from . import log

class ComicDlExceptions(Exception):
    class Base(Exception):
        """Base class for all ComicDlExceptions"""
        pass

    class NotFound(Base):
        """Status Code 404"""
        def __init__(self, url=None):
            if url:
                super().__init__(log(f"Endpoint Not Found, Status Code 404",
                                     "error",_return=True))
            else:
                super().__init__(log(f"Endpoint Not Found, Status Code 404: '{url}'",
                                     "error",_return=True))

    class BadRequest(Base):
        """Status Code 400"""
        def __init__(self, url=None):
            if url:
                super().__init__(log(f"Bad Request, Status Code 400: '{url}"))
            else:
                super().__init__(log(f"Bad Request, Status Code 400"))

    class Unauthorized(Base):
        """Status Code 401"""
        def __init__(self, url=None):
            if url:
                super().__init__(log("Unauthorized, Status Code 401",
                                     "error",_return=True))
            else:
                super().__init__(log(f"Unauthorized, Status Code 401: '{url}'",
                                     "error",_return=True))

    class Forbidden(Base):
        """Status Code 403"""
        def __init__(self, url=None):
            if url:
                super().__init__(log(f"Forbidden, Status Code 403: '{url}'",
                                     "error",_return=True))
            else:
                super().__init__(log("Forbidden, Status Code 403",
                                     "error",_return=True))


def check_status_code(status_code, url=None):
    """Checks status code"""
    if status_code == 200:
        return
    if status_code == 404:
        raise ComicDlExceptions.NotFound(url)
    elif status_code == 400:
        raise ComicDlExceptions.BadRequest(url)
    elif status_code == 401:
        raise ComicDlExceptions.Unauthorized(url)
    elif status_code == 403:
        raise ComicDlExceptions.Forbidden(url)
    else:
        pass

class GenericException(Exception):
    """Generic Exception"""
    class Base(Exception):
        """Base class for all generic exceptions"""
        pass
    class UserRejection(Base):
        def __init__(self,ctx = None):
            if ctx:
                super().__init__(log(ctx,"error",_return=True))
            else:
                super().__init__(log("UserRejection","error",_return=True))
