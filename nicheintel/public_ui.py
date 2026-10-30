"""Read-only public navigation around the existing dashboard presentation."""

import json
from functools import lru_cache

import pandas as pd
import plotly.express as px
import streamlit as st

from . import dashboard
from .classification import taxonomy
from .config import ROOT, Config
from .db import Store
from .public_mode import PUBLIC_DEMO_MODE
from .quota import QuotaManager
from .quota_ui import quota_monitor
from .read_models import results

STAGES = [
    "Autonomous topic discovery", "Competitor identification", "Public video data collection",
    "Topic classification", "Video performance analysis", "Niche opportunity evaluation",
    "Research report generation", "Episode concept recommendations",
]
EXPLANATIONS = [
    "The private application starts across twelve subject families and expands searches using coverage and novelty. This example is frozen; selecting a stage sends no search request.",
    "The private workflow samples different creator sizes and subject families, respects exclusions and uses provisional independence groups. The 24 creators here are entirely fictional.",
    "Live collection uses public metadata, uploads playlists, batched statistics and observation timestamps. These 1,920 records were generated offline, not retrieved from YouTube.",
    "Subjects, curiosity mechanisms, storytelling formats and visual advantages are separate labels. This fixture used the existing deterministic local classifier. No model runs here.",
    "The local application compares matched creator baselines and age cohorts, preferring genuine snapshot growth when available. The synthetic calculations below are precomputed; they do not measure real audience behavior.",
    "The five-factor heuristic balances demand evidence, sampled supply, 3D advantage, repeatability and momentum. Confidence and quality-review limitations remain explicit. It does not prove an underserved market.",
    "The frozen report records a synthetic four-creator Small trial and its stage outcomes. Live reports are collection-only until the existing applicable analytics approval requirement is satisfied.",
    "The original idea engine produced distinct episode briefs from its curated catalog. Exact-premise demand and 100-episode capacity remain unvalidated. Visitors cannot generate, save or rate concepts.",
]


@lru_cache(maxsize=1)
def site():
    return json.loads((ROOT / "site.json").read_text())


def legal_ready():
    info = site()
    return all(info.get(key) for key in ["operator_name", "privacy_contact", "support_contact", "effective_date", "legal_review_confirmed"])


def legal_document(name):
    if not legal_ready():
        st.warning("Draft for owner review — operator/contact approval is pending. These pages are not ready for publication or submission to Google.")
    content = (ROOT / "content" / name).read_text()
    info = site()
    replacements = {"OPERATOR_NAME": info["operator_name"], "PRIVACY_CONTACT": info["privacy_contact"],
                    "SUPPORT_CONTACT": info["support_contact"], "EFFECTIVE_DATE": info["effective_date"]}
    for key, value in replacements.items():
        content = content.replace("{{" + key + "}}", value or "[Pending owner approval]")
    st.markdown(content)


def consent():
    if st.session_state.get("public_privacy_accepted", False):
        return True
    st.subheader("Before exploring the demonstration")
    st.write("Read the Privacy Policy and Terms of Service using the links in the sidebar. They remain accessible without agreement. No account or YouTube login is required.")
    if not st.checkbox("I have read and agree to the Privacy Policy and Terms of Service", key="privacy_agreement_widget"):
        st.info("This choice is held only in this browser's temporary Streamlit session. No acceptance record is written to the dataset.")
        return False
    # Non-widget session key survives Streamlit widget cleanup across pages.
    st.session_state["public_privacy_accepted"] = True
    return True


def walkthrough(store):
    st.subheader("Research Control Centre")
    st.caption("Interactive walkthrough of a completed offline example. There is no research worker in this deployment.")
    st.button("Start Niche Research — unavailable in public demo", disabled=True, use_container_width=True)
    stage = st.select_slider("Explore the research workflow", options=STAGES)
    st.info(EXPLANATIONS[STAGES.index(stage)])
    workflow = json.loads((ROOT / "assets" / "workflow.json").read_text())
    summary = workflow["summary"]
    dashboard.metric_row([
        ("Fictional creators discovered", summary["channels_discovered"], "Frozen offline example"),
        ("Creators in example run", summary["channels_selected"], "Small trial scope"),
        ("Videos in selected sample", summary["videos_in_selected_sample"], "Existing synthetic records"),
        ("Simulated searches", summary["queries_executed"], "No real API calls"),
    ])
    with st.expander("Recorded example stages and report"):
        st.dataframe(pd.DataFrame(summary["stages"]), hide_index=True, use_container_width=True)
        st.download_button("Download synthetic example report", workflow["report"], file_name="synthetic-research-example.md")
        with st.expander("Read the frozen report"):
            st.markdown(workflow["report"])
    quota_monitor(store, Config())


