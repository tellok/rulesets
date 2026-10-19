# rulesets

## AI 分流

`ai.list` 覆盖 OpenAI/ChatGPT/Codex、Claude、Gemini/AI Studio/NotebookLM/Code Assist、GitHub/Microsoft Copilot、Cursor、Perplexity、OpenRouter，并保留 Grok/xAI 和 Hugging Face。

Codex/Dotty 的 `ws.chatgpt.com`、`codex-cloud-backend.chatgpt.com`、`codex-cloud-environments.chatgpt.com` 由 `chatgpt.com` 后缀覆盖。`oaistatic.com`、`oaiusercontent.com` 和限定的 LiveKit 域名覆盖静态资源、文件和已知相关服务。实际来源及边界记录在列表注释中；域名后缀同时匹配主域与其子域。

共享云平台尽量使用精确主机，保留一般 Google、GitHub、Cloudflare、Azure 分流；例如 GitHub 通用登录/API 不因使用 Copilot 就全部转为 AI。Gemini 所需 OAuth/项目管理的精确 Google API 主机也可能被其他 Cloud 应用使用。

该列表只负责域名匹配。Dotty 的 WebRTC 若直接访问真实公网 IP，仍需要客户端/路由器的 UDP/IP 接管能力；不把排查时的临时媒体 IP 固定进公共列表，也不能保证所有第三方 MCP、代理商或自定义网关都归入 AI。

客户端须让此规则优先于普通 Google、CN、OpenAI 订阅规则并指向 `AI` 策略组。规则通常在转换时被内嵌，更新列表后应重新转换或重载，旧 JSON 不会自动变新。

验证：`python3 test_ai.py`（业务覆盖、后缀边界和语法/去重），另需在实际代理核心校验并观察命中。
