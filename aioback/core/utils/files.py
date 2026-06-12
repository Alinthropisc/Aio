from pathlib import Path

import aiofiles
import aiofiles.os


class FileManager:
    def __init__(self, base_dir: str | Path = "storage") -> None:
        self.base_dir = Path(base_dir)

    async def read(self, path: str | Path) -> str:
        async with aiofiles.open(self.base_dir / path, encoding="utf-8") as f:
            return await f.read()

    async def write(self, path: str | Path, content: str) -> None:
        full = self.base_dir / path
        await aiofiles.os.makedirs(full.parent, exist_ok=True)
        async with aiofiles.open(full, "w", encoding="utf-8") as f:
            await f.write(content)

    async def read_bytes(self, path: str | Path) -> bytes:
        async with aiofiles.open(self.base_dir / path, "rb") as f:
            return await f.read()

    async def write_bytes(self, path: str | Path, content: bytes) -> None:
        full = self.base_dir / path
        await aiofiles.os.makedirs(full.parent, exist_ok=True)
        async with aiofiles.open(full, "wb") as f:
            await f.write(content)

    async def exists(self, path: str | Path) -> bool:
        return await aiofiles.os.path.exists(self.base_dir / path)

    async def remove(self, path: str | Path) -> None:
        await aiofiles.os.remove(self.base_dir / path)