def settings(store):
    st.title("Settings and Data Health")
    st.write("Read-only configuration and synthetic data health. Live settings, credentials, imports and collection are unavailable.")
    tabs = st.tabs(["Competitor list", "Collection", "Analysis and taxonomy", "Research imports", "Health and API"])
    with tabs[0]:
        st.info("All creators are fictional. Adding, approving, excluding and deleting creators are disabled here.")
        st.dataframe(store.frame("SELECT name,category,subscribers,status,source FROM channels"), hide_index=True, use_container_width=True)
    with tabs[1]:
        st.subheader("Collection demonstration")
        st.write("The private application uses each channel's uploads playlist, batches video lookups, records snapshots and respects Shorts uncertainty. This deployment has no collection implementation.")
        st.button("Collect or refresh — disabled", disabled=True)
        st.dataframe(store.frame("SELECT short_status,COUNT(*) videos FROM videos GROUP BY short_status"), hide_index=True)
    with tabs[2]:
        st.write("Synthetic labels and weights are frozen. Manual corrections, taxonomy edits, model calls and cluster mutations cannot execute.")
        st.json(store.setting("weights", {"demand": 30, "underserved": 25, "advantage": 20, "repeatability": 15, "momentum": 10}))
        selected = st.selectbox("Inspect a taxonomy entry", [item["name"] for item in taxonomy(store)])
        st.json(next(item for item in taxonomy(store) if item["name"] == selected))
    with tabs[3]:
        st.info("Uploads and imports are unavailable. The local application supports authorised research exports and supported CSV imports; no visitor files are accepted here.")
    with tabs[4]:
        st.subheader("Deployment safety")
        st.write("PUBLIC_DEMO_MODE: enforced. YouTube API: unavailable. Paid models: unavailable. Workers and schedules: unavailable. Data store: immutable synthetic fixture. Google Cloud reconciliation: not connected.")
        quota_monitor(store, Config())
        st.subheader("Quota Usage History — frozen synthetic example")
        history = QuotaManager(store).history()
        endpoint = st.multiselect("Filter example endpoints", sorted(history.endpoint.unique()))
        if endpoint:
            history = history[history.endpoint.isin(endpoint)]
        if not history.empty:
            daily = history[history.period == "day"].groupby(["quota_day", "metric"], as_index=False).units.sum()
            dashboard.plot(px.bar(daily, x="quota_day", y="units", color="metric", barmode="group"))
        st.dataframe(history, hide_index=True, use_container_width=True)
        st.caption("Overlapping quota constraints are not extra requests. Nothing in this view represents Google-reported usage or activity by this public server.")
        st.subheader("Synthetic database statistics")
        st.dataframe(pd.DataFrame([{"table": table, "rows": store.rows(f"SELECT COUNT(*) n FROM {table}")[0]["n"]} for table in ["channels", "videos", "snapshots", "classifications", "ideas"]]), hide_index=True)


def render(page):
    if not consent():
        return
    store = Store()
    if page == "Settings and Data Health":
        settings(store)
        return
    videos, ranking = results()
    if page == "Overview":
        st.title("Find the question worth animating.")
        st.write("Explore how Niche Intelligence evaluates questions for original 3D-animated Shorts, using synthetic evidence.")
        st.info("Live derived analytics remain subject to applicable YouTube API policy acceptance. This demonstration is not connected to YouTube, and no approval is claimed.")
        walkthrough(store)
        dashboard.overview(store, videos, ranking, show_header=False)
    elif page == "Competitor Explorer":
        dashboard.competitors(store, videos)
    elif page == "Viral Outlier Explorer":
        dashboard.outliers(store, videos)
    elif page == "Topic Intelligence":
        dashboard.topic_intelligence(store, videos, ranking)
    elif page == "Niche Opportunity Ranking":
        dashboard.ranking_page(store, videos, ranking)
    elif page == "Market Gap Explorer":
        dashboard.gaps(store, Config(), videos, ranking)
    elif page == "Idea Backlog":
        dashboard.backlog(store, Config(), videos, ranking)


def overview():
    render("Overview")


def competitors():
    render("Competitor Explorer")


def outliers():
    render("Viral Outlier Explorer")


def topics():
    render("Topic Intelligence")


def ranking():
    render("Niche Opportunity Ranking")


def gaps():
    render("Market Gap Explorer")


def backlog():
    render("Idea Backlog")


def health():
    render("Settings and Data Health")


def about():
    st.markdown((ROOT / "content" / "about.md").read_text())


def privacy():
    legal_document("privacy.md")


def terms():
    legal_document("terms.md")


def run():
    st.set_page_config(page_title="Niche Intelligence — Public Demonstration", page_icon="◈", layout="wide")
    st.html("<style>" + (ROOT / "assets" / "theme.css").read_text() + "</style>")
    pages = [
        st.Page(overview, title="Overview", default=True),
        st.Page(competitors, title="Competitor Explorer", url_path="competitors"),
        st.Page(outliers, title="Viral Outlier Explorer", url_path="outliers"),
        st.Page(topics, title="Topic Intelligence", url_path="topics"),
        st.Page(ranking, title="Niche Opportunity Ranking", url_path="opportunities"),
        st.Page(gaps, title="Market Gap Explorer", url_path="market-gaps"),
        st.Page(backlog, title="Idea Backlog", url_path="ideas"),
        st.Page(health, title="Settings and Data Health", url_path="settings"),
        st.Page(about, title="About This Application", url_path="about"),
        st.Page(privacy, title="Privacy Policy", url_path="privacy-policy"),
        st.Page(terms, title="Terms of Service", url_path="terms-of-service"),
    ]
    selected = st.navigation(pages, position="hidden")
    if PUBLIC_DEMO_MODE is not True or site().get("public_demo_mode") is not True:
        st.error("Public demonstration configuration is invalid; access is disabled.")
        st.stop()
    with st.sidebar:
        st.markdown("## ◈ NICHE INTELLIGENCE")
        st.caption("THE 3D STORY RESEARCH DESK")
        st.caption("PUBLIC DEMO ONLY · READ-ONLY")
        for page in pages[:8]:
            st.page_link(page)
        st.divider()
        for page in pages[8:]:
            st.page_link(page)
        st.caption("Fictional examples. No live YouTube connection, research jobs or saved visitor edits.")
        st.markdown("[YouTube Terms](https://www.youtube.com/t/terms) · [Google Privacy](https://policies.google.com/privacy)")
    st.warning("Public Demonstration — Synthetic Data")
    st.caption("24 fictional creators · 1,920 synthetic videos · fixed research date: 30 October 2026 · all scores are illustrative")
    selected.run()
