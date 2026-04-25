import re

from bs4 import BeautifulSoup
from .exceptions import WeebCentralException

from utils import log


def title_from_chapter(soup: BeautifulSoup) -> str:
    top_nav = soup.select_one("section#nav-top")
    if top_nav is None:
        raise WeebCentralException("Top Nav not found, CSS selector: section#nav-top")

    a_tag = top_nav.select_one("a")

    if a_tag is None:
        raise WeebCentralException("Title not found, CSS selector: a")

    return a_tag.get_text(strip=True)


def chapter_name(soup: BeautifulSoup) -> str:
    top_nav = soup.select_one("section#nav-top")
    if top_nav is None:
        raise WeebCentralException("Top Nav not found, CSS selector: section#nav-top")

    chap_btn = top_nav.select_one("button[hx-target='#chapter-select-body']")
    if chap_btn is None:
        raise WeebCentralException("Chapter name not found, CSS selector: button[hx-target='#chapter-select-body']")

    chap_span = chap_btn.select_one("span")
    if chap_span is None:
        raise WeebCentralException("Could not find the chapter name span")

    return chap_span.get_text(strip=True)


def chapter_id(url: str) -> str:
    pattern = r"chapters\/([^/]+)"
    match = re.search(pattern, url)
    if match:
        chapter_id_ = match.group(1)
        return chapter_id_
    else:
        raise WeebCentralException.ChapterIdNotFound(url)


def image_src_of_chapter(html: str) -> list:
    soup = BeautifulSoup(html, "lxml")
    images = soup.find_all("img")
    chapter_urls = []

    for img in images:
        chapter_urls.append(img["src"])

    if chapter_urls:
        return chapter_urls
    else:
        raise WeebCentralException.ChapterImagesNotFound(html)


# series parsing

def title_from_series_page(soup: BeautifulSoup) -> str:
    title = soup.select_one("h1")
    if title is None:
        raise WeebCentralException("Title not found, CSS selector: h1")
    return title.get_text(strip=True)


def series_id(url: str) -> str:
    pattern = r"series\/([^/]+)"

    match = re.search(pattern, url)
    if match:
        series_id_ = match.group(1)
        return series_id_
    else:
        raise WeebCentralException.SeriesIdNotFound(url)


def all_chapter_href(html: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    raw_chapter_urls = soup.find_all("a")
    chapter_urls = []
    for url in raw_chapter_urls:
        if "/chapters/" in url["href"]:
            chapter_urls.append(url["href"])
    return chapter_urls


def cover_url(soup: BeautifulSoup) -> str | None:
    cover_tag = soup.select_one("section picture")
    if cover_tag is None:
        log(f"Cover Image was not found, but your download still continues", "warn")
        return None
    cover_ur_l = cover_tag.find("img")["src"]
    return cover_ur_l


def _parse_info(soup: BeautifulSoup,
                target: str,
                *,
                _list: bool = False,
                _selector: str = "a") -> str | list | None:
    li_tag = soup.select_one(
        f"section ul li:has(strong:-soup-contains('{target}'))"
    )

    if not li_tag:
        log(f"{target} was not found", "warn")
        return None
    items = [a.get_text(strip=True) for a in li_tag.find_all(_selector)]
    if _list:
        return items
    else:
        return ", ".join(items)


def author(soup: BeautifulSoup) -> str | None:
    return _parse_info(soup, "Author(s):")


def tags(soup: BeautifulSoup) -> list[str] | None:
    return _parse_info(soup, "Tags(s):", _list=True)


def status(soup: BeautifulSoup) -> str | None:
    return _parse_info(soup, "Status:")


def released_year(soup: BeautifulSoup) -> str | None:
    return _parse_info(soup, "Released:")


def is_official_translation(soup: BeautifulSoup) -> str | None:
    return _parse_info(soup, "Official Translation:")


def anime_adaptation(soup: BeautifulSoup) -> str | None:
    return _parse_info(soup, "Anime Adaptation:")


def comic_type(soup: BeautifulSoup) -> str | None:
    return _parse_info(soup, "Type:")


def is_adult_content(soup: BeautifulSoup) -> str | None:
    return _parse_info(soup, "Adult Content:")


def description(soup: BeautifulSoup) -> str | None:
    li_tag = soup.select_one(
        "section ul li:has(strong:-soup-contains('Description'))"
    )
    if not li_tag:
        log(f"Description was not found", "warn")
        return None

    paragraphs = [p.get_text(strip=True) for p in li_tag.find_all("p")]
    return " ,".join(paragraphs)
