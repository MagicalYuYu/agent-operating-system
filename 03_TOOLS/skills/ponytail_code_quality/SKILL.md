# Ponytail for AOS — 懒人代码质量 Skill

## Description
当用户要求编写/修改代码时调用本 Skill。强制执行 ponytail 6 级决策阶梯：
能不写就不写 → 能复用就复用 → 能一行就一行。触发词：ponytail、懒人模式、
最简方案、YAGNI、代码审查、减少依赖、简化代码、过度工程、别写太多。

## Persistence

本 Skill 在调用后**本次会话内持续生效**。Agent 在后续代码操作中必须继续
执行 6 级阶梯，直到用户说"停止 ponytail"或"恢复正常模式"。

注意：Trae 无 hooks 机制，无法自动跨会话保持。每次新会话如需 ponytail，
Agent 应主动判断代码任务是否需要调用本 Skill。

首次调用时输出：
"使用强度：full。如效果不佳，说 'ponytail lite' 降低强度。"

## The Ladder

写代码前，按顺序停在第一个成立的台阶：

1. **这东西需要存在吗？**
   - 臆测需求 → 跳过，一行注释说明理由
   - 用户没要求的功能 → 不写
   - YAGNI（You Aren't Gonna Need It）

2. **标准库能做到吗？**
   - Python: itertools, functools, pathlib, dataclasses, re, json, csv...
   - Node.js: fs, path, crypto, http, URL, Buffer...
   - 浏览器: fetch, URLSearchParams, Intl, DOMParser, CSS Grid, <dialog>...

3. **原生平台特性覆盖了吗？**
   - `<input type="date">` 替代日期选择器库
   - CSS Grid/Flexbox 替代布局库
   - DB 约束（UNIQUE, CHECK, FOREIGN KEY）替代应用层校验
   - `<details>` / `<dialog>` 替代 JS 弹窗组件
   - `Constraint Validation API` 替代表单验证库

4. **已安装的依赖能解决吗？**
   - 检查 requirements.txt / package.json / Cargo.toml
   - 已有的库能覆盖，就不再装新的
   - 一个工具函数不值得引入整个库

5. **能一行搞定吗？**
   - 一行代码 > 一个函数 > 一个类 > 一个文件
   - 列表推导式 > for 循环
   - lambda > def（简单场景）
   - 链式调用 > 多步赋值

6. **都不行：写最少能工作的代码**
   - 最短的 diff 是最好的 diff
   - 删除优先于添加
   - 无聊优先于聪明

## 规则

- 不创建未被明确要求的抽象：只有一个实现的接口不要，只有一个产品的工厂不要
- 不写模板代码，不搭"以后用"的脚手架
- 删除优先于添加。无聊优先于聪明
- 文件越少越好。最短能工作的 diff 就是最好的
- 复杂需求？先交付懒人版本，同时问一句："做了 X，Y 能覆盖吗？需要完整版 X 吗？"
- 两个标准库方案一样大？选边界情况正确的那个。懒是指少写代码，不是选更脆弱的算法
- 有意简化时用 `ponytail:` 注释标注：`# ponytail: 全局锁，如果吞吐量成为瓶颈再改为按账户加锁`
- 非平凡逻辑（有分支、循环、解析器、涉及金钱/安全的路径）必须留一个可运行的检查：
  assert demo() 或一个小 test_*.py。不要测试框架，不要 fixtures。平凡一行代码不需要测试

## 安全边界（不可偷懒）

以下领域**绝不简化**：

- **输入验证**：信任边界（用户输入、API 响应、文件内容）必须验证
- **错误处理**：可能导致数据丢失的路径必须有错误处理
- **安全措施**：SQL 注入、XSS、CSRF、敏感信息泄露——必须防护
- **无障碍基础**：alt 文本、label 关联、键盘可操作——必须满足
- **硬件校准**：物理世界不等于理论规格，留校准旋钮

用户明确要求的完整实现 → 照做，不争论。

## 输出格式

代码优先。然后最多三行简短说明：跳过了什么，什么时候加回来。
如果解释比代码长，删掉解释。

格式：`[代码] → 跳过：X，需要时加 Y。`

## 强度级别

| 级别 | 行为 |
|------|------|
| **lite** | 按要求构建，注释指出更懒的替代方案。用户自己选 |
| **full** | 强制执行阶梯。stdlib 和原生优先。最短 diff，最短解释。**默认** |
| **ultra** | YAGNI 极端派。先删再写。交付一行代码同时挑战需求本身 |

切换方式：用户说 `ponytail lite` / `ponytail full` / `ponytail ultra`。