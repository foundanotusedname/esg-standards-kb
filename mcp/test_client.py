"""esg-kb MCP 服务器的端到端测试:initialize → list_tools → 逐个调用工具。

运行:py F:/esg/mcp/test_client.py
"""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = Path(__file__).resolve().parent / "server.py"

CASES = [
    ("esg_search", {"query": "范围3"}),
    ("esg_search", {"query": "北交所 强制", "full_text": False}),
    ("esg_search", {"query": "zzz不存在的词zzz"}),
    ("esg_get", {"file_id": "01-01"}),
    ("esg_get", {"path": "knowledge/不存在.md"}),
    ("esg_compare", {"topic": "气候"}),
    ("esg_compare", {"topic": "乡村振兴"}),
    ("esg_compare", {"topic": ""}),
    ("esg_industry", {"industry": "软件"}),
    ("esg_industry", {"industry": "不存在的行业xyz"}),
]


async def main() -> None:
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            print(f"SERVER: {init.serverInfo.name} | protocol: {init.protocolVersion}")
            tools = await session.list_tools()
            print(f"TOOLS: {sorted(t.name for t in tools.tools)}")

            for name, args in CASES:
                result = await session.call_tool(name, args)
                text = result.content[0].text if result.content else "(空响应)"
                print(f"\n===== {name} {args} =====")
                print(text[:500] + ("…[截断]" if len(text) > 500 else ""))

            print("\nALL TOOL CALLS COMPLETED WITHOUT EXCEPTION")


if __name__ == "__main__":
    asyncio.run(main())
