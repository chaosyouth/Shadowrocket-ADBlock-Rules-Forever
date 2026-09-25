# Shadowrocket CF 自动优选配置

下载目录：https://chaosyouth.github.io/Shadowrocket-ADBlock-Rules-Forever/

全部生成文件位于 [custom/](custom/README.md)，与上游配置同名。

含策略组的懒人配置地址：
https://chaosyouth.github.io/Shadowrocket-ADBlock-Rules-Forever/custom/lazy_group.conf

之前的 `release/edgetunnel.conf` 地址继续可用，其内容与 `custom/lazy_group.conf` 相同。

## 仅叠加 CF 优选

参考当前本机 `cf-auto-local.conf` 的 CF 优选逻辑，在 [custom/reference.json](custom/reference.json) 中只保留两个组：

- `节点选择`：默认使用 `自动选择｜CF最优`，保留手动 `PROXY` 选项。
- `自动选择｜CF最优`：使用订阅 `EDGETUNNEL.CHAOSYOUTH.COM`，每 60 秒检测，超时 5 秒，容差 50 毫秒。

生成时，仅将上游规则和应用组中的通用 `PROXY` 引用接入 `节点选择`；若应用组按名称默认选择 PROXY，该引用也随之调整。应用组的候选顺序、默认选择位置、地区组、规则匹配与顺序均保持上游设定。

**DNS、IPv6、QUIC、Hosts、URL 重写、MITM 等其他设置全部沿用上游，不叠加本机设置。** 无代理引用的纯广告规则或直连配置不添加 CF 策略组。若上游出现同名 CF 组，生成失败并保留已发布配置，避免覆盖上游设置。

## 使用和更新

1. 在 Shadowrocket 首页添加自己的节点订阅，订阅名称为 `EDGETUNNEL.CHAOSYOUTH.COM`，订阅中需有多个候选节点。
2. 在「配置」中下载并使用上面的配置地址，全局路由选择「配置」。
3. 确认 `自动选择｜CF最优` 包含候选节点。测速由客户端执行，按延迟与可用性选择，不等同于最大下载带宽，也不保证旧连接无缝迁移。
4. 仓库更新后，客户端仍需更新远程配置。

Actions 每天北京时间 **09:00**（UTC 01:00）读取 Johnshall 的 release 分支根目录所有 `.conf`，生成同名自定义版本，内容变化才提交；随后通过 GitHub Actions 部署到 GitHub Pages。上游新增、删除配置时同步调整输出。全部输入校验通过后才写入输出；读取上游配置数据，不执行上游脚本。

修改 CF 设置请编辑 `custom/reference.json`，提交后会自动重新生成。不要直接修改生成的 `.conf`，否则下一次生成会覆盖。本机配置后续变化不会自动同步到模板。

可在 Actions → Update edgetunnel configuration → Run workflow 手动更新。无需另设密钥；GitHub 定时任务可能延迟，公开仓库长期无活动时可能暂停。原 release.yml 已限制仅在原作者仓库运行，以避免缺失 build 分支导致失败及强推 release。

本地验证：
```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/generate_edgetunnel.py /path/to/upstream-release custom edgetunnel.conf
```
