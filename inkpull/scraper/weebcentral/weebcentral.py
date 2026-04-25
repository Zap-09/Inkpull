import asyncio
from bs4 import BeautifulSoup
from utils import log

# base
from ...base.downloader import ImageDownloader
from ...base.http_client import HttpClient
from ...base.base_template import BaseTemplate

# WeebCentral module imports
from .config import WeebCentralConfig
from .exceptions import WeebCentralException

from . import parsing


class WeebCentral(BaseTemplate):
    def __init__(self, headers=None, cookies=None):
        # ------configs------ #
        config = WeebCentralConfig()
        super().__init__(config)

        self.headers = headers or self.Config.find("headers", None)
        self.cookies = cookies or self.Config.find("cookies", None)

        self.client = HttpClient(
            headers=self.headers,
            cookies=self.cookies,
            impersonate=self.Config.find("impersonate", None)
        )
        self.downloader = ImageDownloader(
            headers=self.headers
        )

        self.site_download_folder = self.site_folder()

        self.chapter_list_html: str = ""
        self.series_html: str | None = None
        self.chapter_list: list = []

        self.series_name: str | None = None

    async def _download_one_chapter(self, url) -> None:
        try:
            html = self.client.get_url(url, mode="t")
        except Exception as e:
            log(str(e), "error", _noformat=True)
            log("An error occurred while downloading the chapter, skipping this")
            return

        soup = BeautifulSoup(html, "lxml")

        if self.series_name is None:
            self.series_name = parsing.title_from_chapter(soup)

        chapter_id = parsing.chapter_id(url)
        chapter_name = parsing.chapter_name(soup)

        chapter_api = f"https://weebcentral.com/chapters/{chapter_id}/images?is_prev=False&current_page=1&reading_style=long_strip"
        api_response = self.client.get_url(chapter_api, "t")

        src_list = parsing.image_src_of_chapter(api_response)

        output_folder = self.sanitize_path(self.site_download_folder / self.series_name / chapter_name)

        await self.downloader.download_images_concurrently(
            urls=src_list,
            output_dir=output_folder
        )

    def download_one_chapter(self, url: str) -> None:
        asyncio.run(
            self._download_one_chapter(url)
        )

    async def _download_series(self, url: str) -> None:
        self.series_html = self.client.get_url(url, mode="t")
        soup = BeautifulSoup(self.series_html, "lxml")

        self.series_name = parsing.title_from_series_page(soup)
        chapter_id = parsing.series_id(url)
        full_chapter_api = f"https://weebcentral.com/series/{chapter_id}/full-chapter-list"
        self.chapter_list_html = self.client.get_url(full_chapter_api, mode="t")
        chapter_list = parsing.all_chapter_href(self.chapter_list_html)
        chapter_list.reverse()

        log(f"Download Started for: {self.series_name}")

        cover_url = parsing.cover_url(soup)
        if cover_url:
            cover_bytes = self.client.get_url(cover_url, mode="b")
            self.save_cover(
                cover_url=cover_url,
                cover_bytes=cover_bytes,
                save_location=self.site_download_folder / self.series_name
            )

        self.metadata()

        for chapter in chapter_list:
            await self._download_one_chapter(chapter)

    def download_series(self, url: str) -> None:
        asyncio.run(
            self._download_series(url)
        )

    def metadata(self):
        soup = BeautifulSoup(self.series_html, "lxml")
        title = self.series_name
        author = parsing.author(soup)
        artist = author
        tags = parsing.tags(soup)
        status = parsing.status(soup)
        released_year = parsing.released_year(soup)
        official_tl = parsing.is_official_translation(soup)
        anime_adaptation = parsing.anime_adaptation(soup)
        description = parsing.description(soup)
        comic_type = parsing.comic_type(soup)
        is_adult_content = parsing.is_adult_content(soup)

        metadata_dict = self.generate_metadata(
            title=title,
            author=author,
            artist=artist,
            type=comic_type,
            tags=tags,
            status=status,
            released_year=released_year,
            official_translation=official_tl,
            anime_adaptation=anime_adaptation,
            adult_content=is_adult_content,
            description=description
        )

        self.create_metadata_file(
            file_path=self.site_download_folder / self.series_name,
            data=metadata_dict
        )


def Weebcentral_main(url: str, mode: str):
    weebcentral = WeebCentral()
    match mode:
        case "series":
            weebcentral.download_series(url)
        case "chapter":
            weebcentral.download_one_chapter(url)
        case _:
            raise WeebCentralException.InvalidArgs
