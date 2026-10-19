"""验证 AI 规则的业务覆盖及共享域名边界，不访问网络。"""
from pathlib import Path
import unittest

RULES = []
for raw in Path(__file__).with_name('ai.list').read_text().splitlines():
    line = raw.split('#', 1)[0].strip()
    if line:
        kind, domain = line.split(',')
        if kind not in ('DOMAIN', 'DOMAIN-SUFFIX'):
            raise ValueError(line)
        RULES.append((kind, domain))


def matches(host):
    return any(host == domain or (kind == 'DOMAIN-SUFFIX' and host.endswith('.' + domain))
               for kind, domain in RULES)


class AICoverage(unittest.TestCase):
    def test_common_services_and_dot_control(self):
        for host in (
            'api.openai.com', 'auth.openai.com', 'ws.chatgpt.com',
            'codex-cloud-backend.chatgpt.com', 'codex-cloud-environments.chatgpt.com',
            'cdn.oaistatic.com', 'files.oaiusercontent.com', 'chatgpt.livekit.cloud',
            'api.anthropic.com', 'platform.claude.com', 'claude.ai',
            'mcp-proxy.anthropic.com', 'bridge.claudeusercontent.com',
            'gemini.google.com', 'aistudio.google.com', 'notebooklm.google.com',
            'generativelanguage.googleapis.com', 'cloudcode-pa.googleapis.com',
            'cloudaicompanion.googleapis.com', 'api.githubcopilot.com',
            'api.individual.githubcopilot.com', 'copilot-proxy.githubusercontent.com',
            'copilot.microsoft.com', 'api2.cursor.sh', 'authenticate.cursor.sh',
            'marketplace.cursorapi.com', 'cdn.cursor-cdn.com', 'a.b.cursorvm.com',
            'api.perplexity.ai', 'openrouter.ai', 'grok.com', 'api.x.ai',
            'huggingface.co', 'cdn.hf.co', 'app.hf.space',
        ):
            with self.subTest(host=host):
                self.assertTrue(matches(host))

    def test_shared_providers_and_suffix_lookalikes_remain_outside(self):
        for host in ('google.com', 'www.google.com', 'mail.google.com', 'youtube.com',
                     'storage.googleapis.com', 'github.com', 'api.github.com',
                     'raw.githubusercontent.com', 'cloudflare.com', 'example.azureedge.net',
                     'example.blob.core.windows.net', 'auth0.com', 'notopenai.com',
                     'openai.com.example.org', 'unrelated.livekit.cloud'):
            with self.subTest(host=host):
                self.assertFalse(matches(host))

    def test_unique_and_syntax(self):
        self.assertEqual(len(RULES), len(set(RULES)))
        for _, host in RULES:
            self.assertEqual(host, host.lower())
            self.assertNotIn('*', host)
            self.assertNotIn('/', host)
            self.assertNotIn(':', host)


if __name__ == '__main__':
    unittest.main()
