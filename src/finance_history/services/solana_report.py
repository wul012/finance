from __future__ import annotations

from finance_history.domain import SolanaAnalysis
from finance_history.services.trend_analysis import format_decimal


class SolanaMarkdownReportBuilder:
    def build(self, analysis: SolanaAnalysis) -> str:
        snapshot = analysis.snapshot
        metrics = analysis.metrics
        observed_at = snapshot.observed_at.strftime("%Y-%m-%d %H:%M UTC")
        lines = [
            "# SOL 专题研究报告 v0.2.0",
            "",
            f"> 数据时点：{observed_at}。本报告用于研究，不构成投资建议。",
            "",
            "## 1. 当前市场快照",
            "",
            f"- SOL 价格：{format_decimal(snapshot.price_usd)} USD",
            f"- 24 小时涨跌：{format_decimal(snapshot.change_24h_pct)}%",
            f"- 市值：{format_decimal(snapshot.market_cap_usd / 1_000_000_000)} 十亿美元",
            f"- 24 小时成交额：{format_decimal(snapshot.volume_24h_usd / 1_000_000_000)} 十亿美元",
            f"- Solana DeFi TVL：{format_decimal(snapshot.tvl_usd / 1_000_000_000)} 十亿美元",
            "",
            "## 2. SOL 是什么",
            "",
            analysis.profile.overview,
            "",
            "## 3. 价格与风险指标",
            "",
        ]
        for item in metrics.returns:
            lines.append(f"- {item.days} 日涨跌：{format_decimal(item.change_pct)}%")
        lines.extend(
            [
                f"- 20 日均价：{format_decimal(metrics.sma_20_usd)} USD",
                f"- 30 日价格区间：{format_decimal(metrics.range_30d_low_usd)} 至 {format_decimal(metrics.range_30d_high_usd)} USD",
                f"- 样本期年化波动率：{format_decimal(metrics.annualized_volatility_pct)}%",
                f"- 样本期最大回撤：{format_decimal(metrics.max_drawdown_pct)}%",
                f"- 趋势判断：{metrics.trend}",
                "",
                "这里的区间和均线是历史描述，不是保证有效的支撑位或阻力位。加密资产全天交易，短时波动可能明显超过日线样本反映的水平。",
                "",
            ]
        )

        if analysis.position is not None:
            position = analysis.position
            lines.extend(
                [
                    "## 4. 个人持仓情景",
                    "",
                    f"- 推算/输入成本价：{format_decimal(position.entry_price_usd)} USD",
                    f"- 当前收益率：{format_decimal(position.return_pct)}%",
                    f"- 从现价回撤 {format_decimal(position.breakeven_drawdown_pct)}%，该笔持仓将回到盈亏平衡附近。",
                ]
            )
            if position.quantity is not None:
                lines.extend(
                    [
                        f"- 数量：{format_decimal(position.quantity)} SOL",
                        f"- 成本：{format_decimal(position.cost_usd or 0)} USD",
                        f"- 当前价值：{format_decimal(position.market_value_usd or 0)} USD",
                        f"- 未实现盈亏：{format_decimal(position.unrealized_pnl_usd or 0)} USD",
                    ]
                )
            lines.extend(["", "情景压力测试：", ""])
            for scenario in position.scenarios:
                lines.append(
                    f"- 若 SOL 从现价变动 {format_decimal(scenario.market_move_pct)}%，持仓收益率约为 {format_decimal(scenario.resulting_return_pct)}%。"
                )
            lines.append("")

        section = 5 if analysis.position is not None else 4
        self._add_items(lines, section, "价值驱动机制", analysis.profile.value_mechanisms)
        self._add_items(lines, section + 1, "潜在催化剂", analysis.profile.catalysts)
        self._add_items(lines, section + 2, "主要风险", analysis.profile.risks)

        lines.extend([f"## {section + 3}. 关键发展时间线", ""])
        for milestone in analysis.profile.milestones:
            lines.extend(
                [
                    f"### {milestone.date} · {milestone.title}",
                    "",
                    milestone.impact,
                    "",
                    f"来源：<{milestone.source}>",
                    "",
                ]
            )
        lines.extend(
            [
                f"## {section + 4}. 今日上涨的解释框架",
                "",
                "1. **市场层面**：当比特币和整体风险偏好回升时，SOL 往往因波动率和资金弹性更高而放大上涨。今日报道显示，比特币重回 60,000 美元上方后，SOL 在主流币中相对领先。",
                "2. **资产层面**：近期 ETF 资金、RWA、稳定币、支付和链上交易活动为 SOL 提供中期叙事，但这些基本面不能单独证明某一个小时的涨幅。",
                "3. **交易层面**：突破、空头回补、杠杆和流动性会放大行情。若没有逐笔资金流和衍生品数据，不应把上涨归结为单一新闻。",
                "",
                "今日市场背景来源：<https://www.coindesk.com/markets/2026/07/02/ether-solana-dogecoin-in-the-green-after-warsh-comments-push-bitcoin-above-usd60-000>",
                "",
                f"## {section + 5}. 数据来源与边界",
                "",
            ]
        )
        for source in snapshot.sources:
            lines.append(f"- <{source}>")
        lines.extend(
            [
                "- 行情会持续变化，报告中的数字仅对应文首时点。",
                "- 20% 收益若由用户输入，则成本价为不考虑手续费、资金费率、税费和杠杆的反推值。",
                "- TVL、交易量和地址数不能直接等同于协议收入、真实用户数或 SOL 的内在价值。",
                "",
            ]
        )
        return "\n".join(lines)

    @staticmethod
    def _add_items(lines: list[str], number: int, title: str, items: tuple) -> None:
        lines.extend([f"## {number}. {title}", ""])
        for item in items:
            lines.extend(
                [
                    f"### {item.title}",
                    "",
                    item.detail,
                    "",
                    f"来源：<{item.source}>",
                    "",
                ]
            )
