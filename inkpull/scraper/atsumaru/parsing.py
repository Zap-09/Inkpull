import sys
from utils import log
from .exceptions import AtsumaruException
from .schemas import AtsumaruScanlator, AtsumaruChapter


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
    comic_type = _find_json_tags(data, "type")
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
    tags = _find_json_tags(data, "genres")
    if not tags:
        log("Could not find genres tags", "warn")
        return []
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


def construct_chapter_urls(manga_id: str, data: list[AtsumaruChapter]) -> list[AtsumaruChapter]:
    comic_to_download = []

    for chapter in data:
        chapter.chapterUrl = f"https://atsu.moe/read/{manga_id}/{chapter.id}"
        comic_to_download.append(chapter)
    return comic_to_download


def parse_user_input(user_input: str, max_items: int) -> list[int]:
    args = user_input.strip()

    if not args:
        raise ValueError(
            "Invalid input. Empty input."
        )

    if args == "--help":
        log("Use numbers to pick scan groups.", "info")
        log("Example: 1,3", "info")
        log("Use --all to select all.", "info")
        log("Use 0 to exit.", "info")
        raise AtsumaruException.HelpFlag

    if args == "--all":
        return list(range(max_items))

    if args == "0":
        raise SystemExit

    selection_seen = set()
    selection = []

    for item in args.split(","):
        item = item.strip()

        if not item.isdigit():
            log(f"{item} is not a number, skipping...", "warn")
            continue

        number = int(item)

        if number == 0:
            raise ValueError(
                "0 cannot be combined with other selections"
            )

        index = number - 1

        if index < 0 or index >= max_items:
            raise IndexError(
                f"{number} is out of range"
            )

        if index not in selection_seen:
            selection_seen.add(index)
            selection.append(index)

    if not selection:
        raise ValueError(
            "No valid selections"
        )

    return selection


def extract_scanlators(all_chapter_json: dict, page_json: dict) -> list[AtsumaruScanlator]:
    chapters_object = all_chapter_json.get("chapters", None)
    if not chapters_object:
        raise AtsumaruException.UnexpectedJsonStructure(
            f"Unexpected json structure. Can't find key 'chapters'"
        )
    chapters_object.reverse()
    chapters = [
        AtsumaruChapter(
            id=c["id"],
            scanlationMangaId=c["scanlationMangaId"],
            title=c["title"],
            number=c["number"],
        )
        for c in chapters_object
    ]

    chapter_by_scanlator = {}

    for c in chapters:
        chapter_by_scanlator.setdefault(
            c.scanlationMangaId, []
        ).append(c)

    manga_page = page_json.get("mangaPage", None)

    if manga_page is None:
        raise AtsumaruException.UnexpectedJsonStructure(
            f"Unexpected json structure. Can't find key 'mangaPage'"
        )
    scanlators_object = manga_page.get("scanlators", None)
    if not scanlators_object:
        raise AtsumaruException.UnexpectedJsonStructure(
            f"Unexpected json structure. Can't find key 'scanlators'"
        )

    scanlators = [
        AtsumaruScanlator(
            id=s["id"],
            name=s["name"],
            chapters=chapter_by_scanlator.get(s["id"], [])
        )
        for s in scanlators_object
    ]
    return scanlators


def smart_select_chapters(total_items: list[AtsumaruScanlator]) -> list[AtsumaruChapter]:
    seen_chapters = set()
    selected_chapters = []

    for group in total_items:
        for chapter in group.chapters:
            if chapter.number not in seen_chapters:
                chapter.scanlationGroupName = group.name
                seen_chapters.add(chapter.number)
                selected_chapters.append(chapter)
            else:
                continue

    return selected_chapters


def flatten_scanlator_chapters(total_items: list[AtsumaruScanlator]) -> list[AtsumaruChapter]:
    selected_chapters = []
    for group in total_items:
        for chapter in group.chapters:
            chapter.scanlationGroupName = group.name
            selected_chapters.append(chapter)

    return selected_chapters


def interactive_selection(scanlators: list[AtsumaruScanlator]
                          ) -> list[AtsumaruChapter]:
    log("Use comma ',' if you want to pick more than one scan group. Eg; 1, 4")
    while True:
        log("0. Exit", "info")

        for idx, scanlator in enumerate(scanlators, start=1):
            log(
                f"{idx}. "
                f"{scanlator.name} "
                f"({scanlator.chapter_count} chapters)", "info"
            )

        user_input = input(
            "Select scanlators: "
        )
        try:
            indexes = parse_user_input(
                user_input,
                len(scanlators)
            )

            selected_scanlators = [
                scanlators[i]
                for i in indexes
            ]
            return flatten_scanlator_chapters(selected_scanlators)

        except AtsumaruException.HelpFlag:
            pass
        except SystemExit:
            log("Exiting...", "info")
            sys.exit(0)
        except IndexError as e:
            log(str(e), "error")
        except ValueError as e:
            log(str(e), "error")


def resolve_selection(scanlators: list[AtsumaruScanlator],
                      *,
                      select_all: bool = False,
                      smart_select: bool = False,
                      ) -> list[AtsumaruChapter]:
    if smart_select and select_all:
        log("Both --all and --smart flag are present. Ignoring --smart", "warn")

    if select_all:
        return flatten_scanlator_chapters(scanlators)
    elif smart_select:
        return smart_select_chapters(scanlators)
    return interactive_selection(scanlators)
