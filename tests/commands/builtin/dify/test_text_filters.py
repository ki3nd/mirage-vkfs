import pytest

from mirage_vkfs.commands.builtin.dify.awk import awk
from mirage_vkfs.commands.builtin.dify.cut import cut
from mirage_vkfs.commands.builtin.dify.sort import sort
from mirage_vkfs.commands.builtin.dify.uniq import uniq
from mirage_vkfs.core.dify import read, tree

from mirage.io.types import materialize

from .conftest import document


async def list_single_document(config):
    return [document("doc-1", "Guide", "guides/quickstart.md")]


async def get_segments(config, document_id):
    return [{"content": "b beta\nc alpha\na alpha\na alpha"}]


async def iter_pages(config, document_id):
    yield [{"content": "b beta\nc alpha"}]
    yield [{"content": "a alpha\na alpha"}]


@pytest.mark.asyncio
async def test_awk_extracts_first_field(monkeypatch, dify_accessor, dify_index,
                                        guide_path):
    monkeypatch.setattr(tree, "list_all_documents", list_single_document)
    monkeypatch.setattr(read, "get_document_segments", get_segments)
    monkeypatch.setattr(read, "iter_segment_pages", iter_pages)

    stdout, io = await awk(dify_accessor, [guide_path],
                           "{print $1}",
                           index=dify_index)

    assert await materialize(stdout) == b"b\nc\na\na\n"
    assert io.exit_code == 0


@pytest.mark.asyncio
async def test_cut_extracts_first_field(monkeypatch, dify_accessor, dify_index,
                                        guide_path):
    monkeypatch.setattr(tree, "list_all_documents", list_single_document)
    monkeypatch.setattr(read, "iter_segment_pages", iter_pages)

    stdout, io = await cut(dify_accessor, [guide_path],
                           f="1",
                           d=" ",
                           index=dify_index)

    assert await materialize(stdout) == b"b\nc\na\na\n"
    assert io.exit_code == 0


@pytest.mark.asyncio
async def test_sort_orders_lines(monkeypatch, dify_accessor, dify_index,
                                 guide_path):
    monkeypatch.setattr(tree, "list_all_documents", list_single_document)
    monkeypatch.setattr(read, "get_document_segments", get_segments)
    monkeypatch.setattr(read, "iter_segment_pages", iter_pages)

    stdout, io = await sort(dify_accessor, [guide_path], index=dify_index)

    assert await materialize(stdout) == b"a alpha\na alpha\nb beta\nc alpha\n"
    assert io.exit_code == 0


@pytest.mark.asyncio
async def test_uniq_collapses_adjacent_duplicates(monkeypatch, dify_accessor,
                                                  dify_index, guide_path):
    monkeypatch.setattr(tree, "list_all_documents", list_single_document)
    monkeypatch.setattr(read, "get_document_segments", get_segments)
    monkeypatch.setattr(read, "iter_segment_pages", iter_pages)

    stdout, io = await uniq(dify_accessor, [guide_path], index=dify_index)

    assert await materialize(stdout) == b"b beta\nc alpha\na alpha\n"
    assert io.exit_code == 0
