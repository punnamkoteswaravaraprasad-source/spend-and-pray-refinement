"""One selection model for every dashboard chart and KPI."""
from dashboard_charts import order_day


def select_report(rows, campaigns, channels, campaign_ids, statuses, dates=None):
    selected_campaigns = [c for c in campaigns if c['campaign_id'] in campaign_ids
                          and (c.get('channel') or 'Unknown') in channels]
    ids = {c['campaign_id'] for c in selected_campaigns}
    selected = []
    for row in rows:
        if row['status'] not in statuses or row['channel'] not in channels:
            continue
        if row['status'] == 'Matched' and row['campaign_id'] not in ids:
            continue
        if row['status'] != 'Matched' and '__unassigned__' not in campaign_ids:
            continue
        if dates:
            day = order_day(row.get('order_date'))
            if day is None or not dates[0] <= day <= dates[1]:
                continue
        selected.append(row)
    return selected, selected_campaigns


def amount(value):
    import math
    try:
        number = float(value or 0)
        return number if math.isfinite(number) else 0.0
    except (ValueError, TypeError):
        return 0.0
