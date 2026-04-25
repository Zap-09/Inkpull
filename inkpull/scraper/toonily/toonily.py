import asyncio
from bs4 import BeautifulSoup
from utils import log

# base
from ...base.base_template import BaseTemplate
from ...base.downloader import ImageDownloader
from ...base.http_client import HttpClient

# toonily module imports
from .exceptions import ToonilyException
from .config import ToonilyConfig
from . import parsing


class Toonily(BaseTemplate):
    def __init__(self, headers=None, cookies=None):
        config = ToonilyConfig()
        super().__init__(config)

        self.headers = headers or self.Config.find("headers", None)
        self.cookies = cookies or self.Config.find("cookies", None)

        self.client = HttpClient(self.headers,
                                 impersonate=self.Config.find("impersonate_browser"),
                                 cookies=self.cookies)
        self.downloader = ImageDownloader(headers=self.headers)

        self.site_download_folder = self.site_folder()
        self.was_title_shown: bool = False

        self.series_html: str = ""
        self.series_title: str = ""

    async def _download_one_chapter(self, url: str) -> None:
        try:
            html = self.client.get_url(url, "t")
        except Exception as e:
            log(str(e), "error", _noformat=True)
            log("An error occurred, skipping this entry", level="warn")
            return

        soup = BeautifulSoup(html, "lxml")
        comic_name = parsing.comic_name(soup)
        chapter_name = parsing.chapter_name(soup)
        chapter_images = parsing.chapter_images(soup)
        output_dir = self.sanitize_path(self.site_download_folder / comic_name / chapter_name)

        if not self.was_title_shown:
            log(f"Downloading chapter '{chapter_name}' of '{comic_name}'")

            self.was_title_shown = True

        await self.downloader.download_images_concurrently(
            urls=chapter_images,
            output_dir=output_dir,
        )

    def download_one_chapter(self, url: str) -> None:
        asyncio.run(
            self._download_one_chapter(url=url)
        )

    async def _download_series(self, url: str) -> None:
        self.series_html = self.client.get_url(url, "t")

        soup = BeautifulSoup(self.series_html, "lxml")

        series_title = parsing.series_title(soup)
        self.series_title = series_title
        chapter_list = parsing.chapter_list(soup)

        log(f"Downloading series: '{series_title}'")
        self.was_title_shown = True

        cover_url = parsing.cover_src(soup)

        if cover_url:
            cover_image = self.client.get_url(cover_url, "b")
            cover_path = self.site_download_folder / series_title

            self.save_cover(
                cover_url=cover_url,
                cover_bytes=cover_image,
                save_location=self.sanitize_path(cover_path)
            )
        self.metadata()

        for chapter in chapter_list:
            await self._download_one_chapter(chapter)

    def download_series(self, url: str) -> None:
        asyncio.run(
            self._download_series(url=url)
        )

    def metadata(self):
        soup = BeautifulSoup(self.series_html, "lxml")
        title = parsing.series_title(soup)
        author = parsing.authors(soup)
        artist = parsing.artist(soup)
        description = parsing.description(soup)
        tags = parsing.tags(soup)
        genres = parsing.genres(soup)
        status = parsing.comic_status(soup)
        rating = parsing.rating(soup)
        views = parsing.view_count(soup)
        alt_titles = parsing.alternative_titles(soup)

        tags.extend(genres)
        tags = self.remove_dupes_in_list(tags)

        metadata_dict = self.generate_metadata(title=title,
                                               author=author,
                                               artist=artist,
                                               description=description,
                                               tags=tags,
                                               status=status,
                                               rating=rating,
                                               views=views,
                                               alternative_title=alt_titles
                                               )
        self.create_metadata_file(
            file_path=self.site_download_folder / self.sanitize_path(self.series_title),
            data=metadata_dict
        )

    @staticmethod
    def validate_url_mode(url: str, mode: str) -> None:
        url = url.rstrip("/")
        parts = url.split("/")

        if not parts:
            return

        last_part = parts[-1].lower()
        is_chapter_url = "chapter" in last_part

        if mode == "series" and is_chapter_url:
            log("Looks like you entered a chapter URL while in series mode.", "warn")
            log("You might not get the expected results.", "warn")

        elif mode == "chapter" and not is_chapter_url:
            log("Looks like you entered a series URL while in chapter mode.", "warn")
            log("You might not get the expected results.", "warn")


def Toonily_main(url: str, mode: str):
    if not url:
        raise ToonilyException("URL cannot be empty.")

    toonily = Toonily()
    toonily.validate_url_mode(url=url, mode=mode)
    match mode:
        case "series":
            toonily.download_series(url)
        case "chapter":
            toonily.download_one_chapter(url)
        case _:
            raise ToonilyException(f"Invalid mode: {mode}")
