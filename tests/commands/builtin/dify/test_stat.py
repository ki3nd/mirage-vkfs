import pytest

from mirage_vkfs.commands.builtin.dify.stat import stat
from mirage_vkfs.core.dify import tree
from mirage_vkfs.core.dify import stat as stat_module

from mirage.io.types import materialize

from .conftest import document


async def list_documents(config):
    return [
        document("doc-1", "Guide", "guides/quickstart.md", size=42),
        document("doc-2", "Api", "guides/api.md", size=12),
    ]


async def get_document_detail(config, document_id):
    return {
        "updated_at": 1716282600,
        "tokens": 7,
        "indexing_status": "completed",
        "data_source_detail_dict": {
            "upload_file": {
                "size": 99
            }
        },
    }


@pytest.mark.asyncio
async def test_stat_reports_dify_file_metadata(monkeypatch, dify_accessor,
                                               dify_index, guide_path):
    monkeypatch.setattr(tree, "list_all_documents", list_documents)
    monkeypatch.setattr(stat_module, "get_document_detail", get_document_detail)

    stdout, io = await stat(dify_accessor, [guide_path], index=dify_index)

    text = (await materialize(stdout)).decode()
    assert "name=quickstart.md" in text
    assert "size=99" in text
    assert "type=text" in text
    assert "modified=2024-05-21T09:10:00Z" in text
    assert io.exit_code == 0


@pytest.mark.asyncio
async def test_stat_reports_directory(monkeypatch, dify_accessor, dify_index,
                                      guides_path):
    monkeypatch.setattr(tree, "list_all_documents", list_documents)

    stdout, io = await stat(dify_accessor, [guides_path], index=dify_index)

    text = (await materialize(stdout)).decode()
    assert "name=guides" in text
    assert "type=directory" in text
    assert io.exit_code == 0
