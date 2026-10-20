import json
from pathlib import Path
import re
import unittest
from scripts.generate_rewrites import convert, mitm_hosts, render

ROOT = Path(__file__).parent
SOURCE = ROOT / 'rewrites/cinder_f271.redirector.json'


def rewrite(rule, url):
    line = convert(rule)
    if line is None:
        return None
    pattern, target, mode = line.split()
    match = re.search(pattern, url)
    if match is None:
        return None
    return re.sub(r'\$(\d+)', lambda m: match.group(int(m[1])) or '', target)


def chain(rules, url):
    visited = {url}
    for _ in range(12):
        target = next((v for rule in rules if (v := rewrite(rule, url)) is not None), None)
        if target is None:
            return url
        if target in visited:
            raise AssertionError('redirect loop: ' + target)
        visited.add(target)
        url = target
    raise AssertionError('too many redirects')


class RewriteTests(unittest.TestCase):
    def setUp(self):
        self.rules = json.loads(SOURCE.read_text())

    def test_generated_files_match_source_and_have_no_singbox_output(self):
        text, module = render('cinder_f271', self.rules)
        self.assertEqual(SOURCE.with_name('cinder_f271.list').read_text(), text)
        self.assertEqual(SOURCE.with_name('cinder_f271.sgmodule').read_text(), module)
        self.assertEqual(len(self.rules), 54)
        self.assertIn('[URL Rewrite]', text)
        self.assertFalse((ROOT / 'sing-box/cinder_f271.json').exists())

    def test_exclude_preserves_group_number_and_case_insensitivity(self):
        rule = self.rules[8]
        self.assertIsNone(rewrite(rule, 'https://www.sis001.com/bbs/thread-12345-1-1.html'))
        self.assertEqual(rewrite(rule, 'HTTPS://WWW.SIS001.COM/bbs/thread-12345-2-1.html'),
                         'https://www.sis001.com/bbs/thread-12345-1-1.html')

    def test_extra_rules_chains_query_and_canonical_idempotence(self):
        pairs = {
            'https://www.sis001.com/forum/viewthread.php?tid=123&x=1': 'https://www.sis001.com/bbs/viewthread.php?tid=123&x=1',
            'https://sis001.com/bbs/viewthread.php?tid=123': 'https://www.sis001.com/bbs/viewthread.php?tid=123',
            'https://www.sis001.com/bbs/thread-123-1-25.html?x=1': 'https://www.sis001.com/bbs/thread-123-1-1.html?x=1',
            'https://www.sis001.com/forum/thread-123-1-25.html': 'https://www.sis001.com/bbs/thread-123-1-1.html',
            'https://www.sis001.com/bbs/thread-123-1-1.html?x=1': 'https://www.sis001.com/bbs/thread-123-1-1.html?x=1',
            'https://unrelated.example/forum/x': 'https://unrelated.example/forum/x',
        }
        for start, target in pairs.items():
            with self.subTest(start=start):
                self.assertEqual(chain(self.rules, start), target)
                self.assertEqual(chain(self.rules, target), target)

    def test_prefix_partial_match_drops_suffix_like_redirector(self):
        rule = {'mode':'regex', 'from':r'^https://example\.com/path', 'to':'https://target.example/'}
        self.assertEqual(rewrite(rule, 'https://example.com/path?discard=1'), 'https://target.example/')
        rule['from'] = r'https://example\.com/(.*)'
        self.assertEqual(rewrite(rule, 'prefix:https://example.com/one'), 'https://target.example/')

    def test_unsupported_modes_and_pipeline_fail_explicitly(self):
        for rule in [dict(mode='url-pattern', **{'from':'https://example.com/:id', 'to':'https://target.example/'}),
                     dict(mode='regex', **{'from':r'^https://example.com/(.*)', 'to':'{{$1|decodeURIComponent}}'})]:
            with self.assertRaises(ValueError):
                convert(rule)
        self.assertIsNone(convert({'disabled': True}))

    def test_host_expansion_is_limited_to_enabled_https_sources(self):
        hosts = mitm_hosts(self.rules)
        self.assertIn('*.alma6874fe.cc', hosts)
        self.assertIn('www.level-plus.net', hosts)
        self.assertIn('sis001.com', hosts)
        self.assertNotIn('sc7ap.yj9ld.top', hosts)  # HTTP无需解密
        self.assertNotIn('*', hosts)


if __name__ == '__main__':
    unittest.main()
