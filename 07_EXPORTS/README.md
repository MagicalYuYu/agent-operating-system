# AOS v1.0 - Exports 目录

输出导出区，所有输出必须从这里导出。

## 应放什么
- 最终交付文件
- 翻译完成的文件
- 验证报告
- 导出包

## 禁止放什么
- 中间处理文件（应放 05_CACHE/）
- 未完成的草稿（应放 02_SANDBOX/）

## 导出流程
禁止直接从项目目录导出文件，必须经过 Project→Export 流程：
1. 在 01_PROJECTS/ 中完成工作
2. 将最终成果复制到 07_EXPORTS/{project_name}/
3. 从 07_EXPORTS/ 导出给用户

## 分层规则
按项目名分层存放，禁止多项目导出混杂在同一目录：
```
07_EXPORTS/
├── GameXYZ/
│   ├── translation-v1.0/    ← 按交付物分层
│   └── review-report/
├── WebApp/
│   └── build-v2.0/
└── README.md
```
