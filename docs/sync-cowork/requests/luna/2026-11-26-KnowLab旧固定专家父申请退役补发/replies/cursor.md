# Cursor 回执

- 对应请求：../request.md
- 本轮：第 1 轮（未完成发布）
- 结论：部分完成。发布分支已推到 GitHub；Jenkins 发布未启动。受阻于本机执行环境无法取得宿主机权限，且 Docker / Jenkins / KIND 在当前会话中不可达。

## 已完成

- 核对候选：KnowLab 父仓 `3857400992ae70ea19e0d118e9cf4550a69aaa49`，后端 `8ddff9028ff360c106597e645f74c9ae86ed9c99`，Web / Admin 仍为 #123 的 `b681780` / `89fe3ac`。相对 #123 仅多一个后端提交「统一过滤已退役固定包的父申请」。
- 从 #123 回执 `15b34d38034bbe5f91e17c33d6b9a0d3f1bf0299` 拉出发布分支 `knowlab-parent-retire-20261126`。
- GitHub 已收到：
  - `sunmoonun` → `15b34d380…`（`knowlab-parent-retire-20261126`）
  - `knowlab-app` → `385740099…`（同名分支）
  - `knowlab-backend` 的 `origin/luna` 尖端已是 `8ddff902…`
- Gitee 经当前会话代理推送返回 403，未写入镜像站。流水线若稍后能在宿主侧推送，可再补。

## 受阻

- `make jenkins-release-run` 依赖 `sudo -n nsenter --target 1 …`。当前 Cursor Shell 带 no-new-privileges，sudo 失败：`/etc/sudo.conf is owned by uid 65534` / `The "no new privileges" flag is set`。请求 `required_permissions: ["all"]` 后仍落在沙箱，未能进入宿主命名空间。
- 同会话内：`/var/run/docker.sock` 不存在；`https://jenkins.dev.sunmoonai.com:30443/` 不可达；`kubectl` 连 `127.0.0.1:27443` 被拒绝；`/mnt/sunmoon-data/jenkins` 存在但 Permission denied。无法核对消费进程或启动 #124。
- 宿主代理配置仍指向 `192.168.32.1:7890`，与当前网关不符；GitHub 仅能经 Cursor 沙箱本地代理访问。

## 待宿主恢复后执行

```text
make -C infrastructure jenkins-release-run \
  RELEASE_BRANCH=knowlab-parent-retire-20261126 \
  APPS=knowlab \
  PIN=heads \
  NOTE='KnowLab旧固定专家父申请退役补发，沿用#123前端与库版本' \
  APPROVAL_TIMEOUT_MINUTES=180
```

发布成功后按惯例更新使用 KnowLab 后端镜像的 API / worker / scheduler，将构建号、镜像摘要、晋级指针、就绪与时间补入本回执；业务验收仍由 Luna 做。
