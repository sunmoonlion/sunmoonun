# agy 回执

- 对应请求：../request.md
- 本轮：第1轮
- 实际检查版本：
  - `#128` 补发候选（`luna-128-match-clarification` 分支）：
    - `knowbench-app`：`4b37b6482eb312b2d68bba4796f8f7a6ef199c5d`（基线 `7db654728697a89860584a593b228f158669dc3c`，`knowbench-backend` `2ec1c338c2f1b3941c44f55470fa50a4f887c040` 与 `knowbench-admin-frontend` `33559e926c3ebb7570716d5bb318b5a014e0d645` 指针不变）
    - `knowbench-app/knowbench-web-frontend`：`ecc32a199eff196e2be53e3164e28d5a0252c433`（基线 `88514dd74794aa03e87f60ff07e2fdab23b8eaf1`）
  - 日常开发线同步提交（`luna` 分支）：
    - `knowbench-app`：`a6eb090ef0c83fc3028aebd834a9b9061ff2e399`
    - `knowbench-app/knowbench-web-frontend`：`d27e6be9e6670c26927d803fc45fdf5ee4a0da19`（含追问作答 `935a88b` 与侧栏刷新修复 `d27e6be`）
- 结论：通过（适用 `#128` 仅更新 KnowBench Web 镜像及日常开发线同步；线上既有澄清任务无扣费界面核对归发布后执行）

## 发现

- F01（无阻塞问题，匹配澄清下方就地作答、费用上限与失败重试核查通过）：核查 `formal-expert-start.tsx`、`ask-expert-screen.tsx` 与 `formal-expert-intake.tsx`，`MatchClarification` 在匹配结果含 `clarification` 时展示回答输入框与提交按钮；空白回答不可提交且输入期间不发起请求；提交复用既有 v5 `FIND_EXPERT` 修订契约，关联原任务 `revises` 编号与本轮 `¥2` 费用上限，默认仅合并用户原问题与用户回答（不自动拼入模型建议项），超过 `2,000` 字符时提示缩短或由用户显式勾选以回答改写本轮需求；网络异常保留已填回答并沿用同一幂等键重试，成功后跳至新轮次并在旧轮次展示最新修订链接，专家执行仍由用户独立确认。
- F02（无阻塞问题，严格 CSP 下首屏侧栏宽度与登录容器样式修复核查通过）：核查 `sidebar.tsx` 与 `session-boundary.tsx`，移除了在严格 `style-src` 内容安全策略下会被浏览器拦截的服务端输出内联样式，首屏与刷新阶段改由样式类 `w-60 max-w-[calc(100%_-_2.5rem)] min-w-0 shrink-0` 限定侧栏宽度，客户端挂载后及拖拽调整时通过 DOM `ref` 设置像素宽度，登录挂载节点的显隐亦改为样式类控制，未放宽 CSP 规则。

## 验证

- 验证环境：本地 `wsl-dev`，通过 `git worktree add --detach` 建立临时隔离目录验证 `ecc32a199eff196e2be53e3164e28d5a0252c433`。
- 已执行并通过：
  1. `pnpm run typecheck`：通过；
  2. `pnpm run check:i18n`：通过（`1796` 对称键）；
  3. `pnpm exec vitest run --maxWorkers=3`：**66 个测试文件、490 项通过、2 项跳过**（其中 `tests/component/ask-expert-data.test.tsx` 5 项全部通过，`tests/component/feature-boundaries.test.ts` 17 项全部通过）；
  4. 代码核查 `tests/e2e/expert-sidebar.e2e.ts` 覆盖长项目名称、刷新已完成匹配、调宽重载、折叠重载及窄屏展开场景。
- 未运行与依赖条件：未发起任何真实付费模型调用，未在 `#128` 线上环境实操（待 Cursor 更新 KnowBench Web 镜像后由 Luna 在现场用已有澄清任务做不提交扣费的界面与侧栏刷新核对）。

## 交回

- 评审性质：只读代码评审与隔离环境复验，未修改任何被评代码，未切换主工位分支。
- 尚待处理项：由 Cursor 补发 `#128` KnowBench Web 镜像，随后由 Luna 完成现场既有澄清任务与侧栏布局核对。
- 提交与同步状态：本回执已提交本地 `wsl-dev` 的 `luna` 分支、未推送（执行 `sync.sh push sunmoonun` 时因 `sunmoonun` 工作区另有他人未提交改动被脚本预检拦停，按协作规范未夹带他人改动；待主工位处理未提交项后推送，另一端尚未更新）。
