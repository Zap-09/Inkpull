from utils import log
from .exceptions import AtsumaruException


def clean_url(url: str) -> str:
    c_url = url.split("#", 1)[0]
    return c_url


def get_manga_chapter_id(text: str) -> tuple[str, str]:
    try:
        text = text.rstrip("/")
        parsed_url = tuple(text.rsplit("/", 2))
        manga_id = parsed_url[1]
        chapter_id = parsed_url[2]
        return manga_id, chapter_id
    except Exception:
        raise AtsumaruException.MangaAndChapterIDNotFound(text)


def make_image_url(data: dict) -> list:
    read_chapter = data.get("readChapter", None)
    if read_chapter is None:
        raise AtsumaruException.UnexpectedJsonStructure("readChapter")

    pages = read_chapter.get("pages", None)
    if pages is None:
        raise AtsumaruException.UnexpectedJsonStructure("pages")

    image_urls = []

    for items in pages:
        image_urls.append(f"https://atsu.moe{items["image"]}")

    return image_urls


def get_title(text: dict, *, _only_title: bool = False) -> dict:
    manga_page = text.get("mangaPage", None)
    if manga_page is None:
        raise AtsumaruException.UnexpectedJsonStructure("mangaPage")
    title = manga_page.get("title", None)
    if title is None:
        raise AtsumaruException.UnexpectedJsonStructure("title")

    if _only_title:
        return {
            "title": title
        }

    alt_titles = manga_page.get("otherNames", None)
    if alt_titles is None:
        log(f"Alt titles not found on {title}, Just using the title", "warn")
        return {
            "title": title
        }
    return {
        "title": title,
        "alt_titles": alt_titles
    }


def get_chapter_name(text: dict) -> str:
    manga_page = text.get("readChapter", None)
    if manga_page is None:
        raise AtsumaruException.UnexpectedJsonStructure("readChapter")

    chapter_title = manga_page.get("title", None)
    if chapter_title is None:
        raise AtsumaruException.UnexpectedJsonStructure("title")
    return chapter_title


def _find_json_tags(data: dict, key: str):
    manga_page = data.get("mangaPage", None)
    if not manga_page:
        raise AtsumaruException.UnexpectedJsonStructure("mangaPage")

    tags = manga_page.get(key, None)
    if not tags:
        log(f"'{key}' was not found in the metadata", "warn")
    return tags


def get_authors(data: dict) -> list:
    authors = _find_json_tags(data, "authors")

    author_list = []
    for author in authors:
        author_list.append(author.get("name"))

    return author_list


def get_synopsis(data: dict) -> str | None:
    synopsis = _find_json_tags(data, "synopsis")
    if not synopsis:
        log("Could not find synopsis tag", "warn")
        return None
    return synopsis


def get_comic_type(data: dict) -> str | None:
    comic_type = _find_json_tags(data, "synopsis")
    if not comic_type:
        log("Could not find type tag", "warn")
        return None
    return comic_type


def get_status(data: dict) -> str | None:
    status = _find_json_tags(data, "status")
    if not status:
        log("Could not find status tag", "warn")
        return None
    return status


def get_tags(data: dict) -> list:
    tags = _find_json_tags(data, "tags")
    tags_list = []
    for i in tags:
        tags_list.append(i.get("name"))
    return tags_list


def get_poster_url(data: dict) -> str | None:
    poster_url = _find_json_tags(data, "poster")
    if not poster_url:
        log("Could not find poster url tag", "warn")
        return None
    poster_url = poster_url.get("image", None)
    if not poster_url:
        log("Could not find poster url tag", "warn")
        return None

    return f"https://atsu.moe/static/{poster_url}"


# Series parsing

def get_manga_id(text: str) -> str:
    try:
        manga_id = text.rsplit("/", 1)
        manga_id = manga_id[1].split("?")
        return manga_id[0]
    except Exception:
        raise AtsumaruException.MangaIDNotFound(text)


def make_chapter_urls(manga_id: str, text: dict, scanlation_id: str | None) -> list:
    chapters = text.get("chapters", None)

    if chapters is None:
        raise AtsumaruException.UnexpectedJsonStructure("chapters")

    chapter_urls = []
    for chapter in chapters:
        chapter_scanlation = chapter.get("scanlationMangaId")

        if scanlation_id is None or chapter_scanlation == scanlation_id:
            chapter_urls.append(
                f"https://atsu.moe/read/{manga_id}/{chapter['id']}"
            )
    if len(chapter_urls) <= 0:
        raise AtsumaruException.NoChaptersToDownload("Chapter_url list is less than 0")

    return chapter_urls
