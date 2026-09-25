# Shadowrocket 自动优选配置

全部自定义配置位于 [custom/](custom/README.md)，与上游配置同名。

含策略组的懒人配置地址：
https://raw.githubusercontent.com/chaosyouth/Shadowrocket-ADBlock-Rules-Forever/release/custom/lazy_group.conf

之前的 `release/edgetunnel.conf` 地址继续可用，其内容与 `custom/lazy_group.conf` 相同。

参考模板来自 2026-09-25 本机实际启用的 `cf-auto-local.conf`，保存在 [custom/reference.json](custom/reference.json)。其中仅包含通用设置、策略组和 Hosts，不包含节点认证信息、订阅令牌、HTTPS 解密证书及口令。

1. 在 Shadowrocket 首页添加自己的 edgetunnel 节点订阅，订阅名称与当前配置一致，为 `EDGETUNNEL.CHAOSYOUTH.COM`。该订阅需包含多个候选节点。
2. 在「配置」中下载上面的地址并使用配置，全局路由选择「配置」。
3. 在配置的代理分组中确认 `自动选择｜CF最优` 包含该订阅的节点；如果为空，检查订阅名称及节点是否已下载。
4. `节点选择` 默认使用 `自动选择｜CF最优`，同时保留手动 PROXY 选项。应用组使用当前参考模板的默认选择；苹果服务和哔哩哔哩默认 DIRECT，其余代理应用组默认节点选择。仍可手动选择地区组。
5. 仓库文件更新后，手机还需要更新远程配置；Actions 不会主动让手机重新加载。

自动优选每 60 秒测试一次，超时 5 秒，容差 50 毫秒；按测试延迟与可用性选择，不是下载带宽测速，也不承诺已有连接无缝迁移。通用设置沿用当前 DNS、IPv6 开启、block-quic=all-proxy 等偏好。

Actions 每天北京时间 09:00（UTC 01:00）读取 Johnshall 的 release 分支根目录全部 `.conf`，在 `custom/` 生成同名配置，仅内容改变时提交。保留上游规则匹配条件、顺序、DIRECT 和 REJECT 策略；PROXY 规则改为节点选择。完整配置叠加参考模板的通用设置和 Hosts；含代理策略或已有代理组时叠加模板策略组，同名组以个人模板为准，上游新增组保留。纯广告规则保持仅规则格式，纯直连配置不额外加入代理组。

上游新增配置会自动生成对应文件；上游删除配置时，移除 `custom/` 中对应的生成文件。全部输入校验通过后才写入输出。个人设置编辑 `custom/reference.json`；转换逻辑维护在 `scripts/generate_edgetunnel.py`。不要直接编辑自动生成的 `.conf`，否则下一次生成会覆盖。修改 reference.json 后会自动触发重新生成；本机 Shadowrocket 后续改动不会自行同步到此模板。

可在 Actions → Update edgetunnel configuration → Run workflow 手动更新。使用仓库自带 GITHUB_TOKEN，无需另设密钥。GitHub 定时任务可能延迟，公开仓库长期无活动时也可能被暂停。

原 release.yml 依赖本 Fork 不存在的 build 分支且会强推 release，已限制为仅在原作者仓库运行。本工作流不合并或执行上游脚本，只读取配置数据。

本地验证：
```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/generate_edgetunnel.py /path/to/upstream-release custom edgetunnel.conf
```
