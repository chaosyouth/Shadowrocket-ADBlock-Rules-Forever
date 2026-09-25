# 自定义配置

[GitHub Pages 下载目录](https://chaosyouth.github.io/Shadowrocket-ADBlock-Rules-Forever/)

此目录保存根据上游全部 `.conf` 生成的个人版本，每天北京时间 **09:00** 更新。
配置保留原文件名与用途；含代理策略的版本使用当前本机配置中的 `节点选择 → 自动选择｜CF最优`。
订阅名称使用当前的 `EDGETUNNEL.CHAOSYOUTH.COM`，添加下表中的配置地址并使用配置。
[reference.json](reference.json) 只保存当前配置中的两个 CF 优选组，自动优选每 60 秒测试一次。只调整通用 PROXY 引用，其他应用组默认选择、DNS、IPv6、Hosts、分流及重写设置均保持上游配置。
纯广告规则不是完整的独立代理配置，需按其原用途与其他规则配合使用。

| 配置 | 导入地址 |
| --- | --- |
| 懒人配置（含策略组） | [lazy_group.conf](https://chaosyouth.github.io/Shadowrocket-ADBlock-Rules-Forever/custom/lazy_group.conf) |
| 懒人配置 | [lazy.conf](https://chaosyouth.github.io/Shadowrocket-ADBlock-Rules-Forever/custom/lazy.conf) |
| 仅去广告规则 | [sr_ad_only.conf](https://chaosyouth.github.io/Shadowrocket-ADBlock-Rules-Forever/custom/sr_ad_only.conf) |
| sr_adb 配置 | [sr_adb.conf](https://chaosyouth.github.io/Shadowrocket-ADBlock-Rules-Forever/custom/sr_adb.conf) |
| 回国规则 | [sr_backcn.conf](https://chaosyouth.github.io/Shadowrocket-ADBlock-Rules-Forever/custom/sr_backcn.conf) |
| 回国规则＋去广告 | [sr_backcn_ad.conf](https://chaosyouth.github.io/Shadowrocket-ADBlock-Rules-Forever/custom/sr_backcn_ad.conf) |
| 国内外划分 | [sr_cnip.conf](https://chaosyouth.github.io/Shadowrocket-ADBlock-Rules-Forever/custom/sr_cnip.conf) |
| 国内外划分＋去广告 | [sr_cnip_ad.conf](https://chaosyouth.github.io/Shadowrocket-ADBlock-Rules-Forever/custom/sr_cnip_ad.conf) |
| 全局直连＋去广告 | [sr_direct_banad.conf](https://chaosyouth.github.io/Shadowrocket-ADBlock-Rules-Forever/custom/sr_direct_banad.conf) |
| 全局代理＋去广告 | [sr_proxy_banad.conf](https://chaosyouth.github.io/Shadowrocket-ADBlock-Rules-Forever/custom/sr_proxy_banad.conf) |
| 黑名单规则 | [sr_top500_banlist.conf](https://chaosyouth.github.io/Shadowrocket-ADBlock-Rules-Forever/custom/sr_top500_banlist.conf) |
| 黑名单规则＋去广告 | [sr_top500_banlist_ad.conf](https://chaosyouth.github.io/Shadowrocket-ADBlock-Rules-Forever/custom/sr_top500_banlist_ad.conf) |
| 白名单规则 | [sr_top500_whitelist.conf](https://chaosyouth.github.io/Shadowrocket-ADBlock-Rules-Forever/custom/sr_top500_whitelist.conf) |
| 白名单规则＋去广告 | [sr_top500_whitelist_ad.conf](https://chaosyouth.github.io/Shadowrocket-ADBlock-Rules-Forever/custom/sr_top500_whitelist_ad.conf) |

新增文件以本目录实际内容为准。完整说明见 [EDGETUNNEL.md](../EDGETUNNEL.md)。
这些 `.conf` 是生成结果；个人设置请编辑 [reference.json](reference.json)，修改转换逻辑请编辑 [生成脚本](../scripts/generate_edgetunnel.py)，避免直接改生成文件后在每日更新时丢失。修改模板会自动触发重新生成，本机后续配置变动不会自动同步到模板。
