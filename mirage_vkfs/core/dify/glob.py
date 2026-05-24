import fnmatch
import logging

from mirage_vkfs.core.dify.readdir import readdir
from mirage_vkfs.core.dify.walk import walk

from mirage.cache.index import IndexCacheStore
from mirage.types import PathSpec

logger = logging.getLogger(__name__)

SCOPE_ERROR = 50000


async def resolve_glob(accessor, paths: list,
                       index: IndexCacheStore) -> list[PathSpec]:
    if not paths:
        return []
    resolved: list[PathSpec] = []
    for path in paths:
        if isinstance(path, str):
            path = PathSpec.from_str_path(path)
        if path.resolved and not path.pattern:
            resolved.append(path)
            continue
        if path.pattern == "**":
            children = [
                child for child in await walk(
                    accessor, path.dir, index, ignore_missing=True)
                if await is_file(index, child)
            ]
        else:
            children = await readdir(accessor, path.dir, index)
        matched = [
            PathSpec.from_str_path(child, path.prefix) for child in children
            if path.pattern in {None, "**"} or fnmatch.fnmatch(
                child.rstrip("/").rsplit("/", 1)[-1], path.pattern)
        ]
        if len(matched) > SCOPE_ERROR:
            logger.warning(
                "%s: %d matches exceeds limit (%d), truncating",
                path.directory,
                len(matched),
                SCOPE_ERROR,
            )
            matched = matched[:SCOPE_ERROR]
        resolved.extend(matched)
    return resolved


async def is_file(index: IndexCacheStore, path: str) -> bool:
    lookup = await index.get(path)
    return (lookup.entry is not None and lookup.entry.resource_type == "file")
