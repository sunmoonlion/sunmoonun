# Cursor 回执

- 对应请求：../request.md
- 本轮：第 1 轮
- 实际发布版本：KnowBench 父仓 `822656ecae71fe5f35e928fb45d7a1b517da73f5`，后端 `a3c21a487d318f5a512b71bc6c136f0235275afa`；KnowLab 父仓 `386fed38f7e1d85cb13f5ce819d930b2d0bf10b4`，后端 `457932623d2410b61432a050376da973c814fbad`，Web `3f59f9c77ba772f0b03d9edd29061f81f8c0b388`
- 结论：部分完成。候选修订已上线。脚本试跑的目标条件不成立，三条验收待验。

## 发布

与前置两单同一版 Jenkins #98。顺序是先有 KnowBench API、runner 镜像，再有 KnowLab API、Web。供给器 `43d82a044b333db4102dbc2d089ab7b645eec0a8` 已部署，镜像 `sha256:b5c08edbc7cb0c41835f44076f9e9e6617e56d08dabeef9fcbfe7128f7b92185`，含单文件入口。KnowBench 库版本期望 `20261121_0053`。

本单自己没有新迁移。钉上的 KnowLab 后端 Alembic head 是 `20261120_0029`，所以 KnowLab 升到了 `20261120_0029`，Job `knowlab-migrate-66ec19243f85-v5` 成功。

线上脚本开关仍是 `WORKBENCH_SKILL_SCRIPTS_ENABLED=false`。没有改运营价目。

## 目标环境验收

目标环境没有已允许的供给器脚本执行，也没有获准测试作者走下面的步骤。没有来源 ID、试跑编号、执行回执或账本引用。三项都待验。

1. 直接登记单文件脚本，在 KnowLab 选取该版本，用合成输入以宿主身份试跑，通过后私有冻结。
2. 固定专家里前一步产物作脚本输入、下一步读脚本输出；登记 v2 后原专家仍取 v1。
3. 待批准时取消应无新投递；另一账号看不到作者脚本。

`application-check` 的 knowbench 与 knowlab 已通过，只核对发布声明，不代替上述试跑。
