import pytest
from pathlib import Path
import tempfile
from tech_seeker.scanner.contexts.local_directory_context import (
    LocalDirectoryContext,
    LocalFileContext,
)


def test_local_directory_context_name():
    with tempfile.TemporaryDirectory() as tmp_dir:
        dir_path = Path(tmp_dir).joinpath("test_dir")
        dir_path.mkdir(exist_ok=True)
        context = LocalDirectoryContext(str(dir_path))
        assert context.name() == "test_dir"


def test_local_directory_context_next():
    with tempfile.TemporaryDirectory() as tmp_dir:
        dir_path = Path(tmp_dir)
        dir_path.mkdir(exist_ok=True)
        (dir_path / "file1.txt").touch()
        (dir_path / "subdir").mkdir(parents=True, exist_ok=True)
        (dir_path / "subdir" / "file2.txt").touch()

        context = LocalDirectoryContext(str(dir_path))
        iterator = iter(context)

        file1 = next(iterator)
        assert isinstance(file1, LocalFileContext)
        assert file1.path() == dir_path.joinpath("file1.txt").as_posix()

        file2 = next(iterator)
        assert isinstance(file2, LocalFileContext)
        assert file2.path() == dir_path.joinpath("subdir/file2.txt").as_posix()


def test_local_directory_context_stop_iteration():
    with tempfile.TemporaryDirectory() as tmp_dir:
        dir_path = Path(tmp_dir)
        dir_path.mkdir(exist_ok=True)
        (dir_path / "file1.txt").touch()

        context = LocalDirectoryContext(str(dir_path))
        iterator = iter(context)

        next(iterator)
        with pytest.raises(StopIteration):
            next(iterator)
