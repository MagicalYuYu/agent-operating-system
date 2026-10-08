# 08_INBOX — 重量级输入鲁棒入口

外部给的大文件（数据集/压缩包/共享目录转存）先落这里，按 `YYYYMMDD/` 分层。

**中转区语义**：处理完必须迁往真正归宿（项目目录/09_REFERENCE/归档），原处只留去向指针。标准动作：收到 INBOX 路径 → 读取 → 处理 → 主动归位 → 留去向记录。

示例：`08_INBOX/20261007/dataset.zip` → 处理后迁 `01_PROJECTS/myproject/assets/data/`，原处留 `dataset.zip.moved-to.txt` 写明去向
