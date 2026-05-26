# mirage-vkfs

`mirage-vkfs` is a Mirage plugin that mounts a Dify Knowledge dataset as a
read-only virtual filesystem.

It lets Mirage users browse Dify Knowledge documents with familiar filesystem
commands, stream document segments as text, and run Dify-backed semantic search
from the same `Workspace` interface used by agents and tools.

## Features

- Mount a Dify Knowledge dataset under a path such as `/knowledge/`.
- Expose completed Dify documents as plain text files.
- Build folder paths from document metadata such as `slug`.
- Support filesystem-style commands: `ls`, `find`, `cat`, `head`, `tail`,
  `grep`, and `wc`.
- Support Dify retrieval through a `search` command with semantic, full-text,
  hybrid, and keyword modes.
- Register Mirage ops for direct programmatic access: `read`, `readdir`,
  `stat`, `grep`, and `search`.
- Work with Mirage-backed LangChain and OpenAI Agents sandbox examples.

## Installation

Install from the Git repository with `uv`:

```bash
uv add "mirage-vkfs @ git+https://github.com/ki3nd/mirage-vkfs.git"
```

For agent examples, install the optional extras you need:

```bash
uv add "mirage-vkfs[langchain] @ git+https://github.com/ki3nd/mirage-vkfs.git"
uv add "mirage-vkfs[openai] @ git+https://github.com/ki3nd/mirage-vkfs.git"
uv add "mirage-vkfs[agents] @ git+https://github.com/ki3nd/mirage-vkfs.git"
```

The package declares its Mirage dependency in `pyproject.toml`, so installing
`mirage-vkfs` is the recommended way to get a compatible Mirage build.

## Quickstart

```python
import asyncio
import os

from mirage import MountMode
from mirage.workspace import Workspace
from mirage_vkfs.resource.dify import DifyConfig, DifyResource


async def main() -> None:
    resource = DifyResource(
        config=DifyConfig(
            api_key=os.environ["DIFY_API_KEY"],
            base_url=os.environ.get("DIFY_BASE_URL", "https://api.dify.ai/v1"),
            dataset_id=os.environ["DIFY_DATASET_ID"],
            slug_metadata_name=os.environ.get("DIFY_SLUG_METADATA_NAME", "slug"),
        )
    )

    ws = Workspace({"/knowledge/": resource}, mode=MountMode.READ)

    result = await ws.execute("find /knowledge/ -type f | head -n 10")
    print(await result.stdout_str())

    result = await ws.execute(
        'search --method hybrid --top-k 5 "getting started" /knowledge/'
    )
    print(await result.stdout_str())


if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

`DifyConfig` requires:

| Field | Description |
| --- | --- |
| `api_key` | Dify API key. |
| `base_url` | Dify API base URL. Defaults commonly use `https://api.dify.ai/v1`. |
| `dataset_id` | Dify Knowledge dataset ID. |
| `slug_metadata_name` | Metadata field used as the virtual path. Defaults to `slug`. |

Example environment:

```bash
export DIFY_API_KEY="..."
export DIFY_DATASET_ID="..."
export DIFY_BASE_URL="https://api.dify.ai/v1"
export DIFY_SLUG_METADATA_NAME="slug"
```

## Document Paths

Each visible Dify document becomes one file in the mounted filesystem.

Visible documents must be:

- `enabled`
- `indexing_status == completed`
- not archived

By default, `mirage-vkfs` reads a Dify document metadata field named `slug` and
uses it as the path below the mount root.

| Dify document | Metadata | Mirage path |
| --- | --- | --- |
| `Quickstart` | `slug=guides/quickstart.md` | `/knowledge/guides/quickstart.md` |
| `README.md` | no slug | `/knowledge/README.md` |

Slug values can contain `/` to create folders. Keep each slug unique, and avoid
using one document path as another document's parent directory.

## Commands

Once mounted in a `Workspace`, the Dify resource supports:

```bash
ls /knowledge/
find /knowledge/ -type f
cat /knowledge/guides/quickstart.md
head -n 20 /knowledge/guides/quickstart.md
tail -n 20 /knowledge/guides/quickstart.md
grep -i "billing" /knowledge/
wc /knowledge/guides/quickstart.md
```

Document text is assembled from completed, enabled Dify segments. Segment
contents are joined with a single newline.

## Search

Use `search` when meaning matters more than exact text matching:

```bash
search "how do I reset my password" /knowledge/
search --method hybrid --top-k 5 "billing policy" /knowledge/policies/
search --method semantic --threshold 0.4 "quickstart" /knowledge/guides/*.md
```

Supported methods:

| Method | Dify retrieval mode |
| --- | --- |
| `semantic` | Semantic search |
| `fulltext` | Full-text search |
| `hybrid` | Hybrid search |
| `keyword` | Keyword search |

Search can target the full dataset, folders, files, or globs. Scoped search uses
Dify metadata filtering, so it works best when documents consistently define the
configured slug metadata field.

## Agent Examples

Runnable examples are available in `examples/`:

- `examples/dify/dify.py` demonstrates direct `Workspace` usage.
- `examples/agents/langchain_agent.py` demonstrates a Mirage-backed LangChain
  agent.
- `examples/agents/openai_agents_sandbox_agent.py` demonstrates Mirage through
  the OpenAI Agents sandbox interface.

## Development

Install dependencies:

```bash
uv sync
```

Run tests:

```bash
uv run pytest
```

The test suite covers Dify tree construction, path resolution, document reads,
filesystem commands, scoped search, resource registration, and Mirage workspace
integration.

## Notes

- The Dify resource is read-only.
- Snapshots are not supported.
- Directory listings and path resolution use Mirage's index cache.
- Document content is fetched from Dify when commands materialize file data.
