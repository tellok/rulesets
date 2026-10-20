"""固定出口列表只收纳用户明确指定的网站。"""
from pathlib import Path
import unittest
from scripts.generate_singbox import convert


class StableExitTests(unittest.TestCase):
    def test_sites_subdomains_and_lookalike_boundaries(self):
        source = Path(__file__).with_name('stable_exit.list').read_text()
        rules = convert(source)['rules']
        suffixes = [domain for rule in rules for domain in rule.get('domain_suffix', [])]
        self.assertEqual(suffixes, ['hilldisk.com', 'ssdwp.com'])
        def matches(host):
            return any(host == name or host.endswith('.' + name) for name in suffixes)
        for host in ['hilldisk.com', 'www.hilldisk.com', 'ssdwp.com', 'www.ssdwp.com']:
            self.assertTrue(matches(host), host)
        for host in ['nothilldisk.com', 'hilldisk.com.example.org', 'notssdwp.com', 'example.com']:
            self.assertFalse(matches(host), host)


if __name__ == '__main__':
    unittest.main()
