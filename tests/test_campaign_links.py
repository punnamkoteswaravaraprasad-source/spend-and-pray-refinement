import unittest
from urllib.parse import parse_qs, urlsplit
from campaign_links import campaign_link


class CampaignLinksTests(unittest.TestCase):
    def test_current_site_and_tracking_are_preserved(self):
        campaign = dict(campaign_id="CMP-123", utm_source="market & event")
        for origin in ["http://127.0.0.1:8502", "https://new-app.streamlit.app"]:
            url = campaign_link(campaign, origin + "/create_campaign?old=value")
            self.assertTrue(url.startswith(origin + "/?"))
            self.assertEqual(parse_qs(urlsplit(url).query)["utm_source"], ["market & event"])

    def test_subpath_and_missing_context(self):
        self.assertTrue(campaign_link({}, "https://example.com/demo/create_campaign").startswith(
            "https://example.com/demo/?"))
        self.assertTrue(campaign_link({}).startswith("./?"))
