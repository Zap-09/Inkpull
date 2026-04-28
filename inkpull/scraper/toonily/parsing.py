import re
from bs4 import BeautifulSoup
from .exceptions import ToonilyException

from utils import log


def chapter_name(html: BeautifulSoup) -> str:
    title = html.select_one("ol.breadcrumb li.active")
    if title is None:
        raise ToonilyException("Could not find chapter name")

    return title.get_text(strip=True)


def comic_name(html: BeautifulSoup) -> str:
    breadcrumb = html.select_one("ol.breadcrumb")
    if breadcrumb is None:
        raise ToonilyException(
            f"Chapter name was not found because breadcrumb is missing. CSS selector: 'ol.breadcrumb'")

    list_items = breadcrumb.select("li a")
    if not list_items:
        raise ToonilyException(
            f"Chapter name was not found because breadcrumb is missing. CSS selector: 'li a'")

    return list_items[-1].get_text(strip=True)


def chapter_images(html: BeautifulSoup) -> list[str]:
    chapter_content = html.select_one("div.reading-content")
    if chapter_content is None:
        raise ToonilyException(
            "Chapter images not found because chapter_content is missing. CSS selector: 'div.reading-content'")

    images = chapter_content.select("img")

    images_src = []
    for item in images:
        src = item["src"]
        images_src.append(src)

    return images_src

#serirs parsing
def chapter_list(html: BeautifulSoup) -> list[str]:
    manga_content = html.select_one("div#manga-content-tabs")
    if manga_content is None:
        raise ToonilyException("Chapter section not found. CSS selector: '#manga-content-tabs'")

    chapters = manga_content.select("li.wp-manga-chapter")

    chapters_href = []
    for chapter in chapters:
        a_tag = chapter.select_one("a")
        chapters_href.append(a_tag["href"])

    chapters_href.reverse()
    return chapters_href


def series_title(html: BeautifulSoup) -> str:
    h1 = html.select_one("h1")
    name = h1.find(string=True, recursive=False).strip()
    if name:
        return name
    else:
        raise ToonilyException(f"Series title not found.")


def cover_src(html: BeautifulSoup) -> str | None:
    cover_box = html.select_one("div.summary_image")
    if cover_box is None:
        log(f"Cover box was not found", "error")
        return None
    return cover_box.select_one("img")["src"]


def _filter_manga_info(soup: BeautifulSoup,
                       css_selector: str,
                       selector_name: str,
                       ) -> str | None:
    """ Helper fn for metadata parsing """
    target = soup.select_one(css_selector)

    if not target:
        log(f"{selector_name} was not found.", "warn")
        return None
    else:
        return target.get_text(strip=True, separator=" ")  # type: ignore


def alternative_titles(html: BeautifulSoup) -> str | None:
    alt_titles = _filter_manga_info(
        html,
        ".post-content_item:has(h5:-soup-contains('Alt Name')) .summary-content",
        "Alt Name",
    )
    return alt_titles


def authors(html: BeautifulSoup) -> str | None:
    author_ = _filter_manga_info(
        html,
        ".post-content_item:has(h5:-soup-contains('Writer(s)')) .summary-content",
        "Writer(s)",
    )
    return author_ if author_ else None


def artist(html: BeautifulSoup) -> str | None:
    artist_ = _filter_manga_info(
        html,
        ".post-content_item:has(h5:-soup-contains('Artist(s)')) .summary-content",
        "Artist(s)",
    )
    return artist_ if artist_ else None


def description(html: BeautifulSoup) -> str:
    target = html.select_one(".summary__content")

    if not target:
        return ""

    paragraphs = []

    for p in target.find_all("p"):
        text = p.get_text(separator=" ", strip=True)  # type:ignore

        if not text:
            continue

        text = re.sub(r"\s+,", ",", text)
        text = re.sub(r"\s+\.", ".", text)
        text = re.sub(r"\s{2,}", " ", text)

        paragraphs.append(text.strip())

    if not paragraphs:
        return target.get_text(separator=" ", strip=True)  # type:ignore

    return "\n\n".join(paragraphs)


def comic_status(html: BeautifulSoup) -> str | None:
    status_ = _filter_manga_info(
        html,
        ".post-content_item:has(h5:-soup-contains('Status')) .summary-content",
        "Status",
    )
    return status_ if status_ else None


def rating(html: BeautifulSoup) -> str:
    rating_ = _filter_manga_info(
        html,
        "#averagerate",
        "Rating",
    )
    return rating_ if rating_ else "0.0"


def view_count(html: BeautifulSoup) -> str | None:
    views = _filter_manga_info(
        html,
        ".manga-rate-view-comment .item:last-child",
        "Views Count",
    )
    return views if views else None


def genres(html: BeautifulSoup) -> list[str]:
    genre_str = _filter_manga_info(
        html,
        ".post-content_item:has(h5:-soup-contains('Genre(s)')) .summary-content",
        "Genre(s)"
    )
    if not genre_str:
        return []

    genres_ = [g.strip() for g in genre_str.split(",") if g.strip()]
    return genres_


def tags(html: BeautifulSoup) -> list[str]:
    tag_box = html.select_one(".wp-manga-tags-list")
    tags_ = tag_box.select("a")

    tag_list = []
    for tag in tags_:
        tag_list.append((tag.get_text(strip=True)).lstrip("#"))
    return tag_list
