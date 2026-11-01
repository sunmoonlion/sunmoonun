# 沙箱与供给器镜像源码（0003-sandbox）

每用户一个 pod：钉版 `codex app-server`（模型循环，BYOK）+ 沙箱侧出站桥（到会合点）。设计见
[`docs/design/SDD/modules/0003-sandbox.md`](../../../../docs/design/SDD/modules/0003-sandbox.md)。

| 目录 | 内容 |
| --- | --- |
| `image/` | `Dockerfile`、`entrypoint.sh`、`moonshot_responses.py`（Moonshot 空助理消息兼容）；运行版本由 Dockerfile 钉住 |
| `bridge/` | `sandbox_bridge.py`：回环 `ws://127.0.0.1:47002` ↔ 会合点 `/sandbox`，第一帧 hello |
| `provisioner/` | `provisioner.py`：沙箱供给器（FastAPI）——按用户建/查/删沙箱，直接调 API server；`tests/` 对假 API server 验 |

## 进程与端口

```text
pod
├── codex app-server --listen ws://0.0.0.0:47800 --ws-auth capability-token --ws-token-file /secrets/app-server/token   ← 工作台（唯一客户端）
│     CODEX_HOME=/data/codex（PVC）：config.toml、environments.toml（default=user-pc → ws://127.0.0.1:47002，include_local=false）、auth.json（BYOK）
└── sandbox_bridge.py  127.0.0.1:47002 ──出站──▶ 会合点 /sandbox（hello: user、token、codex 版本）
```

当配置中的供应商使用 `https://api.moonshot.cn/v1` 或 `https://api.moonshot.ai/v1` 的 Responses 接口时，
`moonshot_responses.py` 在本 Pod 的随机回环端口转发模型 HTTP/SSE 请求，并作为 app-server 的父进程传递退出信号。
其他供应商直接启动原有 app-server。认证值只随原请求转发，不写日志或新增凭据文件；TLS 校验保持开启，不跟随重定向。

2026-11-02 已复现：Kimi 可能在 `function_call` 后返回空的 assistant message；Codex 原样回传该消息和匹配的
`function_call_output` 时，Kimi 返回 400，并错误地要求 `工具名:序号`。同一请求重放两次均失败；只删除空消息即 200。
因此仅从发往 Moonshot 的 Responses `input` 中过滤无内容、无引用、无拒绝和无工具调用的空助理消息。
有文字的消息、思考条目、工具 ID、命名空间、工具结果和搜索工具声明均保留；不通过提示词规避，也不做隐式重试。

启动器使用公开 `-c` 参数覆盖当前进程的供应商地址，不改 PVC 的 `config.toml`，所以 `REWRITE_CONFIG=0` 也能生效。
模型传输使用 HTTP/SSE，关闭该供应商的 Responses WebSocket 传输；工作台与 app-server 的 WebSocket 不变。
搜索能力仍由原来的 `web_search` 和功能配置决定。不要在 `[features]` 写 `web_search_mode="never"`（0.155.1 会解析失败），
也不要把 `standalone_web_search=false` 当成此次协议故障的修复。

兼容检查：`python3 -m pytest infrastructure/applications/component-images/sandbox-platform/image/tests -q`。
运行日志只记录 `removed_empty_assistant_messages=N`，不记录消息正文、请求头或密钥。
回退时使用之前的固定摘要沙箱镜像，不需要迁移持久数据或重写用户配置。

## key 怎么进去

- `OPENAI_API_KEY` 由 Secret 注入进程环境；入口脚本把它写成 `$CODEX_HOME/auth.json`（600）后从环境里 `unset`；
- 国产厂商：再给 `MODEL_PROVIDER`、`MODEL`、`PROVIDER_BASE_URL`（`wire_api` 默认 `responses`；Kimi 已验）；
- 没有 key 拒绝启动：不垫付 token 是硬杠。

## 构建与部署

构建：`make -C infrastructure platform-build OBJECT=sandbox-platform/sandbox`、`OBJECT=sandbox-platform/provisioner`（配置见上一级 [component-images.yaml](../../component-images.yaml)，产物发到 Harbor `platform/`，锁写进 `gitops/components/sandbox-platform/<对象>/image.lock.yaml`）。部署：供给器由 [`gitops/components/sandbox-platform/provisioner/`](../../../../gitops/components/sandbox-platform/provisioner) 声明；沙箱不单独部署，由供给器按用户拉起。

## 按需拉起（供给器）

工作台 `POST /api/workbench/sandboxes/provision`：取用户设置页登记的 key → 签发该用户的会合点身份并经 `/admin` 登记到会合点 →
`PUT sandbox-provisioner:8080/sandboxes/<relay_user>`（Bearer 共享令牌）→ 供给器建 Secret（key、会合点令牌、能力令牌）、PVC、
Deployment、Service、NetworkPolicy → 工作台把 `app_server_url` 与能力令牌登记为该用户的沙箱。再次调用是更新（换 key），
能力令牌不变，PVC 不动；`DELETE` 回收运行资源，PVC 保留（`?purge=1` 才删）。一用户一个沙箱。

供给器单测：

```bash
cd infrastructure/applications/component-images/sandbox-platform/provisioner && python3 -m pytest tests -q
```

## 已知与待办

- 版本成对：镜像里的 Codex 版与本地代理随包带的版必须一致，会合点在 hello 里核对（`AT-28`）；
- `D9`：按需拉起已由供给器实现（一用户一个，PVC 保留）；`CODEX_HOME` 备份（D18）与配额未做；
- 多会话共用一个 exec-server 未验；冷启动时间未测。
