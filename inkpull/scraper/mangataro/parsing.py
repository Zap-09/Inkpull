import re

from utils import log
from bs4 import BeautifulSoup

from .exceptions import MangaTatoException


def find_chapter_id(url: str) -> str:
    last_part = url.rsplit("/", 1)[-1]
    if not "-" in last_part:
        raise MangaTatoException.ChapterIdNotFound(url)
    return last_part.split("-")[-1]


def find_title_chapter_name(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "lxml")
    reader_tag = soup.select_one("#reader-media")
    if not reader_tag:
        raise MangaTatoException.TitleNotFound(html)

    chapter_title = reader_tag.get("data-chapter-title")

    if not chapter_title:
        raise MangaTatoException.TitleNotFound(html)

    match = re.search(r'Chapter \d+(?:\.\d+)?(?:\s*-\s*.+)?$', chapter_title)
    if match:
        chapter_label = match.group(0)
        title = chapter_title[:match.start()].strip()
        return title, chapter_label
    else:
        raise MangaTatoException.TitleNotFound(chapter_title)


def get_image_urls(json_data: dict) -> list:
    image_list = json_data.get("images")
    if isinstance(image_list, list):
        return image_list
    else:
        raise MangaTatoException.ImageSrcListNotFound(json_data)


# series mode parsing

def get_manga_id(html: str) -> int:
    soup = BeautifulSoup(html, "lxml")
    body = soup.select_one("body")
    if not body:
        raise MangaTatoException.BodyNotFoundInHtml(html)

    manga_id = body.get("data-manga-id")
    if not manga_id:
        raise MangaTatoException.MangaIdNotFound(html)

    return int(manga_id)


def parse_chapter_urls(info: list | None) -> list:
    if info is None:
        raise MangaTatoException.ChapterUrlNotFound()

    chapter_link: list = []
    for items in info:
        url = items.get("url")
        if url:
            chapter_link.append(url)

    if len(chapter_link) < 0:
        raise MangaTatoException.ChapterUrlNotFound()

    return chapter_link


def get_title(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    selector = "h1.text-2xl.lg\\:text-3xl.xl\\:text-4xl.font-bold.text-neutral-100.tracking-tight.mb-1"
    title_div = soup.select_one(selector)

    if not title_div:
        log("No title found, returning empty string ", "warn")
        return ""
    return title_div.text.strip()


def find_cover_image(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    cover_img = soup.select_one("img.w-full.h-auto.aspect-\\[2\\/3\\].object-cover")
    if not cover_img:
        log("Could not find cover image", "warn")
        return ""
    return cover_img.get("src")


def find_author_and_artist(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    author_div = soup.select_one("div.text-sm.text-neutral-200")
    if not author_div:
        log("Could not find author and artist", "warn")

    return author_div.text.strip()


def get_alt_title(html: str):
    soup = BeautifulSoup(html, "lxml")
    alt_title_section = soup.select_one("p.text-sm.text-neutral-400.mb-3.sm\\:mb-4")

    if not alt_title_section:
        log("Alternative title not found", "warn")
        return ""

    return alt_title_section.text.strip()


def get_tags(html: str) -> list:
    soup = BeautifulSoup(html, "lxml")

    tag_div = soup.select_one("div.flex.flex-wrap.gap-1\\.5.sm\\:gap-2")
    if not tag_div:
        log("Could not find tag div, returning empty list ", "warn")
        return []

    raw_tags = tag_div.text

    if not raw_tags:
        log("No tags found, returning empty list ", "warn")
        return []

    return raw_tags.strip().split()


def find_description(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    p_tags = soup.select_one("div#description-content-tab")
    if not p_tags:
        log("No description found, returning empty string", "warn")
        return ""
    return p_tags.text.strip()


def comic_status(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
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
