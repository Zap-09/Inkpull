import asyncio
from utils import log
from ...base.base_template import BaseTemplate

# base
from ...base.downloader import ImageDownloader
from ...base.http_client import HttpClient

# atsumaru module imports
from .config import AtsumaruConfig
from . import parsing

from .schemas import AtsumaruChapter


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

    async def _series_single_chapter(self, manga_id: str, title: str, chapter: AtsumaruChapter):
        api = f"https://atsu.moe/api/read/chapter?mangaId={manga_id}&chapterId={chapter.id}"
        cha_res = self.client.get_url(api, "j")
        image_urls = parsing.make_image_url(cha_res)
        self._get_info(manga_id)

        chapter_name = f"{chapter.title} - ({chapter.scanlationGroupName})"

        output_dir = self.sanitize_path(
            self.site_download_folder / title / chapter_name,
        )
        await self.downloader.download_images_concurrently(
            image_urls, output_dir=output_dir
        )

    async def _download_series(self, url: str,
                               *,
                               select_all: bool = False,
                               smart_select: bool = False):
        manga_id = parsing.get_manga_id(url)
        chapter_list_api = f"https://atsu.moe/api/manga/allChapters?mangaId={manga_id}"
        self._get_info(manga_id)

        chapter_api_res = self.client.get_url(chapter_list_api, "j")

        scanlators_and_chapters = parsing.extract_scanlators(
            all_chapter_json=chapter_api_res,
            page_json=self.series_info
        )
        selected_chapters = parsing.resolve_selection(
            scanlators=scanlators_and_chapters, select_all=select_all, smart_select=smart_select
        )

        chapters_with_urls = parsing.construct_chapter_urls(
            manga_id=manga_id,
            data=selected_chapters
        )

        self._save_metadata()
        title = parsing.get_title(self.series_info, _only_title=True).get("title")

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

        try:
            for chapter in chapters_with_urls:
                await self._series_single_chapter(
                    manga_id=manga_id, chapter=chapter, title=title
                )
        except Exception as e:
            log(str(e), "error")

    def download_series(self, url: str,
                        *,
                        select_all: bool = False,
                        smart_select: bool = False):
        asyncio.run(self._download_series(
            url=url, smart_select=smart_select, select_all=select_all
        ))

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
            alternative_titles=other_titles,
        )

        metadata_file_path = self.site_download_folder / title
        self.create_metadata_file(
            file_path=self.sanitize_path(metadata_file_path),
            data=metadata
        )


def Atsumaru_main(url: str, mode: str, select_all: bool = False, smart_select: bool = False):
    if not url:
        raise Exception("url is required")
    atsumaru = Atsumaru()
    match mode:
        case "chapter":
            atsumaru.download_one_chapter(url)
        case "series":
            atsumaru.download_series(url, select_all=select_all, smart_select=smart_select)
        case _:
            log("Invalid mode", "error")
