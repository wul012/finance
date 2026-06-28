from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from finance_history.infrastructure.repository import SeedRepository
from finance_history.services.report import MarkdownReportBuilder
from finance_history.services.timeline import TimelineService, format_year
from finance_history.services.trend_analysis import TrendAnalyzer, format_decimal


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="finance-history",
        description="金融与货币材料发展、涨跌历史及原因分析工具",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="种子数据目录，默认使用 data/seed",
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("summary", help="查看项目数据摘要")

    timeline_parser = subparsers.add_parser("timeline", help="输出货币与金融事件时间线")
    timeline_parser.add_argument("--limit", type=int, default=0, help="限制输出条数")

    analyze_parser = subparsers.add_parser("analyze", help="分析单个资产涨跌区间")
    analyze_parser.add_argument("--asset", required=True, help="资产 ID，例如 gold、bitcoin")
    analyze_parser.add_argument("--start", type=int, default=None, help="起始年份")
    analyze_parser.add_argument("--end", type=int, default=None, help="结束年份")

    report_parser = subparsers.add_parser("report", help="生成 Markdown 研究报告")
    report_parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/reports/first_version_report.md"),
        help="报告输出路径",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_stdout()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    repository = SeedRepository(args.data_dir)

    if args.command == "summary":
        return _summary(repository)
    if args.command == "timeline":
        return _timeline(repository, args.limit)
    if args.command == "analyze":
        return _analyze(repository, args.asset, args.start, args.end)
    if args.command == "report":
        return _report(repository, args.output)

    parser.print_help()
    return 1


def _summary(repository: SeedRepository) -> int:
    materials = repository.load_materials()
    assets = repository.load_assets()
    events = repository.load_events()
    prices = repository.load_price_points()
    material_types = Counter(material.category for material in materials)

    print("Finance History Lab v0.1.0")
    print(f"货币材料：{len(materials)} 类")
    print(f"资产对象：{len(assets)} 个")
    print(f"金融事件：{len(events)} 条")
    print(f"价格观察点：{len(prices)} 条")
    print()
    print("材料分类：")
    for category, count in sorted(material_types.items()):
        print(f"- {category}: {count}")
    print()
    print("可分析资产：")
    for asset in assets:
        print(f"- {asset.id}: {asset.name}（{asset.asset_type}）")
    return 0


def _timeline(repository: SeedRepository, limit: int) -> int:
    service = TimelineService()
    entries = service.build(
        materials=repository.load_materials(),
        events=repository.load_events(),
    )
    selected = entries[:limit] if limit > 0 else entries
    for entry in selected:
        print(f"{format_year(entry.year)} [{entry.kind}] {entry.title}")
        print(f"  {entry.summary}")
    return 0


def _analyze(
    repository: SeedRepository,
    asset_id: str,
    start_year: int | None,
    end_year: int | None,
) -> int:
    analyzer = TrendAnalyzer(repository.load_price_points(), repository.load_events())
    try:
        window = analyzer.analyze_asset(asset_id, start_year=start_year, end_year=end_year)
    except ValueError as exc:
        print(f"分析失败：{exc}", file=sys.stderr)
        return 2

    asset = repository.asset_by_id(asset_id)
    print(f"{asset.name}：{format_year(window.start_year)} 至 {format_year(window.end_year)}")
    print(f"起点价格：{format_decimal(window.start_price)} {window.unit}")
    print(f"终点价格：{format_decimal(window.end_price)} {window.unit}")
    print(f"变化幅度：{format_decimal(window.change_pct)}%")
    print(f"方向判断：{window.direction.value}")
    if window.related_events:
        print("关联事件：")
        for event in window.related_events:
            print(f"- {format_year(event.year)} {event.name}: {event.direct_reason}")
    else:
        print("关联事件：暂无")
    return 0


def _report(repository: SeedRepository, output: Path) -> int:
    builder = MarkdownReportBuilder(repository)
    report = builder.build()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    print(f"报告已生成：{output}")
    return 0


def _configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

