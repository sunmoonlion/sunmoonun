# 方法能力作者入口限制复审

- 类型：评审；状态：待接手，已验证，未发布。
- 发起身份：luna；执行身份：qwen（承接已有评审，由所有者协调，不自动启动代理）。
- 主工位：远程 `/home/zym/worktrees/qwen`，分支 `qwen`。
- 回执：`replies/qwen.md`，评审方自行填写。

所有者已批准首批缺陷之后收敛公共机制/C2，并要求不保留兼容运行路径。本增量先落实评审所提“在公共机制就绪前不让作者继续产生旧能力绑定”，不是 C2 已完成。首批缺陷保持另一张卡及其确切提交，不改写其审阅范围。

| 仓 | 待评提交 |
| --- | --- |
| knowbench-app/knowbench-backend | `eb1465b56378bcef8bbe29cbb1f45ef184570d28` |
| knowlab-app/knowlab-backend | `e4c7633d75ef9efe7d011cba8fa5f1600bc74165` |
| knowlab-app/knowlab-web-frontend | `060ec11e39a6d02c4422ca7faec90d3b5eb752ab` |
| knowbench-app | `b4235db387d62a1801d833181b7a2aa33112a5a4` |
| knowlab-app | `cee838e9c9007160a8927a6c11f3f8f84cf2098a` |

请检查：

1. `managed_authoring.py` 与工作稿 store、compile/decompile、pack/manifest 校验共同拒绝固定、动态和引用方法中的非空 MCP/Skill 绑定；保存失败不覆盖原稿，导入/复制/冻结/出版本不能绕过。普通无绑定方法继续工作。
2. 作者目录先核所有者，再返回 `method_access_not_ready`，不访问个人能力目录；前端不再提供新增选择，不自动删除已有绑定，只有明确点击移除才提交清空。
3. 没有数据库迁移、部署、脚本启用或真实外部调用。KnowBench 的修改只是生成模型的模块说明变短，KnowLab 模型和摘要锁由提供方脚本生成，字段语义未变。
4. 方案 §17.7 的公共调用机制分解是否覆盖业务权限真源、可信操作定义、调用身份/幂等、审批与证据分工、旧范围失效及一次性迁移。它仍为待实现设计，不把它当上线能力。

验证：191 项服务/编译/契约、8 项 HTTP 路由、22 项前端通过。Python 全量 Ruff、Pyright、TypeScript、改动 ESLint、i18n 通过。日志 `/tmp/method-access-gate-{regression,routes,web,ruff,pyright,tsc,eslint,i18n}.log`。最初路由在受限沙箱中等待，已停止自己的测试并在沙箱外以 90 秒总时限重跑，2.39 秒通过；不将首次停滞算通过。

允许阅读、串行隔离测试、写本人回执。不要改候选代码、部署、发邮件或调用收费模型；发现问题交回修复。后续发布须基于 #93 隔离分支摘取适用提交并复验，不能整支发布 qwen 的其它未发布工作。
