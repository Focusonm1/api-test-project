# api-test-project

使用 Python、requests 和 pytest 编写的接口自动化测试学习项目。被测对象是项目内的本地 HTTP 服务，覆盖健康检查、登录、管理员权限和查询参数处理。

本地服务使用固定的练习账号和 token，方便独立运行与复现测试。

## 快速开始

需要 Python 3.11 或更高版本，以及 uv。在项目根目录执行：

```bash
uv sync
uv run pytest -v
```

当前共有 23 条测试用例。默认请求地址为 `http://127.0.0.1:8000`，无需提前手动启动服务：

- 如果本地服务没有启动，fixture 会自动启动它，并在本次测试结束后关闭。
- 如果该地址已有可响应的服务，则直接复用，测试结束后不会关闭它。请确保端口上运行的是本项目的服务。

只运行登录测试：

```bash
uv run pytest tests/test_login.py -v
```

只运行名称包含 `logged` 的测试：

```bash
uv run pytest -k logged -v
```

## 项目结构

```text
api-test-project/
├── server/
│   └── local_api.py       # 本地被测服务
├── tests/
│   ├── conftest.py        # 服务启停、Session、登录 fixture 和请求日志
│   ├── test_health.py     # 健康检查
│   ├── test_login.py      # 登录及异常输入
│   ├── test_admin.py      # token 校验与权限控制
│   └── test_echo.py       # 查询参数回显及不存在的路径
├── api_helpers.py        # 按 token 构造 Authorization 请求头
├── config.py             # 请求地址和超时时间
├── pyproject.toml        # 项目依赖和 pytest 配置
├── uv.lock               # 锁定依赖版本
└── README.md
```

## 测试覆盖

| 接口 | 测试点 | 用例数 |
|---|---|---|
| GET /health | 状态码和健康状态 | 1 |
| POST /login | 正确登录、错误密码、用户不存在、缺密码字段、空 JSON 对象、非对象 JSON、非法 JSON、媒体类型校验及 charset 参数 | 10 |
| GET /admin | 未带 token、无效 token、普通用户 token、管理员 token，以及实际登录后验证普通用户无权访问 | 5 |
| GET /echo | 单个参数、多个参数、无参数、中文、同名多值、空值参数 | 6 |
| GET /nope | 不存在的路径返回 404 和对应错误信息 | 1 |

测试同时检查 HTTP 状态码和响应体。`/echo` 是用于观察查询参数的小接口，没有实际业务处理。

## 设计要点

- 用 `conftest.py` 共享 fixture，每条测试创建自己的 Session，并通过 `with` 在使用结束后关闭。
- 通过登录 fixture 获取普通用户 token，需要登录的测试不依赖其他测试先执行。
- 使用参数化覆盖不同 token 和登录输入，减少重复测试代码。
- 使用 session 级别的自动 fixture 管理本地服务，整次测试共用一个服务。
- 通过响应 hooks 记录请求方法、URL、状态码、耗时、请求体和响应体；pytest 在失败详情中展示捕获日志。

## 配置

`config.py` 从环境变量读取配置：

| 变量 | 默认值 | 含义 |
|---|---|---|
| `BASE_URL` | `http://127.0.0.1:8000` | 被测服务地址 |
| `TIMEOUT` | `3` | 单次请求的超时设置，单位为秒 |

例如，只调整超时时间：

```bash
TIMEOUT=5 uv run pytest -v
```

切换到另一个兼容服务时，可设置 `BASE_URL`。该服务需要事先启动，并提供相同的接口和测试数据。地址与默认本地地址不同时，fixture 不会自动启动本地服务。

测试 Session 设置了 `trust_env = False`，不读取环境代理设置，避免本地请求被代理转发。

## 观察到的待确认行为

请求：

```text
GET /echo?name=qa01&role=
```

当前返回：

```json
{"args": {"name": "qa01"}}
```

空值参数 `role` 被丢弃，没有保留为 `"role": ""`。现有测试记录这一行为；对于其是否属于缺陷，需要明确接口对空值参数的要求。

## 测试报告

```bash
uv run pytest --html=report.html --self-contained-html
```

运行后用浏览器打开项目根目录的 `report.html`，查看用例结果、耗时和失败详情。在 macOS 上可以执行：

```bash
open report.html
```

`--self-contained-html` 将报告样式打包进 HTML 文件，方便单独分享。再次使用同一命令会覆盖上一次报告


## 登录请求的内容类型

`POST /login` 接收 `application/json`，支持 `application/json; charset=utf-8` 这样的参数形式。

- 内容类型不受支持：返回 415 和 `{"error": "unsupported_media_type"}`。
- 内容类型受支持，但 JSON 格式损坏：返回 400 和 `{"error": "invalid_json"}`。
- 内容类型检查在 JSON 解析之前执行。

## GitHub Actions

配置位于 `.github/workflows/tests.yml`。提交并推送该文件后，GitHub 将在 push、pull request 或手动触发时使用 Ubuntu 运行测试。步骤为获取代码、准备 Python 3.11 和 uv 0.12.0、按 uv.lock 安装依赖、运行 pytest。现有 fixture 负责在该运行环境中启动和清理本地被测服务。

在仓库的 Actions 页面查看每次运行和失败日志。当前配置已在本地准备，首次 GitHub 运行仍待提交推送后验证。
