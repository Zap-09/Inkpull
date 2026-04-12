import asyncio
import hashlib
import random
import time
import json
from pathlib import Path
from typing import Literal

from utils import (clean_folder_name,
                   log,
                   find_project_root,
                   mihon_style,
                   flatten)
from .exceptions import MangaTatoException

# base
from ...base.downloader import ImageDownloader
from ...base.http_client import HttpClient

# global config
from ...config import GConfig

# mangataro module imports
from .config import MangaTaroConfig
from .parsing import (find_chapter_id,
                      find_title_chapter_name,
                      get_image_urls, get_manga_id,
                      parse_chapter_urls,
                      get_alt_title,
                      find_author_and_artist, get_tags, find_description, comic_status, get_title, find_cover_image)


class MangaTaro:
    def __init__(self, headers=None, cookies=None):
        self.config = MangaTaroConfig()

        self.headers = headers or self.config.find("headers", None)
        self.cookies = cookies or self.config.find("cookies", None)

        self.project_root = find_project_root()
        self.base_dl = self.project_root / GConfig.global_get("Download_location")
        self.download_folder_name = self.config.find("download_folder")

        self.client = HttpClient(self.headers,
                                 impersonate=self.config.find("impersonate_browser"),
                                 cookie=self.cookies)

        self.downloader = ImageDownloader(headers=self.headers)

        self.api = ""
        self.html = ""
        self.current_offset = 0

    async def _download_one_chapter(self, url: str):
        chapter_id = find_chapter_id(url)
        try:
            chapter_html = self.client.get_url(url, "t")
        except Exception as e:
            log(str(e), "error", _noformat=True)
            log("An error occurred, skipping this entry", level="warn")
            return

        title, chapter_name = find_title_chapter_name(chapter_html)
        api = f"https://mangataro.org/auth/chapter-content?chapter_id={chapter_id}"

        json_response = self.client.get_url(api, "j")

        image_list = get_image_urls(json_response)

        output_dir = Path(self.project_root /
                          self.base_dl /
                          self.download_folder_name /
                          clean_folder_name(title) /
                          clean_folder_name(chapter_name))
        output_dir.mkdir(parents=True, exist_ok=True)

        await self.downloader.download_images_concurrently(
            urls=image_list,
            output_dir=output_dir
        )

    def download_one_chapter(self, url: str):
        asyncio.run(
            self._download_one_chapter(url)
        )

    def _get_manga_html(self, url: str):
        self.html = self.client.get_url(url, "t")

    def _get_manga_id(self):
        html = self.html
        return get_manga_id(html)

    def _make_url(self, manga_id: int,
                  offset: int,
                  limit: int,
                  order: Literal["DESC", "ASC"] = "ASC",
                  ) -> str:
        token, time_stamp = self._generate_tokens()

        url = f"https://mangataro.org/auth/manga-chapters?manga_id={manga_id}&offset={offset}&limit={limit}&order={order}&_t={token}&_ts={time_stamp}"

        return url

    @staticmethod
    def _generate_tokens() -> tuple[str, int]:
        # Token logic adapted from "mikf/gallery-dl"
        # Original repo https://github.com/mikf/gallery-dl/blob/master/gallery_dl/extractor/mangataro.py#L119
        current_timestamp = int(time.time())
        year, month, day, hour, _, _, _, _, _ = time.gmtime(current_timestamp)

        secret_string = f"{current_timestamp}mng_ch_{year:04}{month:02}{day:02}{hour:02}"
        token = hashlib.md5(secret_string.encode()).hexdigest()[:16]

        return token, current_timestamp

    async def _download_series(self, url: str):
        """https://mangataro.org/manga/i-killed-an-academy-player"""

        self._get_manga_html(url)
        manga_id = get_manga_id(self.html)
        title = get_title(self.html)
        log(f"Download started for {title}", "info")

        self._get_cover()
        self._get_metadata()

        has_more: bool = True

        nested_download_list = []

        while has_more:

            api_url = self._make_url(manga_id=manga_id,
                                     offset=self.current_offset,
                                     limit=500,
                                     order="ASC")

            json_response = self.client.get_url(api_url, "j")
            if not json_response.get("success"):
                raise MangaTatoException.InvalidJsonResponse(json_response)

            raw_chapter_list = json_response.get("chapters", None)
            chapter_urls = parse_chapter_urls(raw_chapter_list)
            nested_download_list.append(chapter_urls)

            has_more = json_response.get("has_more", False)
            if has_more:
                offset = json_response.get("offset")
                self.current_offset += offset

        chapters_to_download = flatten(nested_download_list)

        for i, chapter in enumerate(chapters_to_download):
            await self._download_one_chapter(
                url=chapter
            )
            await asyncio.sleep(random.uniform(0.7, 1.5))

    def download_series(self, url: str):
        asyncio.run(
            self._download_series(url)
        )

    def _get_metadata(self):
        html = self.html

        title = get_title(html)
        alt_titles = get_alt_title(html)
        auther_and_artist = find_author_and_artist(html)
        tags = get_tags(html)
        description = find_description(html)
        status = comic_status(html)

        metadata = mihon_style(
            title=title,
            artist=auther_and_artist,
            author=auther_and_artist,
            tags=tags,
            description=description,
            status=status,
            other_info=(
                f"Other Titles: {alt_titles}",
            )
        )

        json_file_path = self.base_dl / self.download_folder_name / clean_folder_name(title)
        json_file_path.mkdir(exist_ok=True, parents=True)
        json_file_name = clean_folder_name(self.config.find("metadata_file_name"))
        json_path = json_file_path / f"{json_file_name}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            data = json.dumps(metadata,
                              indent=4,
                              ensure_ascii=GConfig.global_get("ensure_ascii", False))
            f.write(data)

    def _get_cover(self):
        url = find_cover_image(self.html)

        if not url:
            return
        title = get_title(self.html)

        ext = Path(url).suffix or ".jpg"
        res = self.client.get_url(url, "b")
        save_folder = self.base_dl / self.download_folder_name / title
        save_folder.mkdir(exist_ok=True, parents=True)

        file_name = save_folder / f"Cover{ext}"
        with open(file_name, "wb") as f:
            f.write(res)
        log("Cover Downloaded", "info")


def MangaTaro_main(url: str, mode: str):
    if not url:
        raise Exception("url is required")

    mangataro = MangaTaro()
    match mode:
        case "chapter":
            mangataro.download_one_chapter(url)
        case "series":
            mangataro.download_series(url)
        case _:
            log("Invalid mode", "error")
