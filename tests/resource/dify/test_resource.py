from mirage_vkfs import register
from mirage_vkfs.resource.dify import DifyConfig, DifyResource

from mirage.resource.registry import REGISTRY, build_resource


def make_resource(**overrides) -> DifyResource:
    data = {
        "api_key": "dataset-secret",
        "base_url": "https://api.dify.ai/v1/",
        "dataset_id": "dataset-1",
    }
    data.update(overrides)
    return DifyResource(DifyConfig(**data))


def test_dify_resource_redacts_api_key():
    resource = make_resource()

    assert resource.name == "dify"
    assert resource.is_remote is True
    assert resource.SUPPORTS_SNAPSHOT is False
    assert resource.config.base_url == "https://api.dify.ai/v1"
    assert resource.config.slug_metadata_name == "slug"
    assert resource.accessor.config is resource.config

    state = resource.get_state()
    assert state["type"] == "dify"
    assert state["needs_override"] is True
    assert state["redacted_fields"] == ["api_key"]
    assert state["config"]["api_key"] == "<REDACTED>"
    assert state["config"]["dataset_id"] == "dataset-1"
    assert state["config"]["slug_metadata_name"] == "slug"


def test_register_adds_dify_to_mirage_resource_registry():
    original = REGISTRY.get("dify")
    try:
        register()
        assert REGISTRY[
            "dify"].resource_path == "mirage_vkfs.resource.dify:DifyResource"
        assert REGISTRY[
            "dify"].config_path == "mirage_vkfs.resource.dify:DifyConfig"

        resource = build_resource(
            "dify",
            {
                "api_key": "dataset-secret",
                "base_url": "https://api.dify.ai/v1/",
                "dataset_id": "dataset-1",
            },
        )
    finally:
        if original is None:
            REGISTRY.pop("dify", None)
        else:
            REGISTRY["dify"] = original

    assert isinstance(resource, DifyResource)
    assert resource.name == "dify"


def test_dify_resource_accepts_configured_slug_metadata_name():
    resource = make_resource(slug_metadata_name="path",
                             base_url="https://api.dify.ai/v1")

    assert resource.config.slug_metadata_name == "path"


def test_dify_resource_registers_expected_commands_and_ops():
    resource = make_resource(base_url="https://api.dify.ai/v1", )

    commands = {item.name for item in resource.commands()}
    ops = {item.name for item in resource.ops_list()}

    assert {"cat", "ls", "grep", "find", "head", "tail",
            "wc"}.issubset(commands)
    assert {"read", "readdir", "stat", "grep"}.issubset(ops)
