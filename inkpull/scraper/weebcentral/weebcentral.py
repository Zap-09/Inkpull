import asyncio
import json
from pathlib import Path

from utils import log, clean_folder_name, mihon_style, find_project_root

# base
from ...base.downloader import ImageDownloader
from ...base.http_client import HttpClient

# global config
from ...config import GConfig

# WeebCentral module imports
from .config import WeebCentralConfig
from .exceptions import WeebCentralException

from .parsing import (find_series_id,
                      find_all_src_of_chapter,
                      find_title_and_chapter_name,
                      find_chapter_id,
                      find_title,
                      find_all_chapter_href, parse_info, get_description, find_cover_url)


class WeebCentral:
    def __init__(self, headers=None, cookies=None):
        # ------configs------ #
        self.config = WeebCentralConfig()
        self.project_root = find_project_root()
        self.headers = headers or self.config.find("headers", None)
        self.cookie = cookies or self.config.find("cookies", None)
        self.base_dl = GConfig.global_get("Download_location")
        self.download_folder_name = self.config.find("download_folder")

        # ------clients------ #
        self.client = HttpClient(self.headers,
                                 impersonate=self.config.find("impersonate_browser"),
                                 cookie=self.cookie)
        self.downloader = ImageDownloader(headers=self.headers)

        self.chapter_list_html: str = ""
        self.series_html: str = ""
        self.chapter_list: list = []

        # ------metadata------ #
        self.title: str = ""

    async def _download_one_chapter(self, url, is_one=False):
        chapter_page_response = self.client.get_url(url, mode="t")
        title, chapter_name = find_title_and_chapter_name(chapter_page_response)
        if is_one:
            log(f"Downloading {chapter_name} of {title}")
        chapter_id = find_chapter_id(url)
        chapter_api = f"https://weebcentral.com/chapters/{chapter_id}/images?is_prev=False&current_page=1&reading_style=long_strip"
        ch_api_res = self.client.get_url(chapter_api, mode="t")
        src_list = find_all_src_of_chapter(ch_api_res)

        output_folder = (
                Path(self.project_root) /
                self.base_dl /
                self.download_folder_name /
                clean_folder_name(title) /
                clean_folder_name(chapter_name)
        )
        await self.downloader.download_concurrently(
            urls=src_list,
            output_dir=output_folder
        )

    def download_one_chapter(self, url: str):
        asyncio.run(
            self._download_one_chapter(url, True)
        )

    async def _download_series(self, url: str):
        self.series_html = self.client.get_url(url, mode="t")

        self.title = find_title(self.series_html)
        chapter_id = find_series_id(url)
        full_chapter_api = f"https://weebcentral.com/series/{chapter_id}/full-chapter-list"
        self.chapter_list_html = self.client.get_url(full_chapter_api, mode="t")
        chapter_list = find_all_chapter_href(self.chapter_list_html)
        chapter_list.reverse()


        log(f"Download Started for: {self.title}")
        self._get_cover()
        self.make_metadata_file()


        for chapter in chapter_list:
            try:
                await self._download_one_chapter(chapter)
            except WeebCentralException as we:
                log(f"Failed to download {chapter} error: {str(we)}", "error")

            except Exception as e:
                log(f"Failed to download {chapter} error: {str(e)}", "error")

    def download_series(self, url):
        asyncio.run(
            self._download_series(url)
        )

    def make_metadata_file(self):
        html = self.series_html
        title = self.title
        author = parse_info(html, "Author(s):", title)
        tags = parse_info(html, "Tags(s):", title, _list=True)
        status = parse_info(html, "Status:", title)
        released_year = parse_info(html, "Released:", title, _selector="span")
        official_tl = parse_info(html, "Official Translation:", title)
        anime_adaptation = parse_info(html, "Anime Adaptation:", title)
        description = get_description(html, title)

        released_year = f"Released Year: {released_year}"
        official_tl = f"Official Translation: {official_tl}"
        anime_adaptation = f"Anime Adaptation: {anime_adaptation}"

        metadata = mihon_style(
            title=title,
            author=author,
            artist=author,
            tags=tags,
            status=status,
            description=description,
            other_info=(released_year, anime_adaptation, official_tl)
        )

        json_file_path = (Path(self.project_root) /
                          self.base_dl /
                          self.download_folder_name /
                          title)
        json_file_name = clean_folder_name(self.config.find("metadata_file_name"))

        json_path = json_file_path / f"{json_file_name}.json"

        with open(json_path, "w", encoding="utf-8") as f:
            data = json.dumps(metadata,
                              indent=4,
                              ensure_ascii=GConfig.global_get("ensure_ascii", False))
            f.write(data)

    def _get_cover(self):
        cover_img = find_cover_url(self.series_html)
        if cover_img is None:
            return
        title = clean_folder_name(self.title)
        save_location = Path(self.project_root) / self.base_dl / self.download_folder_name / title
        save_location.mkdir(parents=True, exist_ok=True)
        ext = Path(cover_img).suffix or ".jpg"
        r = self.client.get_url(cover_img, mode="b")
        filename = save_location / f"cover{ext}"
        with open(filename, "wb") as f:
            f.write(r)
        log("Cover downloaded", "info")


def Weebcentral_main(url: str, mode: str):
    weebcentral = WeebCentral()
    match mode:
        case "series":
            weebcentral.download_series(url)
        case "chapter":
            weebcentral.download_one_chapter(url)
        case _:
            raise WeebCentralException.InvalidArgs
