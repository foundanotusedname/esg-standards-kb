# esg-kb:MCP 检索服务器

**一句话定位**:把知识库变成 MCP 工具,任何支持 MCP 的会话里都能用 `esg_search / esg_get / esg_compare / esg_industry` 四个工具查询,不用先手动读文件。

## 安装(任意机器复现)

1. 依赖:Python 3.12+,官方 SDK **锁定 1.x**(`pip install "mcp<2"`;2.x 改了 API,勿升级)。
2. 在 MCP 宿主(ZCode 等)的用户级配置 `~/.zcode/cli/config.json`(Windows 即 `%USERPROFILE%\.zcode\cli\config.json`)中注册:

```json
{
  "mcp": {
    "servers": {
      "esg-kb": {
        "command": "<本机 Python 解释器绝对路径>",
        "args": ["<本仓库检出路径>/mcp/server.py"]
      }
    }
  }
}
```

3. 重启客户端;新会话自动连接,状态见 设置 → MCP。

> 服务器默认以"本脚本上上级目录"为知识库根目录;如需指向别处,设置环境变量 `ESG_KB_ROOT`。

## 四个工具

| 工具 | 用途 | 示例参数 |
|---|---|---|
| `esg_search` | 按关键词检索知识文件(标题/标签/摘要/正文,自动处理"范围3"↔"范围 3") | `{"query": "北交所 强制"}` |
| `esg_get` | 读取知识文件全文(按路径或编号) | `{"file_id": "01-01"}` 或 `{"path": "knowledge/02-ISSB/02-IFRS-S2解读.md"}` |
| `esg_compare` | 议题在交易所指引 ↔ IFRS ↔ GRI ↔ SASB 间的映射(来自 indexes/topics.json) | `{"topic": "气候"}` |
| `esg_industry` | 行业的 SASB 实质性议题方向与三所议题对应 | `{"industry": "软件"}` |

## 自测

端到端测试(握手 → 工具列表 → 10 个调用用例):

```bash
py mcp/test_client.py   # 在仓库检出目录内运行
```

手动冒烟:在支持 MCP 的对话里问"用 esg_compare 查'应对气候变化'的跨标准映射"。

## 知识库更新后

- 知识库内容变化**无需重启服务器**:`esg_search`/`esg_get`/`esg_industry` 每次实时读文件;
- 新增/删除知识文件时,同步更新 `indexes/kb-index.json`(esg_search 的元数据来源),`esg_get`/`esg_industry` 不受影响。

## 故障排查

- 设置 → MCP 里 esg-kb 显示未连接:先跑上面自测;再检查配置文件路径与 Python 解释器绝对路径是否正确。
- Python 升级/迁移后:更新 config.json 中 `command` 的绝对路径,并确认 SDK 仍为 1.x(`pip show mcp`)。
