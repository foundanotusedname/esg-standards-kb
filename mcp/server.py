"""ESG 披露标准知识库 MCP 服务器(esg-kb)

数据源:本仓库根目录下的知识库(检出后即用,无需配置)
  - indexes/kb-index.json   知识文件元数据索引
  - indexes/topics.json     21 个议题 × IFRS/GRI/SASB 映射
  - knowledge/**/*.md       知识库正文

由 MCP 宿主(如 ZCode)以 stdio 方式拉起;不要手动向 stdout 打印任何内容。

可用环境变量 ESG_KB_ROOT 覆盖知识库根目录(默认:本脚本的上上级目录)。
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

ROOT = Path(os.environ.get("ESG_KB_ROOT") or Path(__file__).resolve().parent.parent)
INDEX_PATH = ROOT / "indexes" / "kb-index.json"
TOPICS_PATH = ROOT / "indexes" / "topics.json"
MAX_GET_CHARS = 80_000


def _load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _norm(s: str) -> str:
    """匹配用规范化:去掉全部空白,使“范围3”可命中“范围 3”。"""
    return re.sub(r"\s+", "", (s or "")).lower()


def _read_kb_file(rel_path: str) -> str:
    full = (ROOT / rel_path).resolve()
    if not (full.is_relative_to(ROOT) and full.is_file()):
        raise FileNotFoundError(f"文件不存在: {rel_path}")
    return full.read_text(encoding="utf-8")


mcp = FastMCP(
    "esg-kb",
    instructions=(
        "ESG 披露标准知识库(esg-kb):覆盖中国三大交易所《可持续发展报告指引》及编制指南、"
        "财政部基本准则(背景)、ISSB(IFRS S1/S2)、SASB、GRI、议题映射与编制实务。"
        "先用 esg_search 定位文件,再用 esg_get 读取全文;跨标准比较用 esg_compare,行业议题用 esg_industry。"
        "回答时应注明知识库文件路径;知识库未收录的内容(如 SASB 逐行业指标明细)应明确说明并指向官方来源。"
    ),
)


@mcp.tool()
def esg_search(query: str, limit: int = 5, full_text: bool = True) -> str:
    """在知识库中检索相关文件。

    按关键词匹配各知识文件的标题、标签、摘要与(可选)正文,返回排序后的候选文件列表。
    之后通常应配合 esg_get 读取命中文件的全文。

    Args:
        query: 检索词,如 “双重重要性” “范围3” “北交所 强制” “鉴证”。
        limit: 最多返回条数(默认 5)。
        full_text: 是否同时检索正文(默认 True,略慢但召回更好)。
    """
    index = _load_json(INDEX_PATH)
    tokens = [_norm(t) for t in query.split() if t.strip()]
    if not tokens:
        tokens = [_norm(query)]
    scored = []
    for entry in index["files"]:
        hay_title = _norm(entry["title"])
        hay_tags = _norm(" ".join(entry.get("tags", [])))
        hay_summary = _norm(entry.get("summary", ""))
        hay_standards = _norm(" ".join(entry.get("standards", [])))
        score = 0
        for tk in tokens:
            if tk in hay_title:
                score += 4
            if tk in hay_tags:
                score += 3
            if tk in hay_summary:
                score += 2
            if tk in hay_standards:
                score += 1
        if full_text and score == 0:
            try:
                text = _norm(_read_kb_file(entry["path"]))
                hits = sum(text.count(tk) for tk in tokens)
                if hits:
                    score += 1 + min(hits, 10)
            except OSError:
                pass
        if score:
            scored.append((score, entry))
    scored.sort(key=lambda x: -x[0])

    if not scored:
        cats = "\n".join(f"- {c['id']} {c['name']}({c['path']})" for c in index["categories"])
        return (
            f"未检索到与 “{query}” 相关的知识文件。\n"
            f"知识库目录如下,可换用其他关键词,或用 esg_get 直接浏览:\n{cats}"
        )

    lines = [f"检索 “{query}” 命中 {len(scored[:limit])} 个文件(共 {len(scored)} 个候选):\n"]
    for score, entry in scored[:limit]:
        tags = "、".join(entry.get("tags", []))
        lines.append(
            f"### {entry['id']} {entry['title']}\n"
            f"- 路径:{entry['path']}\n"
            f"- 摘要:{entry.get('summary', '')}\n"
            f"- 标签:{tags}\n"
            f"- 相关度:{score}\n"
        )
    lines.append("提示:用 esg_get(path=...) 读取全文后再回答,并在回答中注明文件路径。")
    return "\n".join(lines)


@mcp.tool()
def esg_get(path: str = "", file_id: str = "") -> str:
    """读取知识库文件的 Markdown 全文。

    Args:
        path: 相对知识库根目录的路径,如 “knowledge/01-三大交易所/06-议题与指标清单.md”(斜杠或反斜杠均可)。
        file_id: 知识文件编号,如 “01-06”“02-02”(与 path 二选一,优先 path)。
    """
    index = _load_json(INDEX_PATH)
    rel = path
    if not rel and file_id:
        match = next((e for e in index["files"] if e["id"] == file_id.strip()), None)
        if not match:
            ids = ", ".join(e["id"] for e in index["files"])
            return f"未找到文件编号 {file_id}。可用编号:{ids}"
        rel = match["path"]
    if not rel:
        return "请提供 path 或 file_id 之一。可用编号见 esg_search 结果,或用 esg_get(file_id='00-01') 试探。"
    rel = rel.replace("\\", "/").lstrip("/")
    try:
        content = _read_kb_file(rel)
    except FileNotFoundError:
        return f"文件不存在: {rel}。可先用 esg_search 检索,或用 esg_get(file_id=...) 按编号读取。"
    if len(content) > MAX_GET_CHARS:
        content = content[:MAX_GET_CHARS] + "\n\n[内容过长已截断,完整原文请直接打开文件]"
    return f"[{rel}]\n\n{content}"


@mcp.tool()
def esg_compare(topic: str = "") -> str:
    """查询某议题在三大交易所指引、IFRS(S1/S2)、GRI、SASB 之间的映射。

    Args:
        topic: 议题关键词(中文即可),如 “气候”“范围3”“员工”“数据安全”;
               留空则列出全部 21 个议题名称。
    """
    topics = _load_json(TOPICS_PATH)["topics"]
    if not topic.strip():
        by_cat: dict[str, list[str]] = {}
        for t in topics:
            by_cat.setdefault(t["category"], []).append(t["cn"])
        lines = ["三所指引 21 个议题(用 esg_compare(topic=...) 查看单议题映射):"]
        for cat, names in by_cat.items():
            lines.append(f"- {cat}({len(names)}):" + "、".join(names))
        return "\n".join(lines)

    key = _norm(topic)
    hits = [
        t for t in topics
        if any(key in _norm(t.get(f, "")) for f in ("cn", "id", "category", "ifrs", "gri", "sasb", "note"))
    ]
    if not hits:
        names = "、".join(t["cn"] for t in topics)
        return f"未找到与 “{topic}” 匹配的议题。全部议题:{names}"
    out = [f"议题映射:与 “{topic}” 匹配 {len(hits)} 个议题(注意:映射为功能等价,各框架的重要性口径与边界可能不同)\n"]
    for t in hits:
        out.append(
            f"### {t['cn']}({t['category']}类)\n"
            f"- IFRS S1/S2:{t['ifrs']}\n"
            f"- GRI:{t['gri']}\n"
            f"- SASB:{t['sasb']}\n"
            f"- 备注:{t.get('note') or '—'}"
        )
    out.append("\n口径差异详见 knowledge/05-映射与选型/01-议题级互映射表.md(可用 esg_get 读取)。")
    return "\n\n".join(out)


@mcp.tool()
def esg_industry(industry: str) -> str:
    """查询某行业在 SASB 视角下的实质性议题方向及对应的三所指引议题。

    Args:
        industry: 行业关键词,中文或英文均可,如 “银行”“软件”“半导体”“电力”“banks”。
    """
    try:
        text = _read_kb_file("knowledge/03-SASB/02-77行业速查索引.md")
    except OSError as e:
        return f"行业索引文件读取失败: {e}"
    key = _norm(industry)
    rows = []
    in_table = False
    for line in text.splitlines():
        stripped = line.strip()
        in_table = stripped.startswith("|") or (in_table and not stripped)
        if stripped.startswith("|") and in_table:
            if key in _norm(stripped) and "---" not in stripped:
                rows.append(stripped)
    header = "| 行业 | SASB 高关注议题方向 | 对应三所议题 |\n|---|---|---|"
    if rows:
        body = "\n".join(rows)
        return (
            f"行业 “{industry}” 在 SASB 行业速查索引中的命中(共 {len(rows)} 行):\n\n"
            f"{header}\n{body}\n\n"
            "说明:以上为高关注议题方向;逐行业完整指标明细需到 SASB Navigator(navigator.sasb.ifrs.org)查询,知识库未收录。"
            "来源文件:knowledge/03-SASB/02-77行业速查索引.md"
        )
    return (
        f"行业 “{industry}” 未在速查索引中命中。\n"
        "知识库的 SASB 部分只收录到部门与代表行业级(11 部门 77 行业),"
        "逐行业标准请到 https://navigator.sasb.ifrs.org 查询;也可用 esg_search 换关键词(如部门名)检索。"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
