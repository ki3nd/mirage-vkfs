import pytest
from mirage_vkfs.core.dify import glob, tree

from mirage.types import PathSpec

from .conftest import list_nested_documents


@pytest.mark.asyncio
async def test_resolve_glob_matches_directory_pattern(monkeypatch,
                                                      dify_accessor,
                                                      dify_index):
    monkeypatch.setattr(tree, "list_all_documents", list_nested_documents)
    path = PathSpec(original="/knowledge/guides/*.md",
                    directory="/knowledge/guides",
                    pattern="quick*",
                    resolved=False,
                    prefix="/knowledge/")

    matches = await glob.resolve_glob(dify_accessor, [path], dify_index)

    assert [item.original
            for item in matches] == ["/knowledge/guides/quickstart"]
    assert matches[0].directory == "/knowledge/guides/"


@pytest.mark.asyncio
async def test_resolve_glob_recursive_pattern_returns_files_only(
        monkeypatch, dify_accessor, dify_index):
    monkeypatch.setattr(tree, "list_all_documents", list_nested_documents)
    path = PathSpec(original="/knowledge/guides/**",
                    directory="/knowledge/guides",
                    pattern="**",
                    resolved=False,
                    prefix="/knowledge/")

    matches = await glob.resolve_glob(dify_accessor, [path], dify_index)

    assert [item.original for item in matches] == [
        "/knowledge/guides/deep/note",
        "/knowledge/guides/quickstart",
    ]
