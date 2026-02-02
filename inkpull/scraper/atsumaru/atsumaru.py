import asyncio
import json
from pathlib import Path
from utils import clean_folder_name, log, find_project_root, mihon_style, user_confirmation, GenericException

# base
from ...base.downloader import ImageDownloader
from ...base.http_client import HttpClient

# global config
from ...config import GConfig

# atsumaru module imports
from .config import AtsumaruConfig
from .parsing import (get_manga_chapter_id, make_image_url, get_title, get_chapter_name, clean_url, get_manga_id,
                      make_chapter_urls, get_authors, get_tags, get_status, get_comic_type, get_synopsis,
                      get_poster_url)


class Atsumaru:
    def __init__(self, headers=None, cookies=None):
        # ------configs------ #
        self.project_root = find_project_root()
        self.config = AtsumaruConfig()

        self.headers = headers or self.config.find("headers", None)
        self.cookie = cookies or self.config.find("cookies", None)
        self.base_dl = find_project_root() / GConfig.global_get("Download_location")
        self.download_folder_name = self.config.find("download_folder")

        # ------clients------ #
        self.client = HttpClient(self.headers,
                                 impersonate=self.config.find("impersonate_browser"),
                                 cookie=self.cookie)
        self.downloader = ImageDownloader(headers=self.headers)
        # ------metadata------ #
        self.series_info = None
        self.series_title = None

    def _get_info(self, manga_id):
        if self.series_info is None:
            self.series_info = self.client.get_url(f"https://atsu.moe/api/manga/page?id={manga_id}"
                                                   , "j")
        return self.series_info

    async def _download_one_chapter(self, url: str):
        url = clean_url(url)
        manga_id, chapter_id = get_manga_chapter_id(url)
        api = f"https://atsu.moe/api/read/chapter?mangaId={manga_id}&chapterId={chapter_id}"
        cha_res = self.client.get_url(api, "j")
        image_urls = make_image_url(cha_res)

        self._get_info(manga_id)

        title = get_title(self.series_info, _only_title=True).get("title")

        chapter_name = get_chapter_name(cha_res)

        output_dir = (self.base_dl /
                      self.download_folder_name /
                      clean_folder_name(title) /
                      clean_folder_name(chapter_name)
                      )
        await self.downloader.download_concurrently(image_urls, output_dir=output_dir)

    def download_one_chapter(self, url):
        asyncio.run(
            self._download_one_chapter(url)
        )

    async def _download_series(self, url, scan_group: None | str = None):
        manga_id = get_manga_id(url)
        chapter_list_api = f"https://atsu.moe/api/manga/allChapters?mangaId={manga_id}"
        api_res = self.client.get_url(chapter_list_api, "j")
        scanlation_id = None
        scan_warn = self.config.find("scan_group_warn", True)

        if scan_group is not None:
            scan_groups: dict = self.config.find("scan_group", {})
            picked_group = scan_groups.get(scan_group, None)
            if picked_group is None:
                log(f"{scan_group} is not in the config", "warn")
                if not user_confirmation("Do you wanna download from all scan groups?"):
                    raise GenericException.UserRejection
                else:
                    scanlation_id = None
            else:
                scanlation_id = picked_group
        else:
            if scan_warn:
                if not user_confirmation(
                        "Looks like no scan groups was selected, download from all available scan groups?"):
                    raise GenericException.UserRejection
                else:
                    log("Tip you can hide this prompt completely in the config")

        self._get_info(manga_id)
        title = get_title(self.series_info, _only_title=True).get("title")
        self.make_metadata_file()

        log(f"Download started for: {title}")
        self._get_cover()
        chapter_list = make_chapter_urls(manga_id, api_res, scanlation_id)
        chapter_list.reverse()
        for chapter in chapter_list:
            try:
                await self._download_one_chapter(chapter)
            except Exception as e:
                log(f"Error downloading chapter: {chapter}, Error:{e}", "error")

    def download_series(self, url, scan_group):
        asyncio.run(
            self._download_series(url, scan_group)
        )

    def make_metadata_file(self):
        all_titles = get_title(self.series_info, _only_title=False)

        title = all_titles.get("title")
        other_titles = all_titles.get("otherNames", None)
        tags = get_tags(self.series_info)
        author = get_authors(self.series_info)
        status = get_status(self.series_info)
        comic_type = get_comic_type(self.series_info)
        synopsis = get_synopsis(self.series_info)

        metadata = mihon_style(
            title=title,
            artist=str(author),
            author=str(author),
            tags=tags.append(comic_type),
            description=synopsis,
            status=status,
            other_info=(
                f"Other Titles: {other_titles}",
            )
        )

        json_file_path = self.base_dl / self.download_folder_name / clean_folder_name(title)
        json_file_path.mkdir(exist_ok=True, parents=True)
        json_file_name = clean_folder_name(self.config.find("metadata_file_name"))
        json_path = json_file_path / f"{json_file_name}.json"
        with open(json_path, "w") as f:
            data = json.dumps(metadata,
                              indent=4,
                              ensure_ascii=GConfig.global_get("ensure_ascii", False))
            f.write(data)

    def _get_cover(self):
        url = get_poster_url(self.series_info)

        if not url:
            return
        title = get_title(self.series_info, _only_title=True).get("title")

        ext = Path(url).suffix or ".jpg"
        res = self.client.get_url(url, "b")
        save_folder = self.base_dl / self.download_folder_name / title
        save_folder.mkdir(exist_ok=True, parents=True)

        file_name = save_folder / f"Cover{ext}"
        with open(file_name, "wb") as f:
            f.write(res)
        log("Cover Downloaded", "info")


def Atsumaru_main(url: str, mode: str, scan_group: str):
    if not url:
        raise Exception("url is required")
    atsumaru = Atsumaru()
    match mode:
        case "chapter":
            atsumaru.download_one_chapter(url)
        case "series":
            atsumaru.download_series(url, scan_group)
        case _:
            log("Invalid mode")
