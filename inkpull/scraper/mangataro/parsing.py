from utils import log
from bs4 import BeautifulSoup

from .exceptions import MangaTatoException


def chapter_id(url: str) -> str:
    last_part = url.rsplit("/", 1)[-1]
    if not "-" in last_part:
        raise MangaTatoException(f"Chapter ID not found in url. {url}")
    return last_part.split("-")[-1]


def comic_title_from_chapter(soup: BeautifulSoup) -> str:
    sticky_navbar = soup.select_one("div#sticky-navbar")

    a_tag = sticky_navbar.select_one("a")
    if a_tag:
        return a_tag.get_text(strip=True)
    raise MangaTatoException("Chapter name was not found.")


def chapter_name_from_chapter(soup: BeautifulSoup) -> str:
    chapter_sections = soup.select_one("select#chapter-select")
    if not chapter_sections:
        raise MangaTatoException("Chapter section not found.")

    chapter_name = chapter_sections.select_one("option[selected]")
    if not chapter_name:
        raise MangaTatoException("Chapter name was not found. CSS selector: option[selected]")

    return chapter_name.get_text(strip=True)


def image_urls(json_data: dict) -> list:
    image_list = json_data.get("images")
    if isinstance(image_list, list):
        return image_list
    else:
        raise MangaTatoException.ImageSrcListNotFound(json_data)


# series mode parsing

def manga_id(soup: BeautifulSoup) -> int:
    body = soup.select_one("body")
    if not body:
        raise MangaTatoException("Body not found in html")

    manga_id_ = body.get("data-manga-id")
    if not manga_id_:
        raise MangaTatoException("Manga id not found in html tag.")

    return int(manga_id_)


def comic_title(soup: BeautifulSoup) -> str:
    selector = "h1.text-2xl.lg\\:text-3xl.xl\\:text-4xl.font-bold.text-neutral-100.tracking-tight.mb-1"
    title_div = soup.select_one(selector)

    if not title_div:
        raise MangaTatoException(
            "Comic title not found. CSS selector:\n \"h1.text-2xl.lg\\:text-3xl.xl\\:text-4xl.font-bold.text-neutral-100.tracking-tight.mb-1\"")
    return title_div.text.strip()


def parse_chapter_urls(json_data: list | None) -> list:
    if json_data is None:
        raise MangaTatoException("Chapter list not found")

    chapter_link: list = []
    for items in json_data:
        url = items.get("url")
        if url:
            chapter_link.append(url)

    if len(chapter_link) < 0:
        raise MangaTatoException("Chapter list is less than 1")

    return chapter_link


def alt_title(soup: BeautifulSoup) -> str:
    alt_title_section = soup.select_one("p.text-sm.text-neutral-400.mb-3.sm\\:mb-4")

    if not alt_title_section:
        log("Alternative title not found", "warn")
        return ""

    return alt_title_section.text.strip()


def author_and_artist(soup: BeautifulSoup) -> str:
    author_div = soup.select_one("div.text-sm.text-neutral-200")
    if not author_div:
        log("Could not find author and artist", "warn")

    return author_div.text.strip()


def tags(soup: BeautifulSoup) -> list:
    tag_div = soup.select_one("div.flex.flex-wrap.gap-1\\.5.sm\\:gap-2")
    if not tag_div:
        log("Could not find tag div, returning empty list ", "warn")
        return []

    raw_tags = tag_div.text

    if not raw_tags:
        log("No tags found, returning empty list ", "warn")
        return []

    return raw_tags.strip().split()


def description(soup: BeautifulSoup) -> str:
    p_tags = soup.select_one("div#description-content-tab")
    if not p_tags:
        log("No description found, returning empty string", "warn")
        return ""
    return p_tags.text.strip()


def comic_status(soup: BeautifulSoup) -> str:
    info_section = soup.select_one("div.flex.flex-wrap.gap-x-4.gap-y-2.text-sm.text-neutral-300.mb-3.sm\\:mb-4")
    if not info_section:
        log("Could not find info section, setting comic status to 'Unknown'", "warn")
        return "unknown"

    info = info_section.text.strip()
    try:
        status = info.split()[1]
        match status.lower():
            case "ongoing":
                return "ongoing"
            case "completed":
                return "completed"
            case _:
                return "unknown"
    except IndexError:
        return "Unknown"


def cover_image(soup: BeautifulSoup) -> str:
    cover_img = soup.select_one("img.w-full.h-auto.aspect-\\[2\\/3\\].object-cover")
    if not cover_img:
        log("Could not find cover image", "warn")
        return ""
    return cover_img.get("src")
