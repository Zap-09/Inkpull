import json
import re
from .exceptions import MangakatanaException
from bs4 import BeautifulSoup

from utils import log
from urllib.parse import urlparse, urlunparse


def get_image_src(html: str, url: str | None = None) -> list[str]:
    match = re.search(r"var thzq\s*=\s*(\[[^]]+])", html)
    if match:
        js_array = match.group(1)
        js_array = re.sub(r",\s*]", "]", js_array)
        js_array = js_array.replace("'", '"')

        return json.loads(js_array)

    raise MangakatanaException.ImageUrlsNotFound(url)


def get_comic_name(html: str, url: str | None = None) -> str:
    soup = BeautifulSoup(html, "lxml")

    breadcrumb_wrap = soup.select_one("div#breadcrumb_wrap")
    if not breadcrumb_wrap:
        raise MangakatanaException.ComicNameNotFound(url)

    breadcrumb_list = breadcrumb_wrap.select("li")

    comic_name = breadcrumb_list[1]
    return comic_name.text.strip()


def get_chapter_title(html: str, url: str | None = None) -> str | None:
    soup = BeautifulSoup(html, "lxml")

    breadcrumb_wrap = soup.select_one("div#breadcrumb_wrap")
    if not breadcrumb_wrap:
        raise MangakatanaException.ComicNameNotFound(url)

    breadcrumb_list = breadcrumb_wrap.select("li")

    chapter_name = breadcrumb_list[2]
    return chapter_name.text.strip()


def switch_server(url: str) -> str:
    parsed = urlparse(url)
    if parsed.query:
        return url

    path = parsed.path.rstrip("/")
    return str(urlunparse(parsed._replace(path=path, query="sv=3")))


# Series Mode parsing

def get_chapter_urls(html: str, url: str | None = None) -> list[str]:
    soup = BeautifulSoup(html, "lxml")

    raw_chapters_list = soup.select_one("div.chapters")
    if raw_chapters_list is None:
        raise MangakatanaException.ChapterUrlsNotFound(url)

    chapters = raw_chapters_list.select("div.chapter")
    if chapters is None:
        raise MangakatanaException.ChapterUrlsNotFound(raw_chapters_list)

    chapter_hrefs = []
    for ch in chapters:
        a = ch.select_one("a")
        chapter_hrefs.append(a["href"])

    chapter_hrefs.reverse()
    return chapter_hrefs


def get_series_name(html: str) -> str | None:
    try:
        soup = BeautifulSoup(html, "lxml")
        info = soup.select_one("div.info")
        return info.select_one("h1").text.strip()
    except Exception as e:
        raise MangakatanaException.SeriesNameNotFound(e)


def get_cover_url(html: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")

    single_book_div = soup.select_one("div#single_book")

    if single_book_div is None:
        return None

    cover_div = single_book_div.select_one("div.cover")
    if cover_div is None:
        return None
    cover_url = cover_div.select_one("img").get("src", None)
    return cover_url


def get_author(html: str) -> str | None:
    try:
        soup = BeautifulSoup(html, "lxml")
        author = soup.select_one("a.author").text.strip()
        return author
    except Exception:
        log(f"Author/Artist name was not found", "warn")
        return None


def get_alt_title(html: str) -> str | None:
    try:
        soup = BeautifulSoup(html, "lxml")
        alt_title = soup.select_one("div.alt_name").text.strip()
        return alt_title
    except Exception:
        log(f"Alt title was not found", "warn")
        return None


def get_tags(html: str) -> list[str | None]:
    soup = BeautifulSoup(html, "lxml")
    try:
        tag_section = soup.select_one("div.genres")

        a_tags = tag_section.select("a")

        all_tags = []
        for tag in a_tags:
            all_tags.append(tag.text.strip())
        return all_tags

    except Exception:
        log(f"Tags was not found", "warn")
        return []


def get_status(html: str) -> str | None:
    try:
        soup = BeautifulSoup(html, "lxml")
        info_box = soup.select_one("div.info")
        status = info_box.select_one("div.status").text.strip()
        return status
    except Exception:
        log(f"Comic status was not found", "warn")
        return None


def get_description(html: str) -> str | None:
    try:
        soup = BeautifulSoup(html, "lxml")
        summary_box = soup.select_one("div.summary")
        summary_text = summary_box.select_one("p").text.strip()
        return summary_text
    except Exception:
        log(f"Comic description was not found", "warn")
        return None
