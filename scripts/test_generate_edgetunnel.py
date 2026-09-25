import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from generate_edgetunnel import GROUP, REFERENCE_PATH, generate, generate_all


def entries(text, section):
    result = []
    active = False
    for line in text.splitlines():
        if line.startswith('['):
            active = line == section
        elif active and line.strip() and not line.startswith('#'):
            result.append(line)
    return result


class GenerateTest(unittest.TestCase):
    source = '''[General]
dns-server = system
upstream-new-setting = true
[Proxy Group]
媒体 = select,DIRECT,PROXY,香港节点,select=1
香港节点 = url-test,policy-regex-filter=HK
[Rule]
DOMAIN,example.com,媒体
DOMAIN,proxy.example,DIRECT
DOMAIN,ads.example,REJECT
IP-CIDR,1.0.0.0/8,PROXY,no-resolve
FINAL,PROXY
[Host]
example.com = 1.2.3.4
'''

    def test_rule_matches_and_order_preserved(self):
        result = generate(self.source)
        self.assertEqual(entries(result, '[Rule]'), [line.replace(',PROXY', ',' + GROUP) for line in entries(self.source, '[Rule]')])
        self.assertIn(f'媒体 = select,DIRECT,{GROUP},香港节点,select=1', result)
        self.assertEqual(result, generate(self.source))

    def test_current_settings_and_groups_applied(self):
        result = generate(self.source)
        ref = json.loads(REFERENCE_PATH.read_text())
        for key, section in [('general', '[General]'), ('groups', '[Proxy Group]'), ('hosts', '[Host]')]:
            actual = dict(line.split(' = ', 1) for line in entries(result, section))
            for name, value in ref[key].items():
                self.assertEqual(actual[name], value)
        self.assertIn('upstream-new-setting = true', result)
        self.assertIn('example.com = 1.2.3.4', result)
        self.assertIn('select,自动选择｜CF最优,PROXY,policy-select-name=自动选择｜CF最优', result)
        self.assertNotIn('select,自动选择｜CF最优,节点选择', result)
        self.assertIn('interval=60,tolerance=50,timeout=5', result)
        self.assertIn('policy-select-name=DIRECT', result)

    def test_invalid_source_rejected(self):
        for source in ('<html>Error</html>', self.source + '[Rule]\n'):
            with self.subTest(source=source), self.assertRaises(ValueError):
                generate(source)

    def test_group_without_section_added(self):
        result = generate('[General]\n[Rule]\nFINAL,Proxy\n')
        self.assertIn('[Proxy Group]', result)
        self.assertIn(f'FINAL,{GROUP}', result)

    def test_pure_rules_and_direct_configs_keep_purpose(self):
        source = '[Rule]\nDOMAIN-SUFFIX,proxy.example,Reject\n'
        result = generate(source)
        self.assertTrue(result.endswith(source))
        self.assertNotIn('[Proxy Group]', result)
        self.assertNotIn('[General]', result)
        direct = generate('[General]\n[Rule]\nFINAL,DIRECT\n')
        self.assertNotIn('[Proxy Group]', direct)
        self.assertEqual(entries(direct, '[Rule]'), ['FINAL,DIRECT'])

    def test_batch_and_validation_before_writing(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source, dest, legacy = root / 'source', root / 'custom', root / 'edgetunnel.conf'
            source.mkdir()
            dest.mkdir()
            (source / 'lazy_group.conf').write_text(self.source)
            (source / 'new.conf').write_text('[Rule]\nFINAL,PROXY\n')
            (dest / 'removed.conf').write_text('old')
            (dest / 'reference.json').write_text('keep')
            generate_all(source, dest, legacy)
            self.assertEqual({p.name for p in dest.glob('*.conf')}, {'lazy_group.conf', 'new.conf'})
            self.assertEqual(legacy.read_bytes(), (dest / 'lazy_group.conf').read_bytes())
            self.assertEqual((dest / 'reference.json').read_text(), 'keep')
            before = legacy.read_bytes()
            (source / 'new.conf').write_text('invalid upstream response')
            with self.assertRaises(ValueError):
                generate_all(source, dest, legacy)
            self.assertEqual(legacy.read_bytes(), before)

    def test_reference_contains_no_credentials(self):
        ref = json.loads(REFERENCE_PATH.read_text())
        self.assertEqual(set(ref), {'general', 'groups', 'hosts'})
        self.assertNotIn('ca-p12', json.dumps(ref))
        self.assertNotIn('password=', json.dumps(ref))
