import asyncio
import random
import re
from pathlib import Path
from typing import Iterable

import utils

class HelperMixin:

    @staticmethod
    async def delay(minimum: float, maximum: float) -> None:
        """ A simple delay timer that takes a range """
        await asyncio.sleep(random.uniform(minimum, maximum))

    @staticmethod
    def clean_folder_name(name: str) -> str:
        """ Removes invalid Characters in folder/file name """

        invalid_chars = r"[\/:*?\"<>|]"
        name = re.sub(invalid_chars, " ", name)
        name = re.sub(r"\s+", " ", name)
        name = name.strip()
        if name.endswith("."):
            name = name.rstrip(".") + "…"

        return name

    @staticmethod
    def flatten(iterable: list | tuple, *, _cast_to_string: bool = False) -> list:
        result = []
        stack = [iterable]

        while stack:
            current = stack.pop()
            if isinstance(current, Iterable) and not isinstance(current, (str, bytes)):
                stack.extend(reversed(list(current)))
            else:
                if _cast_to_string:
                    result.append(str(current))
                else:
                    result.append(current)
        return result

    @staticmethod
    def remove_dupes_in_list(*all_lists: list | tuple) -> list:
        """ Removes duplicate items in lists while keeping the order """
        big_list = []
        seen = set()
        for lst in all_lists:
            if lst is None:
                continue
            for i in lst:
                if i not in seen:
                    big_list.append(i)
                    seen.add(i)
        return big_list

    @staticmethod
    def make_list_str(input_list: list | str | None) -> str:
        if not input_list:
            return ""
        if isinstance(input_list, str):
            return input_list
        big_str = ", ".join(str(item) for item in input_list)
        return big_str

    @staticmethod
    def find_project_root() -> Path:
        return utils.find_project_root()

    @staticmethod
    def open_config_file():
        utils.open_config_file()

