import unittest

from generate_edgetunnel import GROUP, POLICY, generate


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
        for source in ("<html>Error</html>", self.source + "[Rule]\n", self.source.replace("PROXY", "DIRECT")):
            with self.subTest(source=source), self.assertRaises(ValueError):
                generate(source)

    def test_group_collision_rejected(self):
        with self.assertRaises(ValueError):
            generate(self.source.replace("[Proxy Group]", "[Proxy Group]\n" + POLICY))
