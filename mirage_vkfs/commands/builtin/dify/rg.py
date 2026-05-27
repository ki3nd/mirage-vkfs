from collections.abc import AsyncIterator
from functools import partial

from mirage_vkfs.core.dify.glob import resolve_glob
from mirage_vkfs.core.dify.read import read_stream
from mirage_vkfs.core.dify.readdir import readdir
from mirage_vkfs.core.dify.stat import stat_light

from mirage.cache.index import IndexCacheStore
from mirage.commands.builtin.generic.rg import rg as generic_rg
from mirage.commands.registry import command
from mirage.commands.spec import SPECS
from mirage.io.types import ByteSource, IOResult
from mirage.types import PathSpec


async def bound_readdir(accessor,
                        path: PathSpec,
                        index=None,
                        bound_index=None) -> list[str]:
    effective_index = bound_index if bound_index is not None else index
    return await readdir(accessor, path, effective_index)


async def bound_stat(accessor, path: PathSpec, index=None, bound_index=None):
    effective_index = bound_index if bound_index is not None else index
    return await stat_light(accessor, path, effective_index)


async def bound_read_bytes(accessor,
                           path: PathSpec,
                           index=None,
                           bound_index=None) -> bytes:
    effective_index = bound_index if bound_index is not None else index
    return b"".join(
        [chunk async for chunk in read_stream(accessor, path, effective_index)])


async def bound_read_stream(accessor,
                            path: PathSpec,
                            index=None,
                            bound_index=None):
    effective_index = bound_index if bound_index is not None else index
    async for chunk in read_stream(accessor, path, effective_index):
        yield chunk


@command("rg", resource="dify", spec=SPECS["rg"])
async def rg(
    accessor,
    paths: list[PathSpec],
    *texts: str,
    stdin: AsyncIterator[bytes] | bytes | None = None,
    i: bool = False,
    v: bool = False,
    n: bool = False,
    c: bool = False,
    args_l: bool = False,
    w: bool = False,
    F: bool = False,
    o: bool = False,
    m: str | None = None,
    A: str | None = None,
    B: str | None = None,
    C: str | None = None,
    hidden: bool = False,
    type: str | None = None,
    glob: str | None = None,
    filetype_fns: dict | None = None,
    index: IndexCacheStore = None,
    **_extra: object,
) -> tuple[ByteSource | None, IOResult]:
    if not texts:
        raise ValueError("rg: usage: rg [flags] pattern [path]")
    if paths:
        paths = await resolve_glob(accessor, paths, index)
    readdir_fn = partial(bound_readdir, bound_index=index)
    stat_fn = partial(bound_stat, bound_index=index)
    read_bytes_fn = partial(bound_read_bytes, bound_index=index)
    read_stream_fn = partial(bound_read_stream, bound_index=index)
    context_after = int(A) if A is not None else 0
    context_before = int(B) if B is not None else 0
    if C is not None:
        context_before = context_after = int(C)
    return await generic_rg(
        paths,
        pattern=texts[0],
        readdir=readdir_fn,
        stat=stat_fn,
        read_bytes=read_bytes_fn,
        read_stream=read_stream_fn,
        accessor=accessor,
        filetype_fns=filetype_fns,
        stdin=stdin,
        ignore_case=i,
        invert=v,
        line_numbers=n,
        count_only=c,
        files_only=args_l,
        whole_word=w,
        fixed_string=F,
        only_matching=o,
        max_count=int(m) if m is not None else None,
        context_before=context_before,
        context_after=context_after,
        hidden=hidden,
        file_type=type,
        glob_pattern=glob,
        index=index,
    )
