import unittest
from pathlib import Path
from scripts.generate_singbox import convert


class DirectTests(unittest.TestCase):
    def test_plex_control_domains_and_subdomains_with_strict_boundaries(self):
        source=Path(__file__).with_name('direct.list').read_text()
        rules=convert(source)['rules']
        self.assertEqual(rules,[{'domain_suffix':['plex.tv','plex.bz','plex.direct']}])
        suffixes=rules[0]['domain_suffix']
        def matches(host): return any(host==d or host.endswith('.'+d) for d in suffixes)
        for host in ['v4.plex.tv','pubsub.plex.tv','pubsub02.pop.hnd.plex.bz','10-10-10-11.server.plex.direct']:
            self.assertTrue(matches(host),host)
        for host in ['notplex.tv','plex.tv.other.example','google.com','hilldisk.com']:
            self.assertFalse(matches(host),host)


if __name__=='__main__': unittest.main()
