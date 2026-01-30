import re

from bs4 import BeautifulSoup
from .exceptions import WeebCentralException

from utils import log


def find_series_id(text: str) -> str:
    pattern = r"series\/([^/]+)"

    match = re.search(pattern, text)
    if match:
        series_id = match.group(1)
        return series_id
    else:
        raise WeebCentralException.SeriesIdNotFound(text)


def find_chapter_id(url: str) -> str:
    pattern = r"chapters\/([^/]+)"
    match = re.search(pattern, url)
    if match:
        chapter_id = match.group(1)
        return chapter_id
    else:
        raise WeebCentralException.ChapterIdNotFound(url)


def find_all_chapter_href(html: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    raw_chapter_urls = soup.find_all("a")
    chapter_urls = []
    for url in raw_chapter_urls:
        if "/chapters/" in url["href"]:
            chapter_urls.append(url["href"])
    return chapter_urls


def find_all_src_of_chapter(html: str) -> list:
    soup = BeautifulSoup(html, "lxml")
    images = soup.find_all("img")
    chapter_urls = []

    for img in images:
        chapter_urls.append(img["src"])

    if chapter_urls:
        return chapter_urls
    else:
        raise WeebCentralException.ChapterImagesNotFound(html)


def find_title_and_chapter_name(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "lxml")
    title_tag = soup.select_one("title")

    if title_tag is None:
        raise WeebCentralException.TitleAndChapterNotFound(html)
    parts = [i.strip() for i in title_tag.text.split("|")]

    if len(parts) < 2:
        raise WeebCentralException.TitleAndChapterNotFound(html)

    chapter = parts[0]
    title = parts[1]
    return title, chapter


def find_title(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    title_tag = soup.select_one("title")
    if title_tag is None:
        raise WeebCentralException.TitleNotFound(html)

    parts = [i.strip() for i in title_tag.text.split("|")]
    if len(parts) < 1:
        raise WeebCentralException.TitleNotFound(html)
    title = parts[0]
    return title


def find_cover_url(html: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    cover_tag = soup.select_one("section picture")
    if cover_tag is None:
        log(f"Cover Image was not found, but your download still continues", "warn")
        return None
    cover_url = cover_tag.find("img")["src"]
    return cover_url



def parse_info(html: str,
               target: str,
               series_name: str,
               *,
               _list: bool = False,
               _selector: str = "a") -> str | list | None:
    soup = BeautifulSoup(html, "lxml")
    li_tag = soup.select_one(
        f"section ul li:has(strong:-soup-contains('{target}'))"
    )

    if not li_tag:
        log(f"{target} was not found on '{series_name}'", "warn")
        return None
    items = [a.get_text(strip=True) for a in li_tag.find_all(_selector)]
    if _list:
        return items
    else:
        return ", ".join(items)


def get_description(html:str,series_name: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")

    li_tag = soup.select_one(
        "section ul li:has(strong:-soup-contains('Description'))"
    )
    if not li_tag:
        log(f"Description was not found on '{series_name}'", "warn")
        return None

    paragraphs = [p.get_text(strip=True) for p in li_tag.find_all("p")]
    return " ,".join(paragraphs)

