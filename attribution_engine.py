import csv
import math
from datetime import datetime, timezone
import uuid
from data_store import append_unique
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent / "data"
ORDERS_FILE = DATA_DIR / "demo_orders.csv"
CAMPAIGNS_FILE = DATA_DIR / "campaigns.csv"


def load_csv(file_path):
    if not file_path.exists():
        return []
    with open(file_path, "r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def match_order(order, campaigns):
    campaign_id = (order.get("campaign_id") or "").strip()
    promo_code = (order.get("promo_code") or "").strip().upper()

    id_match = None
    promo_match = None

    for campaign in campaigns:
        saved_id = (campaign.get("campaign_id") or "").strip()
        saved_promo = (campaign.get("promo_code") or "").strip().upper()

        if campaign_id and campaign_id == saved_id:
            id_match = campaign
        if promo_code and saved_promo and promo_code == saved_promo:
            promo_match = campaign

    if id_match and promo_match:
        if id_match["campaign_id"] != promo_match["campaign_id"]:
            return "Needs Review", None

    if id_match:
        return "Matched", id_match
    if promo_match:
        return "Matched", promo_match
    if campaign_id or promo_code:
        return "Needs Review", None
    return "Unattributed", None


def process_orders(scope='Customer orders'):
    if scope not in ('Customer orders', 'Illustrative sample', 'Combined'):
        raise ValueError('Unknown data scope')
    orders, campaigns = [], []
    if scope in ('Customer orders', 'Combined'):
        orders = [dict(row, data_source='Customer orders') for row in load_csv(ORDERS_FILE)]
        campaigns = [dict(row, data_source='Customer orders') for row in load_csv(CAMPAIGNS_FILE)]
    if scope in ('Illustrative sample', 'Combined'):
        for row in load_csv(DATA_DIR / 'sample_orders.csv'):
            item = dict(row, data_source='Illustrative sample')
            item['order_id'] = 'SAMPLE:' + (row.get('order_id') or '')
            item['campaign_id'] = 'SAMPLE:' + row['campaign_id'] if row.get('campaign_id') else ''
            orders.append(item)
        for row in load_csv(DATA_DIR / 'sample_campaigns.csv'):
            item = dict(row, data_source='Illustrative sample')
            item['campaign_id'] = 'SAMPLE:' + row['campaign_id']
            campaigns.append(item)
    results = []
    reviews = {r['order_id']: r for r in load_csv(DATA_DIR / 'attribution_reviews.csv')}


    for order in orders:
        source_campaigns = [c for c in campaigns if c['data_source'] == order['data_source']]
        status, campaign = match_order(order, source_campaigns)
        reason = ('Campaign ID and promo code cannot be verified together. Check the original campaign source.'
                  if status == 'Needs Review' else 'No campaign ID or promo code was captured.'
                  if status == 'Unattributed' else 'Tracking signal matched a saved campaign.')
        review = reviews.get(order.get('order_id')) if order['data_source'] == 'Customer orders' else None
        if review:
            if review['decision'] == 'Unattributed':
                status, campaign = 'Unattributed', None
                reason = 'Owner reviewed: ' + review['note']
            elif review['decision'] == 'Matched':
                manual = next((c for c in campaigns if c['campaign_id'] == review['campaign_id']), None)
                if manual:
                    status, campaign = 'Matched', manual
                    reason = 'Owner assigned: ' + review['note']
                else:
                    status, campaign = 'Needs Review', None
                    reason = 'Previously assigned campaign no longer exists. Review again.'

        try:
            revenue = float(order.get("order_total") or 0)
            if not math.isfinite(revenue):
                revenue = 0.0
        except (ValueError, TypeError):
            revenue = 0.0

        results.append(
            {
                "order_id": order.get("order_id", ""),
                "data_source": order["data_source"],
                "customer_name": (order.get("customer_name") or "").strip() or "Name not recorded",
                "reason": reason,
                "reviewed": bool(review),
                "order_date": order.get("order_date", ""),
                "items": order.get("items", ""),
                "revenue": revenue,
                "status": status,
                "campaign_id": (
                    campaign.get("campaign_id", "")
                    if campaign
                    else order.get("campaign_id", "")
                ),
                "campaign_name": (
                    campaign.get("campaign_name", "")
                    if campaign
                    else "Not verified"
                ),
                "channel": (
                    campaign.get("channel", "")
                    if campaign
                    else "Unknown"
                ),
            }
        )

    return results, campaigns


def calculate_kpis(results):
    total_orders = len(results)
    matched_orders = sum(1 for row in results if row["status"] == "Matched")
    unattributed_orders = sum(
        1 for row in results if row["status"] == "Unattributed"
    )
    needs_review = sum(
        1 for row in results if row["status"] == "Needs Review"
    )
    total_revenue = sum(row["revenue"] for row in results)
    matched_revenue = sum(
        row["revenue"] for row in results if row["status"] == "Matched"
    )
    coverage = matched_orders / total_orders * 100 if total_orders else 0
    average_order_value = total_revenue / total_orders if total_orders else 0

    return {
        "total_orders": total_orders,
        "matched_orders": matched_orders,
        "unattributed_orders": unattributed_orders,
        "needs_review": needs_review,
        "total_revenue": total_revenue,
        "matched_revenue": matched_revenue,
        "coverage": coverage,
        "unattributed_rate": unattributed_orders / total_orders * 100 if total_orders else 0,
        "needs_review_rate": needs_review / total_orders * 100 if total_orders else 0,
        "average_order_value": average_order_value,
    }


def save_review(order_id, decision, campaign_id, note):
    if decision not in ('Matched', 'Unattributed', 'Automatic') or not note.strip():
        raise ValueError('Choose a decision and provide a review note.')
    if not any(r.get('order_id') == order_id for r in load_csv(ORDERS_FILE)):
        raise ValueError('Order no longer exists.')
    if decision == 'Matched' and not any(c.get('campaign_id') == campaign_id for c in load_csv(CAMPAIGNS_FILE)):
        raise ValueError('Select an existing campaign.')
    row = dict(review_id=uuid.uuid4().hex, order_id=order_id, decision=decision,
               campaign_id=campaign_id if decision == 'Matched' else '', note=note.strip(),
               reviewed_at=datetime.now(timezone.utc).isoformat())
    append_unique(DATA_DIR / 'attribution_reviews.csv', list(row), row, 'review_id')
