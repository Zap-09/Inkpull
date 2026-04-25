import asyncio

from ...base.base_template import BaseTemplate
from .config import MangakatanaConfig
from ...base.downloader import ImageDownloader
from ...base.http_client import HttpClient
from utils import log

from . import parsing


class Mangakatana(BaseTemplate):
    def __init__(self, headers=None, cookies=None):
        config = MangakatanaConfig()
        super().__init__(config)

        self.headers = headers or self.Config.find("headers", None)
        self.cookies = cookies or self.Config.find("cookies", None)

        self.client = HttpClient(self.headers,
                                 impersonate=self.Config.find("impersonate_browser"),
                                 cookies=self.cookies)
        self.downloader = ImageDownloader(headers=self.headers)

        self.site_download_folder = self.site_folder()

        self.series_html = ""
        self.series_title = ""

    async def _download_one_chapter(self, url: str):
        url = parsing.switch_server(url)
        try:
            html = self.client.get_url(url, "t")
        except Exception as e:
            log(str(e), "error", _noformat=True)
            log("An error occurred, skipping this entry", level="warn")
            return
        image_src = parsing.get_image_src(html, url)

        comic_title = parsing.get_comic_name(html, url)
        chapter_name = parsing.get_chapter_title(html, url)

        output_dir = self.sanitize_path(self.site_download_folder / comic_title / chapter_name)

        await self.downloader.download_images_concurrently(
            output_dir=output_dir,
            urls=image_src,
        )

    def download_one_chapter(self, url: str):
        asyncio.run(self._download_one_chapter(url))

    def _download_cover(self, url: str | None):
        if url is None:
            log(f"Cover url not found", "warn")
            return
        try:
            response = self.client.get_url(url)
            save_dir = self.site_download_folder / self.series_title
            self.save_cover(cover_url=url, cover_bytes=response, save_location=save_dir)
        except Exception:
            log("Failed to download cover", "warn")
            return

    async def _download_series(self, url: str):
        self.series_html = self.client.get_url(url, "t")

        self.series_title = parsing.get_series_name(self.series_html)
        log(f"Download started for: {self.series_title}", "info")

        self.save_metadata()

        chapter_urls = parsing.get_chapter_urls(self.series_html, url)
        for href in chapter_urls:
            await self._download_one_chapter(href)
            await self.delay(minimum=0.7, maximum=1.5)

    def save_metadata(self):
        title = self.series_title
        alt_title = parsing.get_alt_title(self.series_html)
        author = parsing.get_author(self.series_html)
        artist = author
        tags = parsing.get_tags(self.series_html)
        status = parsing.get_status(self.series_html)
        description = parsing.get_description(self.series_html)

        metadata = self.generate_metadata(
            title=title,
            author=author,
            artist=artist,
            tags=tags,
            description=description,
            status=status,
            alternative_titles=alt_title
        )
        self.create_metadata_file(
            file_path=self.sanitize_path(self.site_download_folder / self.series_title),
            data=metadata
        )

    def download_series(self, url: str):
        asyncio.run(self._download_series(url))


def Mangakatana_main(url: str, mode: str):
    if not url:
        raise Exception("url is required")

    mangakatana = Mangakatana()
    match mode:
        case "chapter":
            mangakatana.download_one_chapter(url)
        case "series":
            mangakatana.download_series(url)
        case _:
            log("Invalid mode", "error")
