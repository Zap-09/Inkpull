import asyncio
from utils import log, user_confirmation, GenericException
from ...base.base_template import BaseTemplate

# base
from ...base.downloader import ImageDownloader
from ...base.http_client import HttpClient

# atsumaru module imports
from .config import AtsumaruConfig
from . import parsing


class Atsumaru(BaseTemplate):
    def __init__(self, headers=None, cookies=None):
        config = AtsumaruConfig()
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

        self.series_info: dict | None = None
        self.series_title: str | None = None

    def _get_info(self, manga_id: str) -> dict:
        if self.series_info is None:
            self.series_info = self.client.get_url(f"https://atsu.moe/api/manga/page?id={manga_id}", "j")

        return self.series_info

    async def _download_one_chapter(self, url: str) -> None:
        try:
            url = parsing.clean_url(url)
        except Exception as e:
            log(str(e), "error", _noformat=True)
            log("An error occurred, skipping this entry", level="warn")
            return

        manga_id, chapter_id = parsing.get_manga_chapter_id(url)

        api = f"https://atsu.moe/api/read/chapter?mangaId={manga_id}&chapterId={chapter_id}"
        cha_res = self.client.get_url(api, "j")

        image_urls = parsing.make_image_url(cha_res)

        self._get_info(manga_id)

        title = parsing.get_title(self.series_info, _only_title=True).get("title")
        chapter_name = parsing.get_chapter_name(cha_res)

        output_dir = self.sanitize_path(
            self.site_download_folder / title / chapter_name,
        )

        await self.downloader.download_images_concurrently(
            image_urls, output_dir=output_dir
        )

    def download_one_chapter(self, url: str) -> None:
        asyncio.run(
            self._download_one_chapter(url)
        )

    def _resolve_scanlation(self, scan_group: str | None) -> str | None:
        scan_warn = self.Config.find("scan_group_warn", True)
        scan_groups: dict = self.Config.find("scan_group", {})

        if scan_group:
            picked = scan_groups.get(scan_group)

            if not picked:
                log(f"{scan_group} is not in the config", "warn")
                if not user_confirmation("Download from all scan groups?"):
                    raise GenericException.UserRejection
                return None

            return picked

        if scan_warn:
            if not user_confirmation(
                    "No scan group selected. Download from all available scan groups?"
            ):
                raise GenericException.UserRejection
            log("Tip: you can disable this prompt in the config")

        return None

    async def _download_series(self, url: str, scan_group: str | None = None) -> None:
        manga_id = parsing.get_manga_id(url)

        chapter_list_api = f"https://atsu.moe/api/manga/allChapters?mangaId={manga_id}"
        api_res = self.client.get_url(chapter_list_api, "j")

        scanlation_id = self._resolve_scanlation(scan_group)

        self._get_info(manga_id)
        title = parsing.get_title(self.series_info, _only_title=True).get("title")

        self._save_metadata()

        log(f"Download started for: {title}", "info")

        cover_url = parsing.get_poster_url(self.series_info)
        if not cover_url:
            log(f"Could not find cover image", "warn")

        cover_res = self.client.get_url(cover_url, "b")
        cover_save_location = self.site_download_folder / title
        self.save_cover(
            cover_url=cover_url,
            save_location=cover_save_location,
            cover_bytes=cover_res
        )

        chapter_list = parsing.make_chapter_urls(manga_id, api_res, scanlation_id)
        chapter_list.reverse()
        for chapter in chapter_list:
            try:
                await self._download_one_chapter(chapter)
            except Exception as e:
                log(f"Error downloading chapter: {chapter}, Error:{e}", "error")

    def _save_metadata(self):
        all_titles = parsing.get_title(self.series_info, _only_title=False)
        title = all_titles.get("title")
        other_titles = all_titles.get("otherNames", None)
        tags = parsing.get_tags(self.series_info)
        author = parsing.get_authors(self.series_info)
        artist = author
        status = parsing.get_status(self.series_info)
        comic_type = parsing.get_comic_type(self.series_info)
        synopsis = parsing.get_synopsis(self.series_info)
        tags.append(comic_type)

        metadata = self.generate_metadata(
            title=title,
            author=author,
            artist=artist,
            tags=tags,
            description=synopsis,
            status=status,
            alternative_titles = other_titles,
        )

        metadata_file_path = self.site_download_folder / title
        self.create_metadata_file(
            file_path=self.sanitize_path(metadata_file_path),
            data=metadata
        )

    def download_series(self, url: str, scan_group: str | None):
        asyncio.run(
            self._download_series(url, scan_group)
        )


def Atsumaru_main(url: str, mode: str, scan_group: str | None):
    if not url:
        raise Exception("url is required")
    atsumaru = Atsumaru()
    match mode:
        case "chapter":
            atsumaru.download_one_chapter(url)
        case "series":
            atsumaru.download_series(url, scan_group)
        case _:
            log("Invalid mode", "error")
