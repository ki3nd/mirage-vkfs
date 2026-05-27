import pytest

from mirage_vkfs.commands.builtin.dify.sed import sed
from mirage_vkfs.core.dify import read, tree

from mirage.io.types import materialize

from .conftest import document


async def list_single_document(config):
    return [document("doc-1", "Guide", "guides/quickstart.md")]


async def get_segments(config, document_id):
    return [{"content": "alpha beta\nbeta"}]


@pytest.mark.asyncio
async def test_sed_rewrites_document_content(monkeypatch, dify_accessor,
                                             dify_index, guide_path):
    monkeypatch.setattr(tree, "list_all_documents", list_single_document)
    monkeypatch.setattr(read, "get_document_segments", get_segments)

    stdout, io = await sed(dify_accessor, [guide_path],
                           "s/beta/gamma/g",
                           index=dify_index)

    assert await materialize(stdout) == b"alpha gamma\ngamma"
    assert io.exit_code == 0


@pytest.mark.asyncio
async def test_sed_rejects_in_place_updates(monkeypatch, dify_accessor,
                                            dify_index, guide_path):
    monkeypatch.setattr(tree, "list_all_documents", list_single_document)

    with pytest.raises(PermissionError,
                       match="sed -i not supported on read-only Dify mount"):
        await sed(dify_accessor, [guide_path],
                  "s/beta/gamma/g",
                  i=True,
                  index=dify_index)
