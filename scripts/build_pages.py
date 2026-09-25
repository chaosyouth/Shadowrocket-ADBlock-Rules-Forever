"""Package generated configurations and a download index for GitHub Pages."""

from html import escape
from pathlib import Path
import shutil
import sys
from urllib.parse import quote

destination = Path(sys.argv[1])
(destination / "custom").mkdir(parents=True, exist_ok=True)
files = sorted(Path("custom").glob("*.conf"))
if not files:
    raise ValueError("No generated configurations to publish")
links = []
for source in files:
    shutil.copyfile(source, destination / "custom" / source.name)
    links.append(f'<li><a href="custom/{quote(source.name)}">{escape(source.name)}</a></li>')
shutil.copyfile("edgetunnel.conf", destination / "edgetunnel.conf")
(destination / "index.html").write_text(
    '<!doctype html><html lang="zh-CN"><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">'
    '<title>Shadowrocket CF 优选配置下载</title>'
    '<body><h1>Shadowrocket CF 优选配置</h1>'
    '<p>每天北京时间 09:00 自动生成并发布。仅加入 CF 自动优选，其余配置沿用上游。</p>'
    '<p>在 Shadowrocket 配置页面导入对应链接；节点订阅名称需为 EDGETUNNEL.CHAOSYOUTH.COM。</p>'
    '<p>常用：<a href="custom/lazy_group.conf">懒人配置（含策略组）</a></p>'
    '<ul>' + ''.join(links) + '</ul>'
    '<p>纯广告规则用于与其他规则配合使用。</p></body></html>\n', encoding="utf-8"
)
print(f"Packaged {len(files)} configurations and the legacy edgetunnel.conf alias")
