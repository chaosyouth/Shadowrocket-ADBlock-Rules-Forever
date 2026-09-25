# Shadowrocket 自动优选配置

全部自定义配置位于 [custom/](custom/README.md)，与上游配置同名。

含策略组的懒人配置地址：
https://raw.githubusercontent.com/chaosyouth/Shadowrocket-ADBlock-Rules-Forever/release/custom/lazy_group.conf

之前的 `release/edgetunnel.conf` 地址继续可用，其内容与 `custom/lazy_group.conf` 相同。

1. 在 Shadowrocket 首页添加自己的 edgetunnel 节点订阅，将订阅备注设为 `edgetunnel`（小写）。该订阅需包含多个候选节点。
2. 在「配置」中下载上面的地址并使用配置，全局路由选择「配置」。
3. 在配置的代理分组中确认 `edgetunnel自动优选` 包含该订阅的节点；如果为空，检查订阅名称及节点是否已下载。
4. 应用分流组原来默认选择 PROXY 的位置现在使用自动优选；默认 DIRECT 的位置保持直连。仍可手动选择原有地区组。
5. 仓库文件更新后，手机还需要更新远程配置；Actions 不会主动让手机重新加载。

自动优选每 300 秒测试一次，超时 5 秒，容差 50 毫秒；按测试延迟与可用性选择，不是下载带宽测速，也不承诺已有连接无缝迁移。

Actions 每天北京时间 09:00（UTC 01:00）读取 Johnshall 的 release 分支根目录全部 `.conf`，在 `custom/` 生成同名配置，仅内容改变时提交。保留上游匹配条件、顺序、直连和拦截策略；有 PROXY 策略引用时添加自动优选组并替换引用。纯广告规则及纯直连配置不额外添加代理行为。节点地址和订阅令牌不写入此公开仓库。

上游新增配置会自动生成对应文件；上游删除配置时，移除 `custom/` 中对应的生成文件。全部输入校验通过后才写入输出。自定义转换逻辑统一维护在 `scripts/generate_edgetunnel.py`，不要直接编辑自动生成的 `.conf`，否则下一次生成会覆盖。

可在 Actions → Update edgetunnel configuration → Run workflow 手动更新。使用仓库自带 GITHUB_TOKEN，无需另设密钥。GitHub 定时任务可能延迟，公开仓库长期无活动时也可能被暂停。

原 release.yml 依赖本 Fork 不存在的 build 分支且会强推 release，已限制为仅在原作者仓库运行。本工作流不合并或执行上游脚本，只读取配置数据。

本地验证：
```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/generate_edgetunnel.py /path/to/upstream-release custom edgetunnel.conf
```
