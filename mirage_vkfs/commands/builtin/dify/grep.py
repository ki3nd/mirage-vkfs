from mirage_vkfs.core.dify.glob import resolve_glob
from mirage_vkfs.core.dify.read import read_bytes, read_stream
from mirage_vkfs.core.dify.readdir import readdir
from mirage_vkfs.core.dify.stat import stat

from mirage.commands.builtin.generic.grep import grep as generic_grep
from mirage.commands.registry import command
from mirage.commands.spec import SPECS
from mirage.io.types import ByteSource, IOResult
from mirage.types import PathSpec


@command("grep", resource="dify", spec=SPECS["grep"])
async def grep(
    accessor,
    paths: list[PathSpec],
    *texts: str,
    r: bool = False,
    R: bool = False,
    i: bool = False,
    args_i: bool = False,
    v: bool = False,
    n: bool = False,
    c: bool = False,
    args_l: bool = False,
    w: bool = False,
    F: bool = False,
    E: bool = False,
    o: bool = False,
    m: str | None = None,
    q: bool = False,
    H: bool = False,
    args_h: bool = False,
    A: str | None = None,
    B: str | None = None,
    C: str | None = None,
    e: str | None = None,
    **_extra: object,
) -> tuple[ByteSource | None, IOResult]:
    index = _extra.get("index")
    paths = await resolve_glob(accessor, paths, index)

    async def _readdir(bound_accessor,
                       path: PathSpec,
                       _index=None) -> list[str]:
        return await readdir(bound_accessor, path, index)

    async def _stat(bound_accessor, path: PathSpec, _index=None):
        return await stat(bound_accessor, path, index)

    async def _read_bytes(bound_accessor,
                          path: PathSpec,
                          _index=None) -> bytes:
        return await read_bytes(bound_accessor, path, index)

    async def _read_stream(bound_accessor, path: PathSpec, _index=None):
        async for chunk in read_stream(bound_accessor, path, index):
            yield chunk

    pattern: str
    if e is not None:
        pattern = e
    elif texts:
        pattern = texts[0]
    else:
        raise ValueError("grep: usage: grep [flags] pattern [path]")

    return await generic_grep(
        paths,
        pattern=pattern,
        readdir=_readdir,
        stat=_stat,
        read_bytes=_read_bytes,
        read_stream=_read_stream,
        accessor=accessor,
        ignore_case=i or args_i,
        invert=v,
        line_numbers=n,
        count_only=c,
        files_only=args_l,
        whole_word=w,
        fixed_string=F,
        only_matching=o,
        quiet=q,
        recursive=r or R,
        max_count=int(m) if m is not None else None,
        after_context=int(A) if A is not None else
        (int(C) if C is not None else 0),
        before_context=int(B) if B is not None else
        (int(C) if C is not None else 0),
        index=index,
    )
