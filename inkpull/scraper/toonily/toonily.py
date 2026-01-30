import asyncio
from pathlib import Path
import json
from utils import clean_folder_name, log, remove_dupes_in_list, find_project_root, mihon_style

# base
from ...base.downloader import ImageDownloader
from ...base.http_client import HttpClient

# global config
from ...config import GConfig

# toonily module imports
from .exceptions import ToonilyException
from .config import ToonilyConfig
from .parsing import (find_title_in_series,
                      find_all_chapters_and_names,
                      find_chapter_images_of_chapters,
                      find_chapter_name_in_chapter,
                      find_title_in_chapter,
                      get_series_tags,
                      get_series_genre,
                      get_metadata,
                      gets_views_and_ratings,
                      get_summary,
                      comic_status,
                      get_cover_image_url)


class Toonily:
    def __init__(self, headers=None, cookies=None):
        # ------configs------ #
        self.project_root = find_project_root()
        self.config = ToonilyConfig()

        self.headers = headers or self.config.find("headers", None)
        self.cookie = cookies or self.config.find("cookies", None)
        self.base_dl = GConfig.global_get("Download_location")
        self.download_folder_name = self.config.find("download_folder")

        # ------clients------ #
        self.client = HttpClient(self.headers,
                                 impersonate=self.config.find("impersonate_browser"),
                                 cookie=self.cookie)
        self.downloader = ImageDownloader(headers=self.headers)
        # ------metadata------ #
        self.series_html = None
        self.series_title = None

    async def _download_series_helper(self, url: str):
        """ Helper function to download the series """
        html = self.client.get_url(url, mode="t")
        self.series_html = html
        title = find_title_in_series(html, url)
        self.series_title = title
        title = clean_folder_name(title)

        log(f"Download Started for: {title}", "info")
        chapters: list = find_all_chapters_and_names(html, url)
        self.make_metadata_file()
        self._get_cover()

        for c_name, c_url in chapters:
            try:
                chapter_html = self.client.get_url(c_url, mode="t")
                image_src_list = find_chapter_images_of_chapters(chapter_html, c_url)

                c_name = clean_folder_name(c_name)

                output_dir = (Path(self.project_root) /
                              self.base_dl /
                              self.download_folder_name /
                              title /
                              c_name)

                await self.downloader.download_concurrently(
                    urls=image_src_list,
                    output_dir=output_dir,
                )

            except ToonilyException as te:
                log(f"Failed to download {c_name} error: {str(te)}", "error")

            except Exception as e:
                log(f"Failed to download {c_name} error: {str(e)}", "error")
        log("Download Finished", "info")

    def download_series(self, url: str):
        """ Downloads the entire series """
        asyncio.run(self._download_series_helper(url))

    def download_one_chapter(self, url: str):
        """ Downloads a single chapter """
        html = self.client.get_url(url, mode="t")
        chapter_name = clean_folder_name(find_chapter_name_in_chapter(html, url))

        title = find_title_in_chapter(html, url)
        log(f"Download Started for: {title}", "info")

        chapter_images = find_chapter_images_of_chapters(html, url)
        output_dir = (Path(self.project_root) / self.base_dl /
                      self.download_folder_name /
                      clean_folder_name(title) /
                      chapter_name)

        asyncio.run(
            self.downloader.download_concurrently(
                urls=chapter_images,
                output_dir=str(output_dir))
        )
        log("Download Finished", "info")

    def _get_cover(self):
        cover_img = get_cover_image_url(self.series_html, self.series_title)
        if cover_img is None:
            return
        title = clean_folder_name(self.series_title)
        save_location = Path(self.project_root) / self.base_dl / self.download_folder_name / title
        save_location.mkdir(parents=True, exist_ok=True)

        ext = Path(cover_img).suffix or ".jpg"
        r = self.client.get_url(cover_img, mode="b")
        filename = save_location / f"cover{ext}"
        with open(filename, "wb") as img:
            img.write(r)
        log("Cover downloaded", "info")

    def make_metadata_file(self):
        html = self.series_html
        title = self.series_title
        tags: list = get_series_tags(html, title)
        genres: list = get_series_genre(html, title)
        other_mata_data: dict = get_metadata(html, title)
        tags_genre = remove_dupes_in_list(tags, genres)
        status = comic_status(html, title)
        view_and_rating = gets_views_and_ratings(html, title)
        views = view_and_rating.get("views", None)
        rating = float(view_and_rating.get("rating", None))
        summary = get_summary(html, title)
        alt_title = other_mata_data.get("alt_titles", None)

        if alt_title:
            alt_title = f"Alternative Titles: {alt_title}\n"
        else:
            alt_title = ""

        metadata = mihon_style(
            title=title,
            author=other_mata_data.get("writer", None),
            artist=other_mata_data.get("artist", None),
            tags= tags_genre,
            status=status,
            description= summary,
            other_info=(
                alt_title,
                f"Rating: {str(rating)}\nViews: {views}",
            )
        )
        json_location = Path(self.project_root) / self.base_dl / self.download_folder_name / title
        json_location.mkdir(parents=True, exist_ok=True)

        json_file_name = clean_folder_name(self.config.find("metadata_file_name"))

        json_path = json_location / f"{json_file_name}.json"

        with open(json_path, "w", encoding="utf-8") as f:
            data = json.dumps(metadata,
                              indent=4,
                              ensure_ascii=GConfig.global_get("ensure_ascii", False))
            f.write(data)


def Toonily_main(url: str, mode: str):
    if not url:
        raise ToonilyException.UrlNotProvided

    toonily = Toonily()
    match mode:
        case "series":
            toonily.download_series(url)
        case "chapter":
            toonily.download_one_chapter(url)
        case _:
            raise ToonilyException.InvalidArgs
