# 挂机放置挖宝游戏项目

这是一个面向商业化研发的挂机放置类挖宝游戏项目仓库。

## 文档

- [挂机放置挖宝游戏技术文档](docs/idle-treasure-game-tech-design.md)

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

## 当前阶段

- 已连接 GitHub 远程仓库：`https://github.com/8846fmc57j-cmyk/new-project.git`
- 已创建 MVP 研发版游戏技术文档，覆盖玩法、系统、后端、商业化、数据配置、反作弊、埋点、接口、数据库、后台、测试验收与研发排期。
- 已创建首批 MVP 配置表模板，位于 `Config/csv/`，覆盖道具、地图、掉落、古物、怪物、战斗关卡、装备和任务。
- 已创建配置导出脚本，生成 `Config/json/` 运行时配置和 `manifest.json`。
- 已创建 MVP 数值模拟脚本，用于早期检查掉落、鉴宝估价和打怪战力。
