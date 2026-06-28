from __future__ import annotations

from finance_history.infrastructure.repository import SeedRepository
from finance_history.services.timeline import TimelineService, format_year
from finance_history.services.trend_analysis import TrendAnalyzer, format_decimal


class MarkdownReportBuilder:
    def __init__(self, repository: SeedRepository) -> None:
        self.repository = repository

    def build(self) -> str:
        materials = self.repository.load_materials()
        assets = self.repository.load_assets()
        events = self.repository.load_events()
        prices = self.repository.load_price_points()
        timeline = TimelineService().build(materials, events)
        analyzer = TrendAnalyzer(prices, events)

        lines: list[str] = [
            "# 金融与货币材料发展及涨跌历史第一版报告",
            "",
            "## 1. 项目定位",
            "",
            "本报告由 Finance History Lab v0.1.0 自动生成，用于展示货币材料演变、金融制度变化、资产价格观察点和涨跌原因之间的关系。",
            "",
            "## 2. 货币材料演变概览",
            "",
        ]

        for material in sorted(materials, key=lambda item: item.active_from_year):
            active_to = "至今" if material.active_to_year is None else format_year(material.active_to_year)
            lines.extend(
                [
                    f"### {material.name}",
                    "",
                    f"- 类型：{material.category}",
                    f"- 活跃阶段：{format_year(material.active_from_year)} 至 {active_to}",
                    f"- 价值基础：{material.value_basis}",
                    f"- 优势：{'；'.join(material.strengths)}",
                    f"- 局限：{'；'.join(material.limits)}",
                    "",
                ]
            )

        lines.extend(
            [
                "## 3. 核心时间线",
                "",
            ]
        )
        for entry in timeline:
            lines.append(f"- {format_year(entry.year)} [{entry.kind}] {entry.title}：{entry.summary}")

        lines.extend(
            [
                "",
                "## 4. 资产涨跌摘要",
                "",
            ]
        )
        for asset in assets:
            try:
                window = analyzer.analyze_asset(asset.id)
            except ValueError:
                continue
            lines.extend(
                [
                    f"### {asset.name}",
                    "",
                    f"- 类型：{asset.asset_type}",
                    f"- 观察区间：{format_year(window.start_year)} 至 {format_year(window.end_year)}",
                    f"- 起点价格：{format_decimal(window.start_price)} {window.unit}",
                    f"- 终点价格：{format_decimal(window.end_price)} {window.unit}",
                    f"- 变化幅度：{format_decimal(window.change_pct)}%",
                    f"- 方向判断：{window.direction.value}",
                    f"- 解释要点：{asset.description}",
                    "",
                ]
            )
            if window.related_events:
                lines.append("关联事件：")
                for event in window.related_events:
                    lines.append(
                        f"- {format_year(event.year)} {event.name}：{event.direct_reason}；深层原因：{event.deep_reason}"
                    )
                lines.append("")

        lines.extend(
            [
                "## 5. 第一版结论",
                "",
                "1. 货币材料从实物稀缺性逐步转向制度信用和网络信用。",
                "2. 金银等材料的长期价格变化，既受供需影响，也受货币制度、实际利率和避险需求影响。",
                "3. 工业金属更容易体现产业周期，法币汇率更依赖国家信用、贸易结构和政策框架。",
                "4. 加密资产的价格波动具有更强的叙事、流动性和监管敏感性。",
                "5. 后续应接入权威数据源，并为每一条价格与事件解释建立可追溯引用。",
                "",
                "## 6. 数据边界",
                "",
                "第一版使用离线种子数据，适合验证项目结构和研究流程，不构成实时行情、投资建议或完整历史数据库。",
                "",
            ]
        )

        return "\n".join(lines)

