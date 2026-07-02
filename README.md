# Finance History Lab

金融与货币材料发展、价格涨跌历史及成因分析项目。

本项目 v0.2.0 在离线金融史框架上增加了 SOL 专题研究管线。重点不是预测价格，而是把市场数据、项目机制、事件证据、技术指标和个人持仓情景放进可复现的分析结构。

## 已完成功能

- 货币材料演变资料库：贝壳、金属、纸币、法币、电子货币、加密资产等。
- 金融事件库：金本位、布雷顿森林体系、尼克松冲击、金融危机、比特币现货 ETF 等。
- 历史价格观察点：黄金、白银、铜、美元指数、人民币兑美元、比特币。
- 涨跌区间分析：计算起止价格、变化百分比、方向，并关联区间内事件。
- Markdown 报告生成：输出第一版项目研究报告。
- CLI 命令行入口：可查看摘要、时间线、单资产分析和生成报告。
- 单元测试：覆盖数据加载、时间线、趋势分析和报告生成。
- SOL 实时专题：读取 CoinGecko 行情和 DeFiLlama TVL，计算 7/30/90 日涨跌、20 日均价、波动率和最大回撤。
- 持仓情景：支持输入成本价或当前收益率，分开显示市场涨跌与个人盈亏，并生成回撤压力测试。
- 引用式专题报告：输出 SOL 机制、催化剂、风险、里程碑和今日上涨解释框架。

## 模块结构

```text
finance/
├── data/seed/                    # 第一版离线种子数据
├── docs/                         # 设计说明和数据字典
├── output/reports/               # 生成的研究报告
├── src/finance_history/
│   ├── domain/                   # 领域模型
│   ├── infrastructure/           # 数据路径与仓储加载
│   ├── services/                 # 时间线、涨跌分析、报告生成
│   └── cli.py                    # 命令行入口
├── tests/                        # 单元测试
├── pyproject.toml
└── 项目计划书.md
```

## 快速开始

在项目根目录执行：

```powershell
python -m finance_history summary
```

如果没有安装为包，请先临时指定源码路径：

```powershell
$env:PYTHONPATH="src"
python -m finance_history summary
python -m finance_history timeline --limit 12
python -m finance_history analyze --asset gold --start 1971 --end 1980
python -m finance_history report --output output/reports/first_version_report.md
python -m finance_history sol --profit-pct 20
```

SOL 命令默认写入 `output/reports/solana_v0.2.0_report.md`。若已知成本价和数量，可执行：

```powershell
python -m finance_history sol --entry-price 68 --quantity 10 --days 90
```

SOL 专题需要联网访问 CoinGecko 和 DeFiLlama；研究资料仍从 `data/seed/solana_research.json` 离线加载。实时请求失败时命令会明确返回失败，不会用旧价格冒充当前行情。

运行测试：

```powershell
$env:PYTHONPATH="src"
python -m unittest discover -s tests
```

## 数据说明

`data/seed` 中的通用数据是第一版研究样例，SOL 研究资料则用于第二版专题报告。实时市场数据来自公开 API，所有结果都带有观察时点。项目输出不构成投资建议。

## 版本规划

- v0.1.0：完成离线研究框架、种子数据、分析服务、CLI、测试和报告。
- v0.2.0：完成 SOL 实时行情、基本面研究、风险指标、持仓情景和专题报告。
- v0.3.0：增加行情缓存、图表、Web 可视化界面和交互式时间线。
- v1.0.0：形成稳定的数据模型、引用规范、报告模板和自动更新流程。
