# AOS 记忆规则（Claude Code 版本）

适用范围：当读取或修改 04_MEMORY/ 目录下的文件时

1. 记忆与指令必须分开存储
2. Memory 区分记录型与状态型：记录型（feedback/经验/坑点/操作日志）只追加不覆盖；状态型（用户画像/项目事实/系统配置）覆盖旧值，保留变更注释
3. INDEX.md 是索引不是内容，硬上限200行/25KB
4. feedback 每条必须包含三要素：规则+Why+How to apply
5. feedback 必须同时记录成功和失败
6. reference 只存指针不存内容
7. project 类型相对日期必须转绝对日期
8. 可推导信息不存入记忆
