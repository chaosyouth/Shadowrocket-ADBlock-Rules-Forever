import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from generate_edgetunnel import GROUP, POLICY, generate, generate_all


class GenerateTest(unittest.TestCase):
    source = """[General]
dns-server = system
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
"""

    def test_routes_and_defaults_preserved(self):
        result = generate(self.source)
        self.assertIn(f"媒体 = select,DIRECT,{GROUP},香港节点,select=1", result)
        self.assertIn(f"IP-CIDR,1.0.0.0/8,{GROUP},no-resolve", result)
        self.assertIn(f"FINAL,{GROUP}", result)
        for line in self.source.splitlines():
            if "PROXY" not in line:
                self.assertIn(line + "\n", result)
        self.assertEqual(result.count(POLICY), 1)
        self.assertEqual(result, generate(self.source))

    def test_invalid_source_rejected(self):
        for source in ("<html>Error</html>", self.source + "[Rule]\n"):
            with self.subTest(source=source), self.assertRaises(ValueError):
                generate(source)

    def test_group_collision_rejected(self):
        with self.assertRaises(ValueError):
            generate(self.source.replace("[Proxy Group]", "[Proxy Group]\n" + POLICY))

    def test_missing_group_added_for_proxy_rules(self):
        source = "[General]\ndns-server = system\n[Rule]\nDOMAIN,a.example,Proxy\nFINAL,DIRECT\n"
        result = generate(source)
        self.assertIn("[Proxy Group]\n" + POLICY + "\n\n[Rule]", result)
        self.assertIn(f"DOMAIN,a.example,{GROUP}", result)
        self.assertIn("FINAL,DIRECT", result)

    def test_pure_rules_and_direct_configs_keep_their_purpose(self):
        for source in ("[Rule]\nDOMAIN-SUFFIX,proxy.example,Reject\n", "[General]\n[Rule]\nFINAL,DIRECT\n"):
            result = generate(source)
            self.assertNotIn(POLICY, result)
            self.assertTrue(result.endswith(source))

    def test_batch_includes_all_inputs_and_preserves_legacy_url(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source, dest, legacy = root / "source", root / "custom", root / "edgetunnel.conf"
            source.mkdir()
            dest.mkdir()
            (source / "lazy_group.conf").write_text(self.source)
            (source / "new.conf").write_text("[Rule]\nFINAL,PROXY\n")
            (dest / "removed.conf").write_text("old")
            (dest / "README.md").write_text("keep")
            generate_all(source, dest, legacy)
            self.assertEqual({p.name for p in dest.glob("*.conf")}, {"lazy_group.conf", "new.conf"})
            self.assertEqual(legacy.read_bytes(), (dest / "lazy_group.conf").read_bytes())
            self.assertEqual((dest / "README.md").read_text(), "keep")
            before = legacy.read_bytes()
            (source / "new.conf").write_text("invalid upstream response")
            with self.assertRaises(ValueError):
                generate_all(source, dest, legacy)
            self.assertEqual(legacy.read_bytes(), before)
            self.assertIn(POLICY, (dest / "new.conf").read_text())
