# skill-esg-standards(源文件目录)

本目录是 `esg-standards` skill 的**源文件**(随仓库版本管理)。

## 安装

复制到你的用户级 skills 目录(Windows:`%USERPROFILE%\.agents\skills\`;macOS/Linux:`~/.agents/skills/`):

```bash
mkdir -p ~/.agents/skills/esg-standards/references
cp SKILL.md ~/.agents/skills/esg-standards/SKILL.md
cp references/examples.md ~/.agents/skills/esg-standards/references/examples.md
```

新会话生效。注意:`.zcode/skills/` 下的同名 skill 会覆盖本 skill,不要创建同名副本。

## 使用前必改一处

`SKILL.md` 与 `references/examples.md` 中的知识库根目录写的是 `F:\esg`。检出本仓库后,请把这两个文件里所有 `F:\esg` 替换为你本机的仓库检出路径,再执行上面的安装复制。

## 文件说明

- `SKILL.md`:路由与使用规则(核心规则、路由表、回答模式、维护方式)
- `references/examples.md`:回答模式正反例(按需读取)

## 同步方式(已在用的机器上更新)

修改本目录源文件后,重新复制到用户级目录即可(命令同"安装"一节)。
