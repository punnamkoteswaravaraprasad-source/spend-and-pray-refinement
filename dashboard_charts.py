"""Chart builders shared by the dashboard and its verification checks."""
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import plotly.graph_objects as go

from ui import BRAND_RED, chart_layout


def order_day(value):
    """Use UTC dates consistently; historical naive timestamps are treated as UTC."""
    try:
        parsed = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(timezone.utc)
        return parsed.date()
    except (ValueError, TypeError):
        return None


def revenue_chart(rows, weekly=False):
    totals = defaultdict(float)
    invalid = 0
    for row in rows:
        day = order_day(row.get("order_date"))
        if day is None:
            invalid += 1
            continue
        if weekly:
            day -= timedelta(days=day.weekday())
        totals[day] += row["revenue"]
    days = sorted(totals)
    fig = go.Figure()
    # Explicit category dates prevent Plotly's single-date millisecond tick range.
    x = [day.isoformat() for day in days]
    common = dict(x=x, y=[totals[d] for d in days],
                  hovertemplate="%{x}<br>Revenue: $%{y:,.2f}<extra></extra>")
    if len(days) == 1:
        fig.add_trace(go.Bar(**common, marker_color=BRAND_RED,
                             text=[f"${totals[days[0]]:,.2f}"], textposition="outside",
                             cliponaxis=False))
    elif days:
        fig.add_trace(go.Scatter(**common, mode="lines+markers",
                                 line=dict(color=BRAND_RED, width=3), marker_size=9))
    fig.update_layout(**chart_layout("Revenue Over Time", "Revenue ($)", 430))
    # Numeric day offsets keep gaps between observed dates proportional without
    # adding fictional zero-revenue dates. Tick text never includes time values.
    if len(days) > 1:
        offsets = [(d - days[0]).days for d in days]
        fig.data[0].x = offsets
        fig.data[0].customdata = x
        fig.data[0].hovertemplate = "%{customdata}<br>Revenue: $%{y:,.2f}<extra></extra>"
        indices = sorted(set(round(i * (len(days) - 1) / min(3, len(days) - 1)) for i in range(min(4, len(days)))))
        fig.update_xaxes(type="linear", tickmode="array", tickvals=[offsets[i] for i in indices],
                         ticktext=[days[i].strftime("%b %d<br>%Y") for i in indices])
    else:
        fig.update_xaxes(type="category", tickmode="array", tickvals=x,
                         ticktext=[d.strftime("%b %d<br>%Y") for d in days])
    fig.update_xaxes(title_text="Date", title_standoff=20)
    fig.update_yaxes(type="linear", tickprefix="$", tickformat=",.2f", rangemode="tozero")
    if len(days) == 1 and totals[days[0]] >= 0:
        fig.update_yaxes(range=[0, totals[days[0]] * 1.25 or 1])
    period = "week" if weekly else "date"
    note = (f"Only one {period} is available for this selection; the bar shows its total revenue, not a trend."
            if len(days) == 1 else f"Actual {'weekly (Monday start)' if weekly else 'daily'} totals, grouped by UTC date. Only observed dates are connected.")
    if not days:
        note = "No valid order dates are available for this selection."
    if invalid:
        note += f" {invalid} order(s) excluded because their dates are missing or invalid."
    return fig, note


def cumulative_revenue_chart(rows):
    """An explicit order-sequence view; never present this as a date trend."""
    valid = []
    for index, row in enumerate(rows):
        try:
            stamp = datetime.fromisoformat(str(row.get('order_date', '')).strip().replace('Z', '+00:00'))
            stamp = stamp.replace(tzinfo=timezone.utc) if stamp.tzinfo is None else stamp.astimezone(timezone.utc)
            valid.append((stamp, index, row))
        except (ValueError, TypeError):
            continue
    valid.sort(key=lambda item: (item[0], item[1]))
    amounts, running = [], 0.0
    for _, _, row in valid:
        running += row['revenue']
        amounts.append(running)
    fig = go.Figure()
    if len(valid) == 1:
        fig.add_trace(go.Bar(x=[1], y=amounts, marker_color=BRAND_RED,
                             text=[f'${running:,.2f}'], textposition='outside', cliponaxis=False))
    elif valid:
        fig.add_trace(go.Scatter(x=list(range(1, len(valid)+1)), y=amounts,
                                 mode='lines+markers', line=dict(color=BRAND_RED, width=3, shape='hv'),
                                 hovertemplate='Order %{x}<br>Cumulative revenue: $%{y:,.2f}<extra></extra>'))
    fig.update_layout(**chart_layout('Cumulative Revenue by Order', 'Cumulative revenue ($)', 430))
    fig.update_xaxes(title_text='Order sequence', dtick=1, rangemode='tozero')
    fig.update_yaxes(tickprefix='$', tickformat=',.2f', rangemode='tozero')
    note = 'Running total after each valid dated order, sorted chronologically in UTC. This is an order sequence, not a daily or weekly trend. Orders with identical timestamps retain their recorded order.'
    if not valid:
        note = 'No valid dated orders are available for the cumulative view.'
    elif len(valid) == 1:
        note = 'Only one valid dated order is available; a revenue bar is shown instead of a curve.'
    excluded = len(rows) - len(valid)
    if excluded:
        note += f' {excluded} order(s) excluded because dates are missing or invalid; their revenue remains in all-date KPI totals.'
    return fig, note
