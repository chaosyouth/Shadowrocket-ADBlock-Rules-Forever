# Shadowrocket 自动优选配置

配置地址：
https://raw.githubusercontent.com/chaosyouth/Shadowrocket-ADBlock-Rules-Forever/release/edgetunnel.conf

1. 在 Shadowrocket 首页添加自己的 edgetunnel 节点订阅，将订阅备注设为 `edgetunnel`（小写）。该订阅需包含多个候选节点。
2. 在「配置」中下载上面的地址并使用配置，全局路由选择「配置」。
3. 在配置的代理分组中确认 `edgetunnel自动优选` 包含该订阅的节点；如果为空，检查订阅名称及节点是否已下载。
4. 应用分流组原来默认选择 PROXY 的位置现在使用自动优选；默认 DIRECT 的位置保持直连。仍可手动选择原有地区组。
5. 仓库文件更新后，手机还需要更新远程配置；Actions 不会主动让手机重新加载。

自动优选每 300 秒测试一次，超时 5 秒，容差 50 毫秒；按测试延迟与可用性选择，不是下载带宽测速，也不承诺已有连接无缝迁移。

Actions 每小时第 17 分钟读取 Johnshall 的 release/lazy_group.conf，仅内容改变时提交 edgetunnel.conf。保留上游匹配条件、顺序、直连和拦截策略，只添加自动优选组并替换 PROXY 策略引用。节点地址和订阅令牌不写入此公开仓库。

可在 Actions → Update edgetunnel configuration → Run workflow 手动更新。使用仓库自带 GITHUB_TOKEN，无需另设密钥。GitHub 定时任务可能延迟，公开仓库长期无活动时也可能被暂停。

原 release.yml 依赖本 Fork 不存在的 build 分支且会强推 release，已限制为仅在原作者仓库运行。本工作流不合并或执行上游脚本，只读取配置数据。

本地验证：
```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/generate_edgetunnel.py lazy_group.conf edgetunnel.conf
```
