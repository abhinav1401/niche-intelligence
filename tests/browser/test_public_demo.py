"""Opt-in browser verification, including mobile navigation and network observations."""

import json
import os
from urllib.parse import urlparse

import pytest

pw = pytest.importorskip("playwright.sync_api")
URL = os.getenv("PUBLIC_DEMO_TEST_URL")
CLOUD = bool(URL and (urlparse(URL).hostname or "").endswith(".streamlit.app"))
# Community Cloud forces usage statistics on and supplies these telemetry
# destinations. Keep this exception exact; unknown app-frame egress must fail.
CLOUD_TELEMETRY_HOSTS = {"data.streamlit.io", "webhooks.fivetran.com"}
pytestmark = pytest.mark.skipif(not URL, reason="Start the isolated public demo and set PUBLIC_DEMO_TEST_URL")
PAGES = [
    ("Overview", "Find the question worth animating."),
    ("Competitor Explorer", "Competitor Explorer"),
    ("Viral Outlier Explorer", "Viral Outlier Explorer"),
    ("Topic Intelligence", "Topic Intelligence"),
    ("Niche Opportunity Ranking", "Niche Opportunity Ranking"),
    ("Market Gap Explorer", "Market Gap Explorer"),
    ("Idea Backlog", "Idea Backlog"),
    ("Settings and Data Health", "Settings and Data Health"),
    ("About This Application", "About This Application"),
    ("Privacy Policy", "Privacy Policy"),
    ("Terms of Service", "Terms of Service"),
]
TABS = ["Competitor list", "Collection", "Analysis and taxonomy", "Research imports", "Health and API"]


def surface(page):
    """Community Cloud wraps the unchanged application in a hosting iframe."""
    return page.frame_locator('iframe[title="streamlitApp"]') if CLOUD else page


def ready(page):
    pw.expect(page.get_by_role("button", name="Stop", exact=True)).not_to_be_visible(timeout=60000)


def navigate(page, label):
    app = surface(page)
    expand = app.get_by_role("button", name="Expand sidebar", exact=True)
    if expand.is_visible():
        expand.click()
    app.locator('[data-testid="stSidebar"]').get_by_role("link", name=label, exact=True).click()
    ready(app)
    collapse = app.get_by_role("button", name="Collapse sidebar", exact=True)
    if page.viewport_size["width"] < 1000 and collapse.is_visible():
        collapse.click()
    if page.viewport_size["width"] < 1000:
        pw.expect(app.locator('[data-testid="stSidebar"]')).to_have_attribute("data-collapsed", "true")
        pw.expect(app.get_by_role("button", name="Expand sidebar", exact=True)).to_be_visible()
    app.locator('[data-testid="stMain"]').evaluate("e=>e.scrollTop=0")


def geometry(page):
    data = surface(page).locator("body").evaluate("""() => {
      const main=document.querySelector('[data-testid="stMain"]');
      const first=main.querySelector('p');const h=main.querySelector('h1');
      return {first:first.getBoundingClientRect().top, heading:h.getBoundingClientRect().top,
      header:document.querySelector('[data-testid="stHeader"]').getBoundingClientRect().bottom,
      overflow:document.documentElement.scrollWidth>innerWidth,
      errors:[...main.querySelectorAll('[data-testid="stException"]')].map(e=>e.innerText)};
    }""")
    assert not data["errors"], data
    assert data["first"] >= data["header"] - 0.5, data
    assert data["heading"] >= data["header"] - 0.5, data
    assert not data["overflow"], data
    assert not page.evaluate("() => document.documentElement.scrollWidth > innerWidth")
    return data


@pytest.mark.parametrize("width,height", [(1440, 1000), (390, 844)])
def test_pages_tabs_filters_and_mobile_navigation(tmp_path, width, height):
    with pw.sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": width, "height": height})
        page = context.new_page()
        hosts, application_hosts = set(), set()

        def record_request(request):
            host = urlparse(request.url).hostname
            hosts.add(host)
            try:
                if not CLOUD or "/~/+/" in request.frame.url:
                    application_hosts.add(host)
            except pw.Error:
                pass  # Hosting/service-worker traffic has no application frame.

        page.on("request", record_request)
        page.goto(URL)
        app = surface(page)
        consent = app.get_by_text("I have read and agree to the Privacy Policy and Terms of Service", exact=True)
        consent.click()
        pw.expect(app.get_by_role("heading", name="Find the question worth animating.", exact=True)).to_be_visible()
        results = []
        for label, heading in PAGES:
            navigate(page, label)
            pw.expect(app.get_by_role("heading", name=heading, exact=True)).to_be_visible(timeout=30000)
            pw.expect(app.get_by_text("Public Demonstration — Synthetic Data", exact=True)).to_be_visible()
            results.append({"page": label, **geometry(page)})
            if label == "Overview":
                assert app.get_by_role("button", name="Start Niche Research — unavailable in public demo").is_disabled()
            if label == "Viral Outlier Explorer":
                app.get_by_text("Outliers only", exact=True).click()
                pw.expect(app.get_by_role("checkbox", name="Outliers only", exact=True)).not_to_be_checked()
                ready(app)
            if label == "Idea Backlog":
                assert app.get_by_role("button", name="Generate and save concepts — unavailable in public demo").is_disabled()
            if label == "Settings and Data Health":
                for tab in TABS:
                    app.get_by_role("tab", name=tab, exact=True).click()
                    results.append({"tab": tab, **geometry(page)})
        app.locator("body").evaluate("() => document.fonts.ready.then(() => true)")
        page.screenshot(path=str(tmp_path / f"public-demo-{width}.png"))
        (tmp_path / "measurements.json").write_text(json.dumps(results, indent=2))
        (tmp_path / "request-hosts.json").write_text(json.dumps({"all_hosts": sorted(str(h) for h in hosts), "application_hosts": sorted(str(h) for h in application_hosts)}, indent=2))
        allowed_application_hosts = {urlparse(URL).hostname, None}
        if CLOUD:
            allowed_application_hosts |= CLOUD_TELEMETRY_HOSTS
        assert application_hosts <= allowed_application_hosts, application_hosts
        if not CLOUD:
            assert hosts <= {urlparse(URL).hostname, None}, hosts
        # Session acknowledgement must not leak to another visitor.
        visitor = browser.new_context(viewport={"width": width, "height": height})
        other = visitor.new_page()
        other.goto(URL)
        pw.expect(surface(other).get_by_text("Before exploring the demonstration", exact=True)).to_be_visible()
        visitor.close()
        browser.close()


def test_direct_legal_urls_need_no_consent_and_have_no_private_paths(tmp_path):
    with pw.sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page()
        for path, title in [("privacy-policy", "Privacy Policy"), ("terms-of-service", "Terms of Service"), ("about", "About This Application")]:
            page.goto(URL.rstrip("/") + "/" + path)
            app = surface(page)
            pw.expect(app.get_by_role("heading", name=title, exact=True)).to_be_visible(timeout=90000)
            pw.expect(app.locator('[data-testid="stSidebar"]').get_by_role("link", name="Privacy Policy", exact=True)).to_be_visible(timeout=60000)
            ready(app)
            assert "/Users/" not in app.locator("body").inner_text()
            if title != "About This Application":
                pw.expect(app.get_by_text("Draft", exact=False)).not_to_be_visible()
                assert "steering9954@gmail.com" in app.locator("body").inner_text()
            assert not app.locator('[data-testid="stException"]').count()
            page.screenshot(path=str(tmp_path / f"legal-{path}.png"), full_page=True)
        browser.close()
