# 挂机放置挖宝游戏项目

这是一个面向商业化研发的 2.5D 微信小游戏挂机挖宝项目仓库。

正式客户端方向：**Cocos Creator + 微信小游戏 + 2.5D 竖屏挂机挖宝**。当前 Web 原型用于快速验证玩法、接口和数值闭环。

## 文档

- [项目长期上下文](PROJECT_CONTEXT.md)
- [挂机放置挖宝游戏技术文档](docs/idle-treasure-game-tech-design.md)
- [MVP 登录、进游戏与主线流程](docs/mvp-login-mainline-flow.md)
- [MVP 客户端界面与接口对接文档](docs/mvp-client-screen-flow.md)
- [MVP 研发任务清单](docs/mvp-development-backlog.md)
- [微信小游戏 2.5D 技术方案](docs/wechat-minigame-2.5d-tech-plan.md)
- [Cocos 微信小游戏客户端骨架](Client/wechat-minigame/README.md)
- [Cocos 客户端接口映射](Client/wechat-minigame/docs/api-mapping.md)

## 配置导出

```bash
python3 Tools/export_config.py
```

该命令会校验 `Config/csv/` 下的配置表，并导出运行时 JSON 到 `Config/json/`。

## MVP 数值模拟

```bash
python3 Tools/simulate_mvp.py --iterations 1000 --seed 20260627
```

该命令会读取 `Config/json/`，模拟地图掉落、古物鉴宝估价和战斗关卡战力门槛。

## MVP Mock API

```bash
python3 Server/mock_api.py
```

本地接口地址为 `http://127.0.0.1:8787`，用于先跑通游客登录、进入游戏、主线任务、新手引导、挂机领取、古物鉴宝和打怪结算。

冒烟测试：

```bash
python3 Tools/test_mock_api.py
python3 Tools/test_web_prototype.py
```

## MVP Web 原型

一键启动：

```bash
python3 Tools/run_mvp_demo.py
```

或手动启动 Mock API 和静态原型：

```bash
python3 Server/mock_api.py
python3 -m http.server 8080
```

浏览器打开 `http://127.0.0.1:8080/Client/web-prototype/`，可体验游客登录、主界面、主线推进、新手引导、挂机领取、鉴宝估价、打怪结算、装备穿戴和境界突破。原型右上角的“重置 Demo”会调用本地 `/dev/reset`，用于反复测试流程。

## 当前阶段

- 已连接 GitHub 远程仓库：`https://github.com/8846fmc57j-cmyk/new-project.git`
- 已创建 MVP 研发版游戏技术文档，覆盖玩法、系统、后端、商业化、数据配置、反作弊、埋点、接口、数据库、后台、测试验收与研发排期。
- 已创建首批 MVP 配置表模板，位于 `Config/csv/`，覆盖道具、地图、掉落、古物、怪物、战斗关卡、装备和任务。
- 已创建配置导出脚本，生成 `Config/json/` 运行时配置和 `manifest.json`。
- 已创建 MVP 数值模拟脚本，用于早期检查掉落、鉴宝估价和打怪战力。
- 已创建 MVP 登录、进入游戏、主线任务和新手引导流程配置。
- 已创建本地 MVP Mock API 服务，用于客户端先接入完整核心流程。
- 已创建 MVP 客户端页面与接口对接说明，重点覆盖主界面、鉴宝估价和打怪关卡。
- 已创建 MVP 研发任务清单，把客户端、接口、配置和验收拆成可执行任务。
- 已创建 MVP Web 原型骨架，直接连接本地 Mock API 验证核心循环，并加入主线、新手引导、装备穿戴与境界突破。
- 已创建一键启动脚本 `Tools/run_mvp_demo.py`，用于同时启动 Mock API 和 Web 原型。
- 已创建 Web 原型冒烟测试 `Tools/test_web_prototype.py`，用于检查静态页面、配置路径和核心 API 联通。
- 已确定正式客户端方向为 Cocos Creator 微信小游戏 2.5D，并补充对应技术方案。
- 已创建 `Client/wechat-minigame/` 正式客户端骨架和 Mock API 到 Cocos 服务层的迁移映射。
