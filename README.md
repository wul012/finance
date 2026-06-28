# Finance History Lab

金融与货币材料发展、价格涨跌历史及成因分析项目。

本项目 v0.1.0 是一个离线可运行的第一版研究框架，重点不是预测价格，而是把“材料演变、金融制度、资产价格观察点、重大事件和原因解释”组织成可扩展的数据与分析模块。

## 已完成功能

- 货币材料演变资料库：贝壳、金属、纸币、法币、电子货币、加密资产等。
- 金融事件库：金本位、布雷顿森林体系、尼克松冲击、金融危机、比特币现货 ETF 等。
- 历史价格观察点：黄金、白银、铜、美元指数、人民币兑美元、比特币。
- 涨跌区间分析：计算起止价格、变化百分比、方向，并关联区间内事件。
- Markdown 报告生成：输出第一版项目研究报告。
- CLI 命令行入口：可查看摘要、时间线、单资产分析和生成报告。
- 单元测试：覆盖数据加载、时间线、趋势分析和报告生成。

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
```

运行测试：

```powershell
$env:PYTHONPATH="src"
python -m unittest discover -s tests
```

## 数据说明

`data/seed` 中的数据是第一版研究样例数据，用于验证项目结构、分析流程和报告生成能力。价格点采用历史观察点形式，不构成投资建议，也不等同于实时行情数据库。后续版本可替换为 FRED、World Bank、IMF、交易所、央行或可信行情数据源。

## 版本规划

- v0.1.0：完成离线研究框架、种子数据、分析服务、CLI、测试和报告。
- v0.2.0：接入可配置数据源，增加数据校验和图表输出。
- v0.3.0：增加 Web 可视化界面和交互式时间线。
- v1.0.0：形成稳定的数据模型、引用规范、报告模板和自动更新流程。

