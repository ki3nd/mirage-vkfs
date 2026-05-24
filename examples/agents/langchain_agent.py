import os

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mirage_vkfs.resource.dify import DifyConfig, DifyResource

from mirage import MountMode, Workspace
from mirage.agents.langchain import (LangchainWorkspace, build_system_prompt,
                                     extract_text)

load_dotenv(".env.development")


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def build_dify_resource() -> DifyResource:
    return DifyResource(
        config=DifyConfig(
            api_key=require_env("DIFY_API_KEY"),
            base_url=os.environ.get("DIFY_BASE_URL",
                                    "https://api.dify.ai/v1"),
            dataset_id=require_env("DIFY_DATASET_ID"),
            slug_metadata_name=os.environ.get("DIFY_SLUG_METADATA_NAME",
                                              "slug"),
        ))


dify = build_dify_resource()
ws = Workspace({"/knowledge/": dify}, mode=MountMode.READ)

agent = create_deep_agent(
    model=ChatOpenAI(model=os.environ.get("OPENAI_MODEL", "gpt-5.5-mini")),
    system_prompt=build_system_prompt(
        mount_info={
            "/knowledge/":
            "Dify Knowledge dataset mounted as read-only text files"
        },
        extra_instructions=(
            "Use /knowledge/ as the source of truth. "
            "Use find, ls, cat, head, grep, and search to inspect documents. "
            "Use head before cat for large files."),
    ),
    backend=LangchainWorkspace(ws),
)

query = os.environ.get(
    "DIFY_EXAMPLE_QUERY",
    "Find the most relevant documents in /knowledge/ and summarize them.",
)
result = agent.invoke({"messages": [{"role": "user", "content": query}]})

for text in extract_text(result["messages"]):
    print(text)

records = ws.ops.records
if records:
    print(f"\n--- {len(records)} ops, {ws.ops.network_bytes:,} network bytes, "
          f"{ws.ops.cache_bytes:,} cache bytes ---")
    for record in records:
        print(f"  {record.op:<8} {record.source:<8} {record.bytes:>10,} B "
              f"{record.duration_ms:>5} ms  {record.path}")
