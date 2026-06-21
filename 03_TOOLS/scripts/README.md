# AOS v1.0 — 工具脚本

AOS 内置的 Python 工具脚本。

## 脚本列表
- aos_check.py — 一致性自检（版本号/引用/索引/目录）
- aos_migrate_collect.py — 迁移采集（项目扫描/对话提取/服务器环境调研）
- aos_migrate_classify.py — 迁移分类（决策树+去重+关联分析）
- aos_migrate_ingest.py — 迁移入库（脱敏+写入+索引更新）

## 用法
```bash
# 一致性自检
python 03_TOOLS/scripts/aos_check.py

# 迁移采集
python 03_TOOLS/scripts/aos_migrate_collect.py --source=project --path="项目路径"
python 03_TOOLS/scripts/aos_migrate_collect.py --source=server --path="服务器项目路径"
python 03_TOOLS/scripts/aos_migrate_collect.py --source=phase0 --path="服务器项目路径"

# 迁移分类
python 03_TOOLS/scripts/aos_migrate_classify.py

# 迁移入库
python 03_TOOLS/scripts/aos_migrate_ingest.py
python 03_TOOLS/scripts/aos_migrate_ingest.py --confirm
```

## 注意
所有脚本自动检测 AOS 根目录（向上查找 AGENTS.md），无需手动配置路径。
