import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from generate_edgetunnel import GROUP, REFERENCE_PATH, PAGES_URL, generate, generate_all, with_update_url


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

    def test_only_cf_groups_added(self):
        result = generate(self.source)
        ref = json.loads(REFERENCE_PATH.read_text())
        actual = dict(line.split(' = ', 1) for line in entries(result, '[Proxy Group]'))
        for name, value in ref['groups'].items():
            self.assertEqual(actual[name], value)
        self.assertEqual(len(actual), 4)
        self.assertEqual(actual['香港节点'], 'url-test,policy-regex-filter=HK')
        for section in ('[General]', '[Host]'):
            self.assertEqual(entries(result, section), entries(self.source, section))
        self.assertIn('select,自动选择｜CF最优,PROXY,policy-select-name=自动选择｜CF最优', result)
        self.assertNotIn('select,自动选择｜CF最优,节点选择', result)
        self.assertIn('interval=60,tolerance=50,timeout=5', result)

    def test_application_defaults_and_other_sections_preserved(self):
        source = self.source.replace('select=1', 'select=0,policy-select-name=DIRECT')
        source += '[URL Rewrite]\n^https://example.com https://example.org 302\n[MITM]\nenable = false\n'
        result = generate(source)
        self.assertIn('select=0,policy-select-name=DIRECT', result)
        for section in ('[General]', '[Host]', '[URL Rewrite]', '[MITM]'):
            self.assertEqual(entries(result, section), entries(source, section))
        selected = generate(self.source.replace('select=1', 'policy-select-name=PROXY'))
        self.assertIn('policy-select-name=节点选择', selected)

    def test_conflicting_upstream_group_rejected(self):
        with self.assertRaises(ValueError):
            generate(self.source.replace('媒体 =', '节点选择 ='))

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
            self.assertEqual(legacy.read_text(), with_update_url((dest / 'lazy_group.conf').read_text(), 'edgetunnel.conf'))
            for filename in ('lazy_group.conf', 'new.conf'):
                self.assertIn('update-url = ' + PAGES_URL + 'custom/' + filename, (dest / filename).read_text())
            self.assertEqual((dest / 'reference.json').read_text(), 'keep')
            before = legacy.read_bytes()
            (source / 'new.conf').write_text('invalid upstream response')
            with self.assertRaises(ValueError):
                generate_all(source, dest, legacy)
            self.assertEqual(legacy.read_bytes(), before)

    def test_reference_contains_no_credentials(self):
        ref = json.loads(REFERENCE_PATH.read_text())
        self.assertEqual(set(ref), {'groups'})
        self.assertNotIn('ca-p12', json.dumps(ref))
        self.assertNotIn('password=', json.dumps(ref))

    def test_update_url_replaces_existing_and_is_idempotent(self):
        source = self.source.replace('[General]', '[General]\nupdate-url = https://old.example/a.conf\nUPDATE-URL=https://old.example/b.conf')
        result = with_update_url(source, 'custom/lazy_group.conf')
        urls = [line for line in entries(result, '[General]') if line.startswith('update-url')]
        self.assertEqual(urls, ['update-url = ' + PAGES_URL + 'custom/lazy_group.conf'])
        self.assertEqual(result, with_update_url(result, 'custom/lazy_group.conf'))
        self.assertEqual(entries(result, '[Rule]'), entries(source, '[Rule]'))

    def test_update_url_added_to_rule_only_config(self):
        source = '[Rule]\nDOMAIN,ads.example,REJECT\n'
        result = with_update_url(source, 'custom/sr_ad_only.conf')
        self.assertEqual(entries(result, '[General]'), ['update-url = ' + PAGES_URL + 'custom/sr_ad_only.conf'])
        self.assertEqual(entries(result, '[Rule]'), entries(source, '[Rule]'))
