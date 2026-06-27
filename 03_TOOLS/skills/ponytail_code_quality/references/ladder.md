# ponytail 6 级阶梯 — 详细说明

## 梯级 1：YAGNI

**判断标准**：用户没有明确要求的功能，不要写。

**示例**：
- 用户要一个"把字符串转大写"的函数 → 不需要创建 StringUtils 类
- 用户要一个"查询用户列表"的接口 → 不需要同时做创建/更新/删除

## 梯级 2：标准库

**判断标准**：标准库已有等价功能，就不自己写。

**示例**：
- `functools.lru_cache` 替代手写缓存
- `pathlib.Path` 替代字符串拼接路径
- `dataclasses.dataclass` 替代手写 __init__
- `json.loads` 替代手写 JSON 解析

## 梯级 3：原生平台特性

**判断标准**：浏览器/Node.js/Python 原生 API 能覆盖，就不引入库。

**示例**：
- `<input type="date">` 替代 flatpickr
- CSS Grid 替代 Bootstrap 布局
- `fetch()` 替代 axios（简单场景）
- `URLSearchParams` 替代 qs 库

## 梯级 4：已安装依赖

**判断标准**：项目已安装的依赖中有等价功能，就用它。

**示例**：
- 项目已有 lodash，用 `_.debounce` 而不是手写
- 项目已有 requests，用 `requests.get` 而不是 `urllib`

## 梯级 5：一行代码

**判断标准**：能一行搞定，就不写函数/类/文件。

**示例**：
- `sorted(users, key=lambda u: u.age)` 而不是写一个排序函数
- `[x for x in items if x.active]` 而不是 for 循环
- `result = json.loads(data) if data else {}` 而不是 if-else 块

## 梯级 6：最小实现

**判断标准**：以上都不行，写最少能工作的代码。

**示例**：
- 一个简单的 REST API 不需要 Controller → Service → Repository → DTO → Mapper 五层
- 一个配置项不需要 ConfigManager 类，一个 dict 就够了