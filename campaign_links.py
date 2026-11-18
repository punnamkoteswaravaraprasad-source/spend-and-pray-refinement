"""Build campaign assets against the app currently being viewed."""
from urllib.parse import urlencode, urlsplit, urlunsplit


def campaign_link(campaign, app_url=None):
    params = {key: campaign.get(key) or "" for key in
              ("campaign_id", "utm_source", "utm_medium", "utm_campaign")}
    if not app_url:
        # Relative navigation works even when browser context is unavailable.
        return "./?" + urlencode(params)
    current = urlsplit(app_url)
    base = current.path.rstrip("/")
    if base.endswith("/create_campaign"):
        base = base[:-len("/create_campaign")]
    return urlunsplit((current.scheme, current.netloc,
                       base + "/", urlencode(params), ""))
