# rulesets

## AI 分流

`ai.list` 覆盖 OpenAI/ChatGPT/Codex、Claude、Gemini/AI Studio/NotebookLM/Code Assist、GitHub/Microsoft Copilot、Cursor、Perplexity、OpenRouter，并保留 Grok/xAI 和 Hugging Face。

Codex/Dotty 的 `ws.chatgpt.com`、`codex-cloud-backend.chatgpt.com`、`codex-cloud-environments.chatgpt.com` 由 `chatgpt.com` 后缀覆盖。`oaistatic.com`、`oaiusercontent.com` 和限定的 LiveKit 域名覆盖静态资源、文件和已知相关服务。实际来源及边界记录在列表注释中；域名后缀同时匹配主域与其子域。

共享云平台尽量使用精确主机，保留一般 Google、GitHub、Cloudflare、Azure 分流；例如 GitHub 通用登录/API 不因使用 Copilot 就全部转为 AI。Gemini 所需 OAuth/项目管理的精确 Google API 主机也可能被其他 Cloud 应用使用。

该列表只负责域名匹配。Dotty 的 WebRTC 若直接访问真实公网 IP，仍需要客户端/路由器的 UDP/IP 接管能力；不把排查时的临时媒体 IP 固定进公共列表，也不能保证所有第三方 MCP、代理商或自定义网关都归入 AI。

客户端须让此规则优先于普通 Google、CN、OpenAI 订阅规则并指向 `AI` 策略组。Surge 可以直接引用远程 `.list`；sing-box 可以引用本仓库自动生成的远程 JSON 并定期更新。旧的本地/内嵌配置需要先迁移一次。

验证：`python3 test_ai.py`（业务覆盖、后缀边界和语法/去重），另需在实际代理核心校验并观察命中。

## sing-box 自动生成与订阅

根目录的 `.list` 为唯一维护源。GitHub Actions 在 main 的列表、生成脚本、测试或工作流变更后，运行测试并生成 `sing-box/<原文件名>.json`，只有产物变化才由机器人提交到 main。Pull Request 只验证，不写仓库；也可以在 Actions 中手动运行。生成提交不匹配触发路径，且 GITHUB_TOKEN 推送不会递归触发工作流。不要手工编辑生成 JSON。

本地生成及验证：

```sh
python3 -m unittest discover -p 'test_*.py'
python3 scripts/generate_singbox.py
```

支持 DOMAIN、DOMAIN-SUFFIX、DOMAIN-KEYWORD、IP-CIDR、IP-CIDR6 和 PROCESS-NAME；IP 规则允许 no-resolve。未知类型/选项、空列表和无效 CIDR 会阻止整批发布，避免静默漏规则。每种字段独立成一条 headless rule，保留不同类型之间的 OR 语义；JSON 使用 version=1，当前字段不需要更高格式版本。只转换格式和去重，不添加策略或扩大域名范围。

Surge 示例（策略组 `AI` 需已存在）：

```ini
RULE-SET,https://raw.githubusercontent.com/tellok/rulesets/main/ai.list,AI,update-interval=86400
```

sing-box 的 `route.rule_set` 示例：

```json
{
  "type": "remote",
  "tag": "AI",
  "format": "source",
  "url": "https://raw.githubusercontent.com/tellok/rulesets/main/sing-box/ai.json",
  "download_detour": "Final",
  "update_interval": "1d"
}
```

同时在 `route.rules` 中声明 `{"rule_set":["AI"],"action":"route","outbound":"AI"}`，并启用 `experimental.cache_file.enabled` 持久化缓存。`Final`、`AI` 需由客户端配置定义，更新下载路径由客户端决定。以上下载字段沿用当前 adapter 的 sing-box 1.14 配置；上游已弃用 download_detour，后续升级至 1.16 前需迁移到 http_client。

一天是客户端运行时的更新间隔，设备休眠/断网不保证准时更新；首次无缓存启动需要可访问 GitHub Raw。更新列表不更新节点，不修改客户端策略选择或既有连接。原始 `.list` 与生成 JSON 两次提交之间，以及 Raw CDN 传播时，可能短暂不同步；Actions 失败时 JSON 保持最后成功版本，修正源后重新运行。

依据：[Surge Rule Sets](https://manual.nssurge.com/rules/ruleset.html)、[sing-box rule-set](https://sing-box.sagernet.org/configuration/rule-set/)、[GitHub 工作流触发规则](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)。

## 固定出口网站

`stable_exit.list` 收纳用户指定的需稳定出口的网站，目前为 `hilldisk.com`、`ssdwp.com`（含子域）。这是用户反馈的会话稳定需求，不是对网站服务端认证机制的断言。Actions 自动生成 `sing-box/stable_exit.json`，客户端按一天间隔更新。

搭配 `Stable_Exit` 手动选择组，候选只放具体代理节点，不能把 SG/Final/Proxies 等会自动换节点的组放进去。节点失效时保留选择，由用户手动换节点；这避免自动测速/故障切换改变出口，但不保证服务商不会调整同一节点的出口IP，也不保证Cookie永不过期。列表内网站共享一个固定节点；若将来需要每站不同出口，应拆为多个策略组。

Surge：`RULE-SET,https://raw.githubusercontent.com/tellok/rulesets/main/stable_exit.list,Stable_Exit,update-interval=86400`。sing-box使用对应JSON远程规则集并路由到Stable_Exit，update_interval为1d。放在普通业务/CN/兜底规则之前；客户端的DNS、必要私网/iOA保护规则按原配置保留。切换或首次加载可能改变这两个站的出口，宜在选择好节点后重新登录。
