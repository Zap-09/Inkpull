from dataclasses import dataclass
from typing import Optional


@dataclass
class AtsumaruChapter:
    id: str
    scanlationMangaId: str
    title: str
    number: int
    scanlationGroupName: Optional[str] = ""
    chapterUrl: Optional[str] = ""


@dataclass
class AtsumaruScanlator:
    id: str
    name: str
    chapters: list[AtsumaruChapter]

    @property
    def chapter_count(self) -> int:
        return len(self.chapters)
