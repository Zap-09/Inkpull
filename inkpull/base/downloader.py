import asyncio
import aiohttp
import aiofiles
from pathlib import Path

from utils import log
from ..config import GConfig

class ImageDownloader:
    def __init__(self, headers=None, concurrency = None):
        self.headers = headers or {}
        self.semaphore = None

        #------configs------#
        self.chunk_size = GConfig.global_get("chunk_size")
        self.concurrency = concurrency or GConfig.global_get("image_concurrency")


    async def _download_one(self, session, url, path):
        async with self.semaphore:
            async with session.get(url) as resp:
                resp.raise_for_status()
                async with aiofiles.open(path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(self.chunk_size):
                        await f.write(chunk)


    async def download_concurrently(self, urls: list, output_dir: str | Path):
        """
        Downloads images concurrently
    Args:
        urls (List[str]): list of urls to download.
        output_dir (Path or str): directory to save the image.
        """


        self.semaphore = asyncio.Semaphore(self.concurrency)

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        timeout = aiohttp.ClientTimeout(total=GConfig.global_get("timeout"))
        async with aiohttp.ClientSession(
            headers=self.headers,
            timeout=timeout
        ) as session:
            tasks = []
            for i, url in enumerate(urls, 1):
                ext = Path(url).suffix or ".jpg"
                path = output_dir / f"{i:03d}{ext}"
                tasks.append(self._download_one(session, url, path))
            await asyncio.gather(*tasks)
        log(f"Downloaded {output_dir.name}")

