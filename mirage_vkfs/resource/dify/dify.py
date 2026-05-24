from mirage_vkfs.accessor.dify import DifyAccessor
from mirage_vkfs.commands.builtin.dify import COMMANDS
from mirage_vkfs.core.dify.glob import resolve_glob as _resolve_glob
from mirage_vkfs.core.dify.read import read_bytes, read_stream
from mirage_vkfs.core.dify.readdir import readdir
from mirage_vkfs.core.dify.stat import stat
from mirage_vkfs.ops.dify import OPS as DIFY_VFS_OPS
from mirage_vkfs.resource.dify.config import DifyConfig
from mirage_vkfs.resource.dify.prompt import PROMPT

from mirage.resource.base import BaseResource

_DIFY_OPS = {
    "read_bytes": read_bytes,
    "read_stream": read_stream,
    "readdir": readdir,
    "stat": stat,
}


class DifyResource(BaseResource):

    name: str = "dify"
    is_remote: bool = True
    _ops = _DIFY_OPS
    PROMPT: str = PROMPT
    SUPPORTS_SNAPSHOT: bool = False

    def __init__(self, config: DifyConfig) -> None:
        super().__init__()
        self.config = config
        self.accessor = DifyAccessor(config)

        for fn in COMMANDS:
            self.register(fn)
        for fn in DIFY_VFS_OPS:
            self.register_op(fn)

    async def resolve_glob(self, paths, prefix: str = ""):
        return await _resolve_glob(self.accessor, paths, index=self._index)

    async def fingerprint(self, path: str) -> str | None:
        return None

    def get_state(self) -> dict:
        redacted = ["api_key"]
        config = self.config.model_dump()
        if config.get("api_key") is not None:
            config["api_key"] = "<REDACTED>"
        return {
            "type": self.name,
            "needs_override": True,
            "redacted_fields": redacted,
            "config": config,
        }

    def load_state(self, state: dict) -> None:
        pass
