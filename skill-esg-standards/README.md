# skill-esg-standards(源文件目录)

本目录是 `esg-standards` skill 的**源文件**(版本管理用)。

**已注册(生效)位置**:`C:\Users\daaa\.agents\skills\esg-standards\`
用户级安装使该 skill 在任意工作区的对话中都可触发(触发条件见 SKILL.md 的 description)。

## 同步方式

修改本目录的 `SKILL.md` 或 `references/examples.md` 后,重新复制过去即可:

```bash
cp F:/esg/skill-esg-standards/SKILL.md C:/Users/daaa/.agents/skills/esg-standards/SKILL.md
cp F:/esg/skill-esg-standards/references/examples.md C:/Users/daaa/.agents/skills/esg-standards/references/examples.md
```

(新会话生效;`.zcode/skills/` 同名 skill 会覆盖本 skill,注意不要在项目里创建同名副本。)

## 文件说明

- `SKILL.md`:路由与使用规则(核心规则、路由表、回答模式、维护方式)
- `references/examples.md`:回答模式正反例(按需读取)
