import pytest

from mirage_vkfs.commands.builtin.dify.tree import tree as tree_command
from mirage_vkfs.core.dify import tree

from mirage.io.types import materialize

from .conftest import document


async def list_documents(config):
    return [
        document("doc-1", "Guide", "guides/quickstart.md"),
        document("doc-2", "Api", "guides/deep/note.md"),
        document("doc-3", "Readme", "README.md"),
    ]


@pytest.mark.asyncio
async def test_tree_renders_directory_structure(monkeypatch, dify_accessor,
                                                dify_index, knowledge_root):
    monkeypatch.setattr(tree, "list_all_documents", list_documents)

    stdout, io = await tree_command(dify_accessor, [knowledge_root],
                                    index=dify_index)

    assert await materialize(stdout) == (
        b"\xe2\x94\x9c\xe2\x94\x80\xe2\x94\x80 README.md\n"
        b"\xe2\x94\x94\xe2\x94\x80\xe2\x94\x80 guides\n"
        b"    \xe2\x94\x9c\xe2\x94\x80\xe2\x94\x80 deep\n"
        b"    \xe2\x94\x82   \xe2\x94\x94\xe2\x94\x80\xe2\x94\x80 note.md\n"
        b"    \xe2\x94\x94\xe2\x94\x80\xe2\x94\x80 quickstart.md")
    assert io.exit_code == 0


@pytest.mark.asyncio
async def test_tree_uses_cwd_and_depth_limit(monkeypatch, dify_accessor,
                                             dify_index, guides_path):
    monkeypatch.setattr(tree, "list_all_documents", list_documents)

    stdout, io = await tree_command(dify_accessor, [],
                                    cwd=guides_path,
                                    L="1",
                                    index=dify_index)

    assert await materialize(stdout) == (
        b"\xe2\x94\x9c\xe2\x94\x80\xe2\x94\x80 deep\n"
        b"\xe2\x94\x82   \xe2\x94\x94\xe2\x94\x80\xe2\x94\x80 note.md\n"
        b"\xe2\x94\x94\xe2\x94\x80\xe2\x94\x80 quickstart.md")
    assert io.exit_code == 0
