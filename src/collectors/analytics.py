from fastapi import HTTPException

from src.config import get_settings
from src.models.metrics import AnalyticsMetrics


def collect_analytics_metrics(property_id: str, start_date: str, end_date: str) -> AnalyticsMetrics:
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

        client = BetaAnalyticsDataClient()
        base = dict(property=f"properties/{property_id}", date_ranges=[DateRange(start_date=start_date, end_date=end_date)])
        totals_response = client.run_report(RunReportRequest(**base, metrics=[Metric(name=name) for name in ("activeUsers", "sessions", "screenPageViews", "eventCount")]))
        totals = {header.name: _value(totals_response.rows[0].metric_values[index].value) for index, header in enumerate(totals_response.metric_headers)} if totals_response.rows else {}
        source_response = client.run_report(RunReportRequest(**base, dimensions=[Dimension(name="sessionSource")], metrics=[Metric(name="sessions")], limit=10))
        page_response = client.run_report(RunReportRequest(**base, dimensions=[Dimension(name="pageTitle")], metrics=[Metric(name="screenPageViews")], limit=10))
        return AnalyticsMetrics(timestamp=get_settings().now(), property_id=property_id, start_date=start_date, end_date=end_date, totals=totals, top_sources=_rows(source_response, "sessionSource"), top_pages=_rows(page_response, "pageTitle"))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Google Analytics indisponivel: {exc}") from exc


def _value(value: str) -> int | float:
    try:
        return float(value) if "." in value else int(value)
    except ValueError:
        return 0


def _rows(response, dimension_name: str) -> list[dict[str, str | int | float]]:
    return [{dimension_name: row.dimension_values[0].value, "value": _value(row.metric_values[0].value)} for row in response.rows]
