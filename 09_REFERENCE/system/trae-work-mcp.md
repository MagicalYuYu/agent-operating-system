# TRAE Work MCP（Model Context Protocol）

> 来源：https://docs.trae.cn/solo_mcp-overview + https://docs.trae.cn/solo_remote-mcp-server
> 入库时间：2026-06-21T13:00:00+08:00
> 主题：TRAE Work MCP 协议
> 标签：trae, work, mcp, protocol

---

## TL;DR

- MCP（Model Context Protocol）允许 LLM 访问自定义工具和服务
- 支持三种传输类型：stdio（本地）、HTTP/SSE（本地/远程）、Streamable HTTP（本地/远程）
- 添加方式：MCP 市场添加或手动 JSON 配置
- stdio 类型通过 command/args/env 配置，HTTP 类型通过 url/headers 配置
- 支持超时配置（START_MCP_TIMEOUT_MS / RUN_MCP_TIMEOUT_MS）和 ${workspaceFolder} 变量引用
- MCP Server 由第三方构建，TRAE 不审查其行为

## 核心概念

**MCP 架构**：TRAE Work 智能体（MCP 客户端）→ MCP Server（工具提供方）。

**传输类型**：

| 类型 | 传输协议 | 执行环境 |
|---|---|---|
| stdio | stdio | 本地 |
| HTTP | SSE | 本地 / 远程 |
| Streamable HTTP | — | 本地 / 远程 |

**运行环境**：

| 环境类型 | 适用任务 | 适用客户端 |
|---|---|---|
| 本地 | 仅对本地任务生效 | TRAE Work 桌面版 |
| 云端 | 仅对云端任务（及从 GitHub 拉取的项目）生效 | TRAE Work 网页版、桌面版 |

## 方法论 / 流程

### 从 MCP 市场添加 MCP Server

1. 在界面左下角，点击 **头像** > **设置**
2. 在左侧导航栏中，选择 **MCP** → 进入 MCP Server 管理面板
3. (仅 TRAE Work 桌面版) 选择 MCP Server 的运行环境：**本地** / **云端**
4. 在 **MCP Servers 管理** 部分，点击右上角的 **创建** > **从市场添加** → 页面上弹出 MCP 市场
5. 在 MCP 市场中找到所需的 MCP Server
6. 点击右侧的 **+** 按钮
7. 在弹窗中填入 MCP Server 的配置信息（`env` 中的 API Key、Token、Access Key 等须替换为真实信息）
8. 点击 **确认** 按钮

### 手动配置 MCP Server

1. 在界面左下角，点击 **头像** > **设置**
2. 在左侧导航栏中，选择 **MCP** → 进入 MCP Server 管理面板
3. (仅 TRAE Work 桌面版) 选择 MCP Server 的运行环境：**本地** / **云端**
4. 在 **MCP Servers 管理** 部分的右上角，点击 **创建** > **手动配置** → 页面上弹出 **手动配置** 框
5. 填入 MCP Server 的配置内容（优先使用 NPX 或 UVX 配置，无需全局安装）
6. 点击 **确认** 按钮

## 配置参数详解

### stdio 类型 MCP Server 配置

stdio 类型的 MCP Server 通过标准输入（stdin）和标准输出（stdout）与客户端进行通信。

| 字段 | 是否必填 | 描述 |
|---|---|---|
| command | 是 | 用于启动 MCP Server 的可执行命令。必须位于系统 `PATH` 中，或使用完整路径。**注意：命令中不能包含空格，否则会导致解析错误。** |
| args | 否 | 启动命令的参数列表。每个参数必须为字符串类型。 |
| env | 否 | 传递给 MCP Server 的环境变量，每个环境变量的值必须为字符串。 |

示例：
```json
{
  "mcpServers": {
    "mcp_name": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "API_Key": "value"
      }
    }
  }
}
```

### HTTP 类型 MCP Server 配置

HTTP 类型的 MCP Server 通过 HTTP 或 HTTPS 协议与远程服务进行通信。

| 字段 | 是否必填 | 描述 |
|---|---|---|
| url | 是 | 远程 MCP Server 的访问地址，需为合法的 HTTP 或 HTTPS URL。 |
| headers | 否 | 自定义的 HTTP 请求头，用于在请求中携带额外信息（如鉴权信息等）。 |

示例：
```json
{
  "mcpServers": {
    "mcp_name": {
      "url": "https://example.com/mcp",
      "headers": {
        "Authorization": "Bearer xxxx-xxxxxxx"
      }
    }
  }
}
```

### 超时配置

stdio 类型通过 `env` 字段设置超时：
```json
"env": {
    "START_MCP_TIMEOUT_MS": "60000",
    "RUN_MCP_TIMEOUT_MS": "60000"
}
```

HTTP 类型通过 `headers` 字段设置超时：
```json
"headers": {
    "START_MCP_TIMEOUT_MS": "60000",
    "RUN_MCP_TIMEOUT_MS": "60000"
}
```

### 变量引用

目前仅支持 `${workspaceFolder}` 变量。在 MCP Server 启动时，`${workspaceFolder}` 会被自动替换为当前项目的实际根目录路径。

示例：
```json
{
  "mcpServers": {
    "mcp_name": {
      "command": "node",
      "args": [
        "${workspaceFolder}/plugins/mcp.js"
      ]
    }
  }
}
```

## 可复用经验

- 优先使用 NPX 或 UVX 配置，无需全局安装，自动完成依赖获取与版本解析
- ${workspaceFolder} 变量使配置可移植，无论项目存放于何处都能正确加载
- 超时配置可防止 MCP Server 启动/调用卡死

## 关键坑点

- MCP Server 由第三方构建和维护，TRAE Work 不审查或认可这些服务器
- command 中不能包含空格，否则会导致解析错误
- env 中的 API Key、Token、Access Key 等须替换为真实信息
- 部分 MCP Server 可能因相关法律法规、网络限制、或服务器自身的访问策略，在你所在的国家或地区无法访问或使用
- 暂不支持自定义容器镜像

## 可迁移到 AOS 的规则

- MCP 协议可直接作为 AOS Agent 调用外部工具的标准
- stdio/HTTP 双传输模式适用于本地+云端混合架构
- ${workspaceFolder} 变量引用机制可复用
- 超时配置模式（START/RUN 分离）可复用为 AOS Agent 工具调用的超时策略
