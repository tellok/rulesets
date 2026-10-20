import json
from pathlib import Path
import tempfile
import unittest
from scripts.generate_singbox import convert, generate


class GeneratorTests(unittest.TestCase):
    def test_mixed_rules_are_alternatives_and_deduplicated(self):
        result = convert('DOMAIN,a.example\nDOMAIN,a.example\nDOMAIN-SUFFIX,b.example\nIP-CIDR,192.0.2.1/24,no-resolve\nIP-CIDR6,2001:db8::1/32\nPROCESS-NAME,Example\n')
        self.assertEqual(result['rules'], [
            {'domain': ['a.example']}, {'domain_suffix': ['b.example']},
            {'ip_cidr': ['192.0.2.0/24', '2001:db8::/32']}, {'process_name': ['Example']}])

    def test_invalid_input_is_rejected(self):
        for text in ['URL-REGEX,foo', 'DOMAIN,', 'DOMAIN,x,Policy', 'DOMAIN,x,extended-matching',
                     'IP-CIDR,not-an-ip', 'IP-CIDR6,192.0.2.0/24', '# empty']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                convert(text)

    def test_generation_is_deterministic_removes_stale_and_does_not_publish_invalid(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'a.list').write_text('DOMAIN,a.example')
            generate(root)
            output = root / 'sing-box/a.json'
            original = output.read_bytes()
            generate(root)
            self.assertEqual(original, output.read_bytes())
            (root / 'sing-box/stale.json').write_text('{}')
            generate(root)
            self.assertFalse((root / 'sing-box/stale.json').exists())
            (root / 'a.list').write_text('DOMAIN,changed.example')
            (root / 'z.list').write_text('INVALID,x')
            with self.assertRaises(ValueError):
                generate(root)
            self.assertEqual(original, output.read_bytes())

    def test_all_repository_lists_convert(self):
        for path in Path(__file__).parent.glob('*.list'):
            with self.subTest(path=path.name):
                self.assertTrue(convert(path.read_text())['rules'])


if __name__ == '__main__':
    unittest.main()
