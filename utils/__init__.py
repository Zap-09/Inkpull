import colorama

colorama.init()

from .terminal import log, user_confirmation
from .exceptions import check_status_code, ComicDlExceptions, GenericException
from .parsing_style import mihon_style
from .helper_funcs import (clean_folder_name,
                           find_project_root,
                           remove_dupes_in_list,
                           flatten,
                           open_config_file
                           )

__all__ = [
    "log",
    "user_confirmation",
    "find_project_root",
    "check_status_code",
    "ComicDlExceptions",
    "GenericException",
    "clean_folder_name",
    "remove_dupes_in_list",
    "flatten",
    "mihon_style",
    "open_config_file"
]
