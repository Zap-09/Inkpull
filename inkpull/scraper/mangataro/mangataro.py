import asyncio
import hashlib
import time
from typing import Literal

from bs4 import BeautifulSoup
from utils import log

from ...base.base_template import BaseTemplate
from ...base.downloader import ImageDownloader
from ...base.http_client import HttpClient

from .exceptions import MangaTatoException
from .config import MangaTaroConfig
from . import parsing


class MangaTaro(BaseTemplate):
    def __init__(self, headers=None, cookies=None):
        config = MangaTaroConfig()
        super().__init__(config)

        self.headers = headers or self.Config.find("headers", None)
        self.cookies = cookies or self.Config.find("cookies", None)

        self.client = HttpClient(self.headers,
                                 impersonate=self.Config.find("impersonate_browser"),
                                 cookies=self.cookies)
        self.downloader = ImageDownloader(headers=self.headers)

        self.site_download_folder = self.site_folder()

        self.html: str = ""
        self.current_offset = 0

    async def _download_one_chapter(self, url: str) -> None:
        chapter_id = parsing.chapter_id(url)
        try:
            chapter_html = self.client.get_url(url, "t")
        except Exception as e:
            log(str(e), "error", _noformat=True)
            log("An error occurred, skipping this entry", level="warn")
            return

        soup = BeautifulSoup(chapter_html, "lxml")

        title = parsing.comic_title_from_chapter(soup)
        chapter_name = parsing.chapter_name_from_chapter(soup)
        api = f"https://mangataro.org/auth/chapter-content?chapter_id={chapter_id}"

        json_response = self.client.get_url(api, "j")
        image_list = parsing.image_urls(json_response)

        output_dir = self.sanitize_path(self.site_download_folder / title / chapter_name)
        output_dir.mkdir(parents=True, exist_ok=True)

        await self.downloader.download_images_concurrently(
            urls=image_list,
            output_dir=output_dir
        )

    def download_one_chapter(self, url: str) -> None:
        asyncio.run(
            self._download_one_chapter(url)
        )

    @staticmethod
    def _generate_tokens() -> tuple[str, int]:
        # Token logic adapted from "mikf/gallery-dl"
        # Original repo https://github.com/mikf/gallery-dl/blob/master/gallery_dl/extractor/mangataro.py#L119
        current_timestamp = int(time.time())
        year, month, day, hour, _, _, _, _, _ = time.gmtime(current_timestamp)

        secret_string = f"{current_timestamp}mng_ch_{year:04}{month:02}{day:02}{hour:02}"
        token = hashlib.md5(secret_string.encode()).hexdigest()[:16]

        return token, current_timestamp

    def _make_url(self, manga_id: int,
                  offset: int,
                  limit: int,
                  order: Literal["DESC", "ASC"] = "ASC",
                  ) -> str:
        token, time_stamp = self._generate_tokens()

        url = f"https://mangataro.org/auth/manga-chapters?manga_id={manga_id}&offset={offset}&limit={limit}&order={order}&_t={token}&_ts={time_stamp}"

        return url

    async def _download_series(self, url: str):

        self.html = self.client.get_url(url, "t")
        soup = BeautifulSoup(self.html, "lxml")

        manga_id = parsing.manga_id(soup)
        title = parsing.comic_title(soup)

        self.download_cover()
        self.metadata()

        log(f"Download started for {title}", "info")

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
            chapter_urls = parsing.parse_chapter_urls(raw_chapter_list)
            nested_download_list.append(chapter_urls)

            has_more = json_response.get("has_more", False)
            if has_more:
                offset = json_response.get("offset")
                self.current_offset += offset

        chapters_to_download = self.flatten(nested_download_list)

        for i, chapter in enumerate(chapters_to_download):
            await self._download_one_chapter(
                url=chapter
            )
            await self.delay(minimum=0.4, maximum=1.3)

    def download_series(self, url: str) -> None:
        asyncio.run(
            self._download_series(url)
        )

    def download_cover(self):
        soup = BeautifulSoup(self.html, "lxml")
        url = parsing.cover_image(soup)
        if not url:
            return

        title = parsing.comic_title(soup)

        cover_bytes = self.client.get_url(url, "b")

        self.save_cover(
            cover_url=url,
            cover_bytes=cover_bytes,
            save_location=self.site_download_folder / self.sanitize_path(title)
        )

    def metadata(self):
        soup = BeautifulSoup(self.html, "lxml")

        title = parsing.comic_title(soup)
        alternative_title = parsing.alt_title(soup)
        auther_and_artist = parsing.author_and_artist(soup)
        tags = parsing.tags(soup)
        description = parsing.description(soup)
        status = parsing.comic_status(soup)

        metadata_dict = self.generate_metadata(
            title=title,
            author=auther_and_artist,
            artist=auther_and_artist,
            tags=tags,
            description=description,
            status=status,
            alternative_title=alternative_title,
        )
        self.create_metadata_file(
            file_path=self.site_download_folder / self.sanitize_path(title),
            data=metadata_dict
        )


def MangaTaro_main(url: str, mode: str):
    if not url:
        raise MangaTatoException("URL cannot be empty.")

    mangataro = MangaTaro()
    match mode:
        case "chapter":
            mangataro.download_one_chapter(url)
        case "series":
            mangataro.download_series(url)
        case _:
            log("Invalid mode", "error")
