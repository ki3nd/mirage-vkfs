import asyncio
import os

from agents import Runner
from agents.run import RunConfig
from agents.sandbox import SandboxAgent, SandboxRunConfig
from dotenv import load_dotenv
from mirage_vkfs.resource.dify import DifyConfig, DifyResource

from mirage import MountMode, Workspace
from mirage.agents.openai_agents import MirageSandboxClient

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
client = MirageSandboxClient(ws)

agent = SandboxAgent(
    name="Mirage Dify Knowledge Agent",
    model=os.environ.get("OPENAI_MODEL", "gpt-5.5-mini"),
    instructions=(
        f"{ws.file_prompt}\n\n"
        "The /knowledge/ mount contains a Dify Knowledge dataset as "
        "read-only text files. Use shell commands such as find, ls, cat, "
        "head, grep, and search to inspect it. Use head before cat for "
        "large files."),
)

task = os.environ.get(
    "DIFY_EXAMPLE_QUERY",
    "Search /knowledge/ for the most relevant documents and summarize them.",
)


async def main() -> None:
    result = await Runner.run(
        agent,
        task,
        run_config=RunConfig(sandbox=SandboxRunConfig(client=client)),
    )
    print(result.final_output)

    records = ws.ops.records
    if records:
        print(f"\n--- {len(records)} ops, {ws.ops.network_bytes:,} "
              f"network bytes, {ws.ops.cache_bytes:,} cache bytes ---")
        for record in records:
            print(f"  {record.op:<8} {record.source:<8} "
                  f"{record.bytes:>10,} B {record.duration_ms:>5} ms  "
                  f"{record.path}")


asyncio.run(main())
