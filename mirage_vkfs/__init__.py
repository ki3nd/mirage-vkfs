from mirage.resource.registry import REGISTRY, ResourceEntry

__all__ = ["register"]


def register() -> None:
    REGISTRY["dify"] = ResourceEntry(
        "mirage_vkfs.resource.dify:DifyResource",
        "mirage_vkfs.resource.dify:DifyConfig",
    )
