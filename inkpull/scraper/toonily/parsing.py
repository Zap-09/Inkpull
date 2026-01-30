from bs4 import BeautifulSoup
from .exceptions import ToonilyException

from utils import log


def find_title_in_series(html: str, url: str) -> str:
    """ Get the title from the main page not the chapter page """
    soup = BeautifulSoup(html, "lxml")
    post_title = soup.select_one(".post-title")

    if not post_title:
        raise ToonilyException.ChapterBoxNotFound(url)

    for badge in post_title.select(".manga-title-badges"):
        badge.decompose()
    return post_title.get_text(strip=True)


def find_all_chapters_and_names(html: str, url: str) -> list[tuple]:
    """ Find all the chapters and names in the main page """
    soup = BeautifulSoup(html, "lxml")

    all_chapters = soup.select("li.wp-manga-chapter")
    if not all_chapters:
        raise ToonilyException.ChapterBoxNotFound(url)

    chapter_names = []
    for chapter in all_chapters:
        chapter_name = chapter.select_one("a").text
        chapter_href = chapter.select_one("a")["href"]
        chapter_names.append((chapter_name, chapter_href))
    chapter_names.reverse()
    return chapter_names


# Chapter specific parsing

def find_chapter_images_of_chapters(html: str, url: str) -> list[str]:
    """Find all the images of a chapter"""
    soup = BeautifulSoup(html, "lxml")
    reading_content = soup.select_one(".reading-content")

    if not reading_content:
        raise ToonilyException.ChapterBoxNotFound(url)

    images = []
    for image in reading_content.find_all("img"):
        images.append(image["src"])
    return images


def find_chapter_name_in_chapter(html: str, url: str) -> str:
    """ Find the series title of the chapter """
    soup = BeautifulSoup(html, "lxml")
    chapter_name = soup.select_one(".chapter-trigger").get_text(strip=True)
    if not chapter_name:
        raise ToonilyException.ChapterNameNotFound(url)
    return chapter_name


def find_title_in_chapter(html: str, url: str) -> str:
    """ Find the title of the chapter """
    soup = BeautifulSoup(html, "lxml")
    links = soup.select("ol.breadcrumb li a")

    if len(links) < 2:
        raise ToonilyException.TitleNameNotFoundInChapter(url)

    return links[1].get_text(strip=True)


# Metadata related parsing

def get_cover_image_url(html:str, url:str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    cover_box = soup.select_one(".summary_image")
    image = cover_box.select_one("img")
    if image:
        return image["src"]
    else:
        log(f"No cover image for '{url}'", "warn")
        return None



def get_series_tags(html: str, url: str) -> list[str] | None:
    """ Gets all the tags of the series """
    soup = BeautifulSoup(html, "lxml")
    tag_box = soup.select_one(".wp-manga-tags-list")
    tags = tag_box.select("a")

    tag_list = []
    for tag in tags:
        tag_list.append((tag.get_text(strip=True)).lstrip("#"))
    if not tag_list:
        log(f"No tags found. Series '{url}'", "warn")
        return None
    return tag_list


def _filter_manga_info(soup: BeautifulSoup, css_selector: str, selector_name: str, name: str) -> str | None:
    """ Helper fn for metadata parsing """
    target = soup.select_one(css_selector)

    if not target:
        log(f"{selector_name} was not found on '{name}'", "warn")
        return None
    else:
        return target.get_text(strip=True)


def get_series_genre(html: str, series_title: str) -> list[str] | None:
    """ Gets all the genres of the series """
    # Yes tags and Genre(s) are different in Toonily
    soup = BeautifulSoup(html, "lxml")

    genre_str = _filter_manga_info(
        soup,
        ".post-content_item:has(h5:-soup-contains('Genre(s)')) .summary-content",
        "Genre(s)",
        series_title
    )
    if not genre_str:
        return None

    genres = [g.strip() for g in genre_str.split(",") if g.strip()]
    return genres


def get_metadata(html: str, series_title: str) -> dict[str, str | None] | None:
    soup = BeautifulSoup(html, "lxml")

    alt_titles = _filter_manga_info(
        soup,
        ".post-content_item:has(h5:-soup-contains('Alt Name')) .summary-content",
        "Alt Name",
        series_title
    )

    writer = _filter_manga_info(
        soup,
        ".post-content_item:has(h5:-soup-contains('Writer(s)')) .summary-content",
        "Writer(s)",
        series_title
    )

    artist = _filter_manga_info(
        soup,
        ".post-content_item:has(h5:-soup-contains('Artist(s)')) .summary-content",
        "Artist(s)",
        series_title
    )
    return {
        "alt_titles": alt_titles,
        "writer": writer,
        "artist": artist
    }


def comic_status(html: str, series_title: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    status = _filter_manga_info(
        soup,
        ".post-content_item:has(h5:-soup-contains('Status')) .summary-content"
        ,
        "Status",
        series_title
    )
    status = status.lower()
    return str(status)

def gets_views_and_ratings(html: str, series_title: str) -> dict | None:
    """ Gets the view count and ratings of the series """

    soup = BeautifulSoup(html, "lxml")

    rating = _filter_manga_info(
        soup,
        "#averagerate",
        "Rating",
        series_title
    )

    views = _filter_manga_info(
        soup,
        ".manga-rate-view-comment .item:last-child",
        "View Count",
        series_title
    )
    return {
        "views": views,
        "rating": rating
    }


def get_summary(html: str, series_title: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    summary = _filter_manga_info(
        soup,
        ".summary__content",
        "Summary",
        series_title
    )
    return summary
