# esg-kb:MCP 检索服务器(第二期)

**一句话定位**:把知识库变成 MCP 工具,任何支持 MCP 的会话里都能用 `esg_search / esg_get / esg_compare / esg_industry` 四个工具查询,不用先手动读文件。

## 已注册位置

- 用户级配置:`C:\Users\daaa\.zcode\cli\config.json` → `mcp.servers["esg-kb"]`
- 服务器脚本:`F:\esg\mcp\server.py`(stdio 传输,由宿主自动拉起)
- 生效方式:新会话自动连接;当前会话需重启客户端后在 设置 → MCP 中可见。

## 四个工具

| 工具 | 用途 | 示例参数 |
|---|---|---|
| `esg_search` | 按关键词检索知识文件(标题/标签/摘要/正文,自动处理"范围3"↔"范围 3") | `{"query": "北交所 强制"}` |
| `esg_get` | 读取知识文件全文(按路径或编号) | `{"file_id": "01-01"}` 或 `{"path": "knowledge/02-ISSB/02-IFRS-S2解读.md"}` |
| `esg_compare` | 议题在交易所指引 ↔ IFRS ↔ GRI ↔ SASB 间的映射(来自 indexes/topics.json) | `{"topic": "气候"}` |
| `esg_industry` | 行业的 SASB 实质性议题方向与三所议题对应 | `{"industry": "软件"}` |

## 依赖与自测

- Python 3.12 + 官方 SDK:`py -m pip install "mcp<2"`(已安装 mcp 1.30.0;2.x 改了 API,勿升级)
- 端到端自测(握手 → 工具列表 → 10 个调用用例):

```bash
py F:/esg/mcp/test_client.py
```

- 手动冒烟:在支持 MCP 的对话里问"用 esg_compare 查'应对气候变化'的跨标准映射"。

## 知识库更新后

- 知识库内容变化**无需重启服务器**:`esg_search`/`esg_get`/`esg_industry` 每次实时读文件;
- 新增/删除知识文件时,同步更新 `indexes/kb-index.json`(esg_search 的元数据来源),`esg_get`/`esg_industry` 不受影响。

## 故障排查

- 设置 → MCP 里 esg-kb 显示未连接:先跑上面自测;再按 zcode-guide 的 `diagnosing-mcp` 技能流程检查配置文件与 Python 路径。
- Python 路径变化(升级/迁移):更新 config.json 中 `command` 的绝对路径。
