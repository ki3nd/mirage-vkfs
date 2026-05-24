from mirage_vkfs.core.dify import read
from mirage_vkfs.core.dify.stream import read_stream


def test_stream_reexports_read_stream():
    assert read_stream is read.read_stream
