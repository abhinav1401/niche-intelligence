"""Original quota monitor, reading a frozen synthetic ledger."""

import pandas as pd
import streamlit as st

from .quota import QuotaManager

LABELS = {"general": "General API quota", "search": "Search API quota", "batch_stats": "Video Batch Get Stats",
          "requests": "All requests", "per_user": "Requests per user"}


def quota_monitor(store, config, compact=False):
    snapshot = QuotaManager(store, config).snapshot()
    st.subheader("API Quota Monitor")
    st.caption(
        "SYNTHETIC DEMO ACCOUNTING"
        if store.mode == "demo"
        else "LOCALLY TRACKED USAGE · not Google-confirmed usage"
    )
    display = st.warning if snapshot["status"] in {"Quota exhausted", "Low remaining quota"} else st.info
    display(snapshot["status"] + " · " + snapshot["cloud_note"])
    for col, row in zip(st.columns(2), snapshot["daily"][:2], strict=True):
        with col:
            st.metric(LABELS[row["metric"]], f"{row['used']:,} / {row['limit']:,}", delta=None)
            st.progress(min(row["percent"] / 100, 1))
            st.caption(f"{row['remaining']:,} remaining · {row['percent']:.1f}% consumed")
            if row.get("provider_reported_window") is not None:
                st.caption(
                    f"Provider window sample: {row['provider_reported_window']:,.0f}; conservative safe headroom {row['safe_remaining']:,}."
                )
    seconds = snapshot["seconds_remaining"]
    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60
    st.caption(
        f"Quota day: {snapshot['day']} · Reset: {snapshot['reset_pacific']} ({snapshot['timezone']}) · "
        f"{hours}h {minutes}m remaining · Sydney: {snapshot['reset_sydney']}"
    )
    if store.mode == "demo":
        st.caption("Demo clock fixed at 30 Oct 2026, 18:00 UTC; the reset countdown is illustrative.")
    thresholds = store.setting("quota_alert_thresholds", [50, 75, 90])
    for row in snapshot["daily"]:
        level = (
            "Blocked"
            if row["percent"] >= 100
            else "Critical"
            if row["percent"] >= thresholds[2]
            else (
                "Approaching limit"
                if row["percent"] >= thresholds[1]
                else "Informational"
                if row["percent"] >= thresholds[0]
                else ""
            )
        )
        if level:
            st.caption(f"{level}: {LABELS[row['metric']]} at {row['percent']:.1f}% of its local limit.")
    with st.expander("Additional quota buckets, minute limits and accounting details"):
        st.dataframe(
            pd.DataFrame(
                snapshot["daily"]
                + [{**r, "metric": r["metric"] + " / rolling minute"} for r in snapshot["minute"]]
            ),
            hide_index=True,
            use_container_width=True,
        )
        st.caption(
            f"Safety buffer: {snapshot['limits']['buffer']:.0%}. Failed, retried and interrupted reservations stay charged. "
            "Minute protection uses a rolling 60-second window. No counter resets on Streamlit restart."
        )
        if snapshot["reserved_requests"]:
            st.warning(
                f"{snapshot['reserved_requests']} reserved/in-flight or interrupted attempts are conservatively charged."
            )
        if snapshot["suspensions"]:
            st.json(snapshot["suspensions"])
    return snapshot
