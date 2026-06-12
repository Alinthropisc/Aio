import pytest

from core.utils.files import FileManager


@pytest.fixture
async def fm(tmp_path):
    return FileManager(base_dir=tmp_path)


class TestFileManager:
    async def test_write_and_read_text(self, fm):
        await fm.write("hello.txt", "hello world")
        content = await fm.read("hello.txt")
        assert content == "hello world"

    async def test_write_creates_subdirs(self, fm):
        await fm.write("a/b/c.txt", "nested")
        content = await fm.read("a/b/c.txt")
        assert content == "nested"

    async def test_write_and_read_bytes(self, fm):
        await fm.write_bytes("data.bin", b"\x00\x01\x02")
        content = await fm.read_bytes("data.bin")
        assert content == b"\x00\x01\x02"

    async def test_write_bytes_creates_subdirs(self, fm):
        await fm.write_bytes("x/y/z.bin", b"abc")
        content = await fm.read_bytes("x/y/z.bin")
        assert content == b"abc"

    async def test_exists_true(self, fm):
        await fm.write("exists.txt", "yes")
        assert await fm.exists("exists.txt") is True

    async def test_exists_false(self, fm):
        assert await fm.exists("does_not_exist.txt") is False

    async def test_remove_deletes_file(self, fm):
        await fm.write("to_delete.txt", "bye")
        await fm.remove("to_delete.txt")
        assert await fm.exists("to_delete.txt") is False

    async def test_overwrite_file(self, fm):
        await fm.write("file.txt", "v1")
        await fm.write("file.txt", "v2")
        assert await fm.read("file.txt") == "v2"
