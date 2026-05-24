from mirage_vkfs.resource.dify.config import DifyConfig

from mirage.accessor.base import Accessor


class DifyAccessor(Accessor):

    def __init__(self, config: DifyConfig) -> None:
        self.config = config
