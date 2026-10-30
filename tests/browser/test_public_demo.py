"""Opt-in browser verification, including mobile navigation and network observations."""

import json
import os
from urllib.parse import urlparse

import pytest

pw = pytest.importorskip("playwright.sync_api")
URL = os.getenv("PUBLIC_DEMO_TEST_URL")
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


def ready(page):
    pw.expect(page.get_by_role("button", name="Stop", exact=True)).not_to_be_visible(timeout=60000)


def navigate(page, label):
    expand = page.get_by_role("button", name="Expand sidebar", exact=True)
    if expand.is_visible():
        expand.click()
    page.locator('[data-testid="stSidebar"]').get_by_role("link", name=label, exact=True).click()
    ready(page)
    collapse = page.get_by_role("button", name="Collapse sidebar", exact=True)
    if page.viewport_size["width"] < 1000 and collapse.is_visible():
        collapse.click()
    if page.viewport_size["width"] < 1000:
        page.wait_for_function("""() => document.querySelector('[data-testid="stSidebar"]').getBoundingClientRect().right <= 1""", timeout=10000)
    page.locator('[data-testid="stMain"]').evaluate("e=>e.scrollTop=0")


def geometry(page):
    data = page.evaluate("""() => {
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
    return data


@pytest.mark.parametrize("width,height", [(1440, 1000), (390, 844)])
def test_pages_tabs_filters_and_mobile_navigation(tmp_path, width, height):
    with pw.sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": width, "height": height})
        page = context.new_page()
        hosts = set()
        page.on("request", lambda request: hosts.add(urlparse(request.url).hostname))
        page.goto(URL)
        consent = page.get_by_text("I have read and agree to the Privacy Policy and Terms of Service", exact=True)
        consent.click()
        pw.expect(page.get_by_role("heading", name="Find the question worth animating.", exact=True)).to_be_visible()
        results = []
        for label, heading in PAGES:
            navigate(page, label)
            pw.expect(page.get_by_role("heading", name=heading, exact=True)).to_be_visible(timeout=30000)
            pw.expect(page.get_by_text("Public Demonstration — Synthetic Data", exact=True)).to_be_visible()
            results.append({"page": label, **geometry(page)})
            if label == "Overview":
                assert page.get_by_role("button", name="Start Niche Research — unavailable in public demo").is_disabled()
            if label == "Viral Outlier Explorer":
                page.get_by_text("Outliers only", exact=True).click()
                pw.expect(page.get_by_role("checkbox", name="Outliers only", exact=True)).not_to_be_checked()
                ready(page)
            if label == "Idea Backlog":
                assert page.get_by_role("button", name="Generate and save concepts — unavailable in public demo").is_disabled()
            if label == "Settings and Data Health":
                for tab in TABS:
                    page.get_by_role("tab", name=tab, exact=True).click()
                    results.append({"tab": tab, **geometry(page)})
        page.evaluate("() => document.fonts.ready.then(() => true)")
        page.screenshot(path=str(tmp_path / f"public-demo-{width}.png"))
        (tmp_path / "measurements.json").write_text(json.dumps(results, indent=2))
        assert hosts <= {urlparse(URL).hostname, None}, hosts
        # Session acknowledgement must not leak to another visitor.
        visitor = browser.new_context(viewport={"width": width, "height": height})
        other = visitor.new_page()
        other.goto(URL)
        pw.expect(other.get_by_text("Before exploring the demonstration", exact=True)).to_be_visible()
        visitor.close()
        browser.close()


def test_direct_legal_urls_need_no_consent_and_have_no_private_paths():
    with pw.sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page()
        for path, title in [("privacy-policy", "Privacy Policy"), ("terms-of-service", "Terms of Service"), ("about", "About This Application")]:
            page.goto(URL.rstrip("/") + "/" + path)
            pw.expect(page.get_by_role("heading", name=title, exact=True)).to_be_visible(timeout=30000)
            assert "/Users/" not in page.locator("body").inner_text()
            assert not page.locator('[data-testid="stException"]').count()
        browser.close()
