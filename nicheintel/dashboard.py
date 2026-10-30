"""Presentation reused from the local dashboard, with mutation forms removed."""

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from .export import bundle, idea_markdown, safe_csv
from .ideas import adjacent_opportunities
from .public_mode import blocked

PAGES = ["Overview", "Competitor Explorer", "Viral Outlier Explorer", "Topic Intelligence",
         "Niche Opportunity Ranking", "Market Gap Explorer", "Idea Backlog", "Settings and Data Health"]
COLORS = ["#007F73", "#5168AD", "#D9973B", "#C65A66", "#60A89F", "#95A5C8"]
service_action = invalidate = blocked


def plot(fig, key=None):
    fig.update_layout(
        font_family="Arial",
        font_color="#334A5D",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=8, t=24, b=8),
        colorway=COLORS,
        height=340,
    )
    st.plotly_chart(fig, use_container_width=True, key=key)


def metric_row(items):
    for col, (label, value, detail) in zip(st.columns(len(items)), items, strict=False):
        col.metric(label, value)
        col.caption(detail)


def video_cards(videos, limit=12):
    for _, row in videos.head(limit).iterrows():
        with st.container(border=True):
            image_col, content = st.columns([1, 5])
            if row.thumbnail:
                image_col.image(row.thumbnail, use_container_width=True)
            else:
                image_col.markdown("### ◈")
                image_col.caption("Demo example" if row.source == "synthetic_demo" else "No thumbnail")
            content.markdown(f"**{row.title}**")
            content.caption(
                f"{row.channel_name} · {row.published_at[:10]} · {row.duration}s · {row.eligibility}"
            )
            views = f"{int(row.views):,}" if pd.notna(row.views) else "Unavailable"
            ratio = f"{row.performance_ratio:.2f}×" if pd.notna(row.performance_ratio) else "Unavailable"
            content.write(f"{views} public views · {ratio} relative lift")
            content.caption(row.performance_basis)
            if row.url:
                content.link_button("Open on YouTube ↗", row.url)


def detail_view(store, row, videos):
    st.subheader(row["niche"])
    st.write(row["description"])
    st.caption(row["status"])
    metric_row(
        [
            ("Adjusted opportunity", f"{row['score']:.1f}", f"Raw heuristic: {row['raw_score']:.1f}"),
            ("Demand", f"{row['demand']:.0f}/100", row["demand_class"]),
            ("Sampled competition", f"{row['competition']:.0f}/100", "Not total-market saturation"),
            ("Confidence", f"{row['confidence']:.0%}", row["confidence_level"]),
        ]
    )
    evidence, production, risks = st.tabs(
        ["Evidence and calculations", "Channel concept", "Risks and next experiment"]
    )
    with evidence:
        st.write(
            f"{row['comparable_videos']} age-comparable videos · {row['outliers']} outliers · "
            f"{row['successful_creators']} independently successful creator groups · "
            f"{row['success_months']} publication months with success"
        )
        factors = pd.DataFrame(
            {
                "Factor": [
                    "Demand",
                    "Underserved supply",
                    "3D advantage prior",
                    "Repeatability prior",
                    "Momentum",
                ],
                "Score": [
                    row[k] for k in ["demand", "underserved", "advantage", "repeatability", "momentum"]
                ],
            }
        )
        plot(
            px.bar(
                factors,
                x="Score",
                y="Factor",
                orientation="h",
                range_x=[0, 100],
                color_discrete_sequence=COLORS,
            )
        )
        st.write("**Why a gap might exist:** " + row["why_underserved"])
        st.write("**Performance evidence:** " + row["evidence_basis"])
        st.write("**Momentum:** " + row["momentum_basis"])
        st.json(
            {
                "demand_components_0_100": row["demand_calculation"],
                "sampled_creators": row["creators"],
                "recent_sampled_uploads": row["recent_videos"],
                "observed_uploads_per_month": row["uploads_per_month_observed"],
                "view_concentration_HHI": row["hhi"],
                "leading_creator_view_share": row["top_creator_share"],
                "coverage_queries": row["coverage_queries"],
                "quality_review_count": row["quality_reviews"],
                "mean_reviewed_quality_1_5": row["quality_mean"],
                "imported_signals": row["supplemental_signals"],
            }
        )
        examples = videos[videos.id.isin(row["evidence_video_ids"])].sort_values("age_ratio", ascending=False)
        video_cards(examples, 4)
        with st.expander("All competing channels in this sample"):
            channels = store.frame("SELECT id,name,url,category FROM channels")
            st.dataframe(
                channels[channels.id.isin(row["competitor_ids"])],
                hide_index=True,
                column_config={"url": st.column_config.LinkColumn("YouTube")},
                use_container_width=True,
            )
        with st.expander("Coverage searches, quality reviews and imported sources"):
            st.json(
                {
                    "searches": row["coverage_searches"],
                    "reviews": row["review_evidence"],
                    "signals": row["signal_evidence"],
                }
            )
    with production:
        st.write("**Audience curiosity:** " + row["curiosity"])
        st.write("**Why 3D adds value:** " + row["why_3d"])
        st.write("**Reusable production assets:** " + row["assets"])
        st.write("**Complexity estimate:** " + row["complexity"])
        st.info(
            f"{row['catalog_capacity']} curated distinct premises available. The 100-episode channel-identity "
            "criterion requires further validation. Generate additional concepts with an optional model or "
            "extend the taxonomy catalog; the generator does not pad a count with paraphrases."
        )
    with risks:
        for warning in row["warnings"]:
            st.warning(warning)
        st.write("**Next validation experiment:** " + row["experiment"])
        st.write("**Factual research requirements:** " + row["research_requirements"])


def overview(store, videos, ranking, show_header=True):
    if show_header:
        st.title("Find the question worth animating.")
        st.write("A research desk for curiosity, hidden mechanisms, and evidence of unmet viewer interest.")
    if videos.empty:
        st.info(
            "No collected evidence yet. Click Start Niche Research above to discover creators and collect "
            "evidence automatically. Manual research controls remain available in Settings."
        )
        return
    channels = store.rows("SELECT id FROM channels WHERE status='approved'")
    eligible = int(videos.eligible_for_analysis.sum())
    subjects = store.rows(
        "SELECT COUNT(DISTINCT video_id) n FROM classifications WHERE dimension='subject' "
        "AND label!='Unclassified'"
    )[0]["n"]
    metric_row(
        [
            ("Creators analysed", len(channels), "Approved competitor list"),
            ("Videos collected", f"{len(videos):,}", "Includes longer-form context"),
            ("Eligible Shorts", f"{eligible:,}", "Likely + confirmed; ≥24h old"),
            ("Viral outliers", int(videos.outlier.sum()), "≥3× matched median + interval check"),
        ]
    )
    left, right = st.columns([1.3, 1])
    with left:
        st.subheader("Opportunity shortlist")
        if not ranking.empty:
            plot(
                px.bar(
                    ranking.head(7).iloc[::-1],
                    x="score",
                    y="niche",
                    orientation="h",
                    labels={"score": "Confidence-adjusted opportunity", "niche": ""},
                    color="demand",
                    color_continuous_scale=["#C3DDD8", "#007F73"],
                    range_x=[0, 100],
                )
            )
        else:
            st.info("Classify collected videos to build a shortlist.")
    with right:
        st.subheader("Evidence coverage")
        metric_row(
            [
                ("Topic clusters", len(ranking), "Observed classified topics"),
                ("Classification", f"{subjects / max(len(videos), 1):.0%}", "Videos with a subject label"),
            ]
        )
        plot(
            px.pie(
                videos.groupby("eligibility").size().reset_index(name="videos"),
                names="eligibility",
                values="videos",
                hole=0.7,
                color_discrete_sequence=COLORS,
            )
        )
    st.subheader("Research readout")
    if not ranking.empty:
        leader = ranking.iloc[0]
        st.write(
            f"**{leader.niche}** leads this {'fictional demo' if store.mode == 'demo' else 'collected sample'} "
            f"at **{leader.score:.1f}/100**, supported by {leader.successful_creators} independently "
            f"successful creator groups. Its evidence status is **{leader.status.lower()}**."
        )
    st.caption(
        "Freshest collection: "
        + str(videos.collected_at.max())
        + " · Public engaged views, retention, and swipe-away rates are unavailable for competitors."
    )
    st.download_button(
        "Export complete research bundle ↓",
        bundle(store, videos, ranking),
        file_name=f"research-{store.mode}.zip",
        mime="application/zip",
    )


def competitors(store, videos):
    st.title("Competitor Explorer")
    st.write("Study the audience and topic landscape across 3D, illustration, and live footage.")
    if videos.empty:
        st.info("Approve channels and collect uploads in Settings to populate this view.")
        return
    channels = store.frame("SELECT * FROM channels WHERE status='approved'")
    categories = st.multiselect("Channel categories", sorted(channels.category.unique()))
    sort = st.selectbox("Sort creators by", ["Outlier frequency", "Typical views", "Subscribers", "Name"])
    cards = []
    for _, c in channels.iterrows():
        g = videos[videos.channel_id == c.id]
        scored = g[g.age_ratio.notna()]
        cards.append(
            {
                **c.to_dict(),
                "n": len(g),
                "median": scored.views.median(),
                "frequency": scored.outlier.mean() if len(scored) else 0,
                "dominant": ", ".join(g.topics.str.split(", ").explode().value_counts().head(2).index),
            }
        )
    data = pd.DataFrame(cards)
    if categories:
        data = data[data.category.isin(categories)]
    key = {
        "Outlier frequency": "frequency",
        "Typical views": "median",
        "Subscribers": "subscribers",
        "Name": "name",
    }[sort]
    data = data.sort_values(key, ascending=sort == "Name")
    for start in range(0, len(data), 3):
        for col, (_, c) in zip(st.columns(3), data.iloc[start : start + 3].iterrows(), strict=False):
            with col.container(border=True):
                if c.thumbnail:
                    st.image(c.thumbnail, width=56)
                st.subheader(c["name"])
                subscribers = f"{int(c.subscribers):,}" if pd.notna(c.subscribers) else "Unavailable"
                st.caption(f"{c.category} · {subscribers} subscribers")
                st.write(f"**{c.n}** analysed videos · **{c.frequency:.0%}** outlier frequency")
                st.write(
                    f"Typical lifetime views: **{int(c['median']):,}**"
                    if pd.notna(c["median"])
                    else "Typical performance: insufficient comparable sample"
                )
                st.caption(c.dominant or "No topic classifications yet")
                if c.url:
                    st.link_button("Visit channel ↗", c.url)


def outliers(store, videos):
    st.title("Viral Outlier Explorer")
    st.write("Find unusually strong videos, then inspect the comparison that supports the result.")
    if videos.empty:
        st.info("No collected videos yet.")
        return
    a, b, c = st.columns([2, 1, 1])
    channel = a.multiselect("Creators", sorted(videos.channel_name.unique()))
    only_outliers = b.checkbox("Outliers only", True)
    min_views = c.number_input("Minimum views", 0, value=0, step=10000)
    g = videos.copy()
    if only_outliers:
        g = g[g.outlier]
    if channel:
        g = g[g.channel_name.isin(channel)]
    g = g[g.views >= min_views]
    topics = sorted({x for value in videos.topics for x in value.split(", ")})
    selected_topic = st.selectbox("Topic filter", ["All topics"] + topics)
    if selected_topic != "All topics":
        g = g[g.topics.str.split(", ").apply(lambda x: selected_topic in x)]
    order = st.selectbox(
        "Sort videos by",
        ["performance_ratio", "age_ratio", "outlier_ratio", "views", "published_at", "growth_7d"],
    )
    g = g.sort_values(order, ascending=False)
    st.caption(
        "Outlier = matched-peer lift ≥3× and bootstrap lower ratio ≥2×; minimum "
        f"{store.setting('min_peers', 8)} peers. Observed growth takes priority when matched observations exist; "
        "otherwise age-cohort totals approximate exposure, not first-week views."
    )
    st.dataframe(
        g[
            [
                "title",
                "channel_name",
                "views",
                "performance_ratio",
                "performance_basis",
                "age_ratio",
                "performance_ci_low",
                "performance_ci_high",
                "outlier_ratio",
                "performance_peer_n",
                "eligibility",
                "published_at",
                "topics",
                "url",
            ]
        ],
        hide_index=True,
        use_container_width=True,
        column_config={
            "url": st.column_config.LinkColumn("Original video"),
            "performance_ratio": st.column_config.NumberColumn("Selected evidence lift", format="%.2f×"),
            "performance_ci_low": st.column_config.NumberColumn("Selected lower ratio", format="%.2f×"),
            "performance_ci_high": st.column_config.NumberColumn("Selected upper ratio", format="%.2f×"),
            "performance_peer_n": st.column_config.NumberColumn("Matched peers"),
            "age_ratio": st.column_config.NumberColumn("Age-cohort lift", format="%.2f×"),
            "outlier_ratio": st.column_config.NumberColumn("Channel-relative lift", format="%.2f×"),
        },
    )
    if g.empty:
        st.info("No videos match these filters. Sparse cohorts remain unscored.")
        return
    st.subheader("Evidence cards")
    video_cards(g)
    picked = st.selectbox(
        "Inspect a video", g.id.tolist(), format_func=lambda x: g.set_index("id").loc[x, "title"]
    )
    row = g[g.id == picked].iloc[0]
    with st.expander("Supporting calculations and synthetic observations", expanded=True):
        st.write(row.baseline_note)
        st.json(
            {
                k: None if pd.isna(row[k]) else row[k]
                for k in [
                    "views",
                    "performance_ratio",
                    "performance_basis",
                    "performance_baseline",
                    "performance_peer_n",
                    "performance_ci_low",
                    "performance_ci_high",
                    "observed_growth_window",
                    "age_days",
                    "age_cohort",
                    "channel_median",
                    "baseline_n",
                    "outlier_ratio",
                    "age_cohort_median",
                    "age_cohort_n",
                    "age_ratio",
                    "ratio_ci_low",
                    "ratio_ci_high",
                    "robust_log_z",
                    "growth_1d",
                    "growth_1d_elapsed",
                    "growth_7d",
                    "growth_7d_elapsed",
                    "growth_30d",
                    "growth_30d_elapsed",
                ]
            }
        )
        st.dataframe(
            store.frame(
                "SELECT captured_at,views,likes,comments,source FROM snapshots WHERE video_id=?", (picked,)
            ),
            hide_index=True,
        )
        st.caption(
            "In the live application, growth uses real stored observations near the requested interval. "
            "A blank value means unavailable. A 30-day interval needs permitted extended retention."
        )
    with st.expander("Review Shorts eligibility and explanation quality"):
        st.caption(row.short_reason)
        st.info("Eligibility and quality reviews are frozen synthetic examples. Changes are disabled.")



def topic_intelligence(store, videos, ranking):
    st.title("Topic Intelligence")
    st.write("Separate the subject from its curiosity mechanism, format, and visual opportunity.")
    if ranking.empty:
        st.info("Classify videos in Settings to create topic intelligence.")
        return
    selected = st.selectbox("Explore topic", ranking.niche.tolist())
    g = videos[videos.topics.str.split(", ").apply(lambda x: selected in x)]
    left, right = st.columns([1.4, 1])
    with left:
        monthly = (
            g.assign(month=g.published.dt.strftime("%Y-%m"))
            .groupby("month")
            .agg(median_relative_lift=("age_ratio", "median"), videos=("id", "count"))
            .reset_index()
        )
        plot(
            px.line(
                monthly,
                x="month",
                y="median_relative_lift",
                markers=True,
                labels={"median_relative_lift": "Median age-cohort lift", "month": "Publication month"},
            )
        )
        st.caption("Publication-cohort comparison, not historical growth or search demand.")
    with right:
        labels = store.frame(
            """SELECT dimension,label,COUNT(*) videos,AVG(confidence) confidence
            FROM classifications WHERE video_id IN (SELECT video_id FROM classifications
            WHERE dimension='subject' AND label=?) GROUP BY dimension,label""",
            (selected,),
        )
        st.dataframe(labels[labels.dimension != "subject"], hide_index=True, use_container_width=True)
    detail_view(store, ranking[ranking.niche == selected].iloc[0].to_dict(), videos)


def ranking_page(store, videos, ranking):
    st.title("Niche Opportunity Ranking")
    st.write("Prioritise a validation experiment using five configurable factors and an evidence adjustment.")
    if ranking.empty:
        st.info("No scored niches yet. Collect and classify videos first.")
        return
    threshold = st.slider("Minimum confidence", 0, 85, 0, format="%d%%")
    table = ranking[ranking.confidence >= threshold / 100]
    cols = [
        "niche",
        "score",
        "raw_score",
        "confidence_level",
        "confidence",
        "demand",
        "competition",
        "underserved",
        "advantage",
        "repeatability",
        "momentum",
        "successful_creators",
        "catalog_capacity",
        "status",
    ]
    st.dataframe(
        table[cols],
        hide_index=True,
        use_container_width=True,
        column_config={
            "score": st.column_config.ProgressColumn("Adjusted score", min_value=0, max_value=100),
            "confidence": st.column_config.NumberColumn("Confidence", format="%.2f"),
        },
    )
    st.download_button("Download ranking CSV", safe_csv(table), file_name=f"ranking-{store.mode}.csv")
    if not table.empty:
        selected = st.selectbox("Open niche research", table.niche.tolist())
        detail_view(store, table[table.niche == selected].iloc[0].to_dict(), videos)
    st.caption(
        "Initial heuristic weights: demand 30%, underserved 25%, 3D advantage 20%, "
        "repeatability 15%, momentum 10%. Weights are frozen in this public demonstration. Scores are not scientifically validated."
    )


def gaps(store, config, videos, ranking):
    st.title("Market Gap Explorer")
    st.write("Look for strong demand beside weak reviewed explanations. An empty corner is a hypothesis.")
    if ranking.empty:
        st.info("Collect and classify videos before exploring market gaps.")
        return
    fig = px.scatter(
        ranking,
        x="competition",
        y="demand",
        size="comparable_videos",
        size_max=48,
        color="confidence",
        hover_name="niche",
        hover_data=["score", "successful_creators", "status"],
        range_x=[0, 100],
        range_y=[0, 100],
        color_continuous_scale=["#C4D7D9", "#007F73"],
        labels={"competition": "Sampled supply pressure →", "demand": "Demand evidence →"},
    )
    fig.add_vline(x=50, line_dash="dot", line_color="#BBC8D4")
    fig.add_hline(y=50, line_dash="dot", line_color="#BBC8D4")
    plot(fig, "gap_matrix")
    st.caption(
        "Bubble size = age-comparable video count; colour = confidence. Axes describe this sample. "
        "High demand/high supply suggests a crowded sample; low supply/low demand remains unproven."
    )
    selected = st.selectbox("Explore adjacent questions", ranking.niche.tolist())
    adjacent = adjacent_opportunities(store, selected, videos)
    st.dataframe(
        pd.DataFrame(adjacent).drop(columns=["evidence", "query"]), hide_index=True, use_container_width=True
    )
    question = st.selectbox("Inspect a question and its coverage", [r["question"] for r in adjacent])
    candidate = next(r for r in adjacent if r["question"] == question)
    st.write("**Underlying curiosity:** " + candidate["curiosity"])
    st.json(candidate["evidence"])
    history = store.rows(
        "SELECT * FROM searches WHERE topic=? AND query=? AND purpose='coverage'", (selected, question)
    )
    if history:
        with st.expander("Official API search evidence", expanded=True):
            for search in history:
                st.caption(search["searched_at"] + " · Non-exhaustive relevance sample")
                for vid in json.loads(search["result_ids"]):
                    st.markdown(f"[Open sampled competing video ↗](https://www.youtube.com/watch?v={vid})")
    if st.button("Search existing YouTube coverage", disabled=store.mode == "demo"):
        service_action(store, config, lambda api: {"results": len(api.coverage(question, selected))})
    st.caption(
        "Coverage searches discover candidates for the approval queue. Search result volume is "
        "coverage evidence, not YouTube query volume or Shorts feed demand."
    )


def backlog(store, config, videos, ranking):
    st.title("Idea Backlog")
    st.write("Build recurring series from distinctive questions, then record what still needs validation.")
    st.info("Precomputed synthetic concepts. Generation, paid models and saving are disabled.")
    st.button("Generate and save concepts — unavailable in public demo", disabled=True)
    rows = store.rows("SELECT * FROM ideas ORDER BY rating DESC,created_at DESC")
    if not rows:
        st.info(
            "Generate a concept set to begin your backlog. No real viewer demand is assumed for new ideas."
        )
        return
    frame = pd.DataFrame(rows)
    a, b, c = st.columns(3)
    topic_filter = a.multiselect("Backlog niches", sorted(frame.topic.unique()))
    status_filter = b.multiselect(
        "Backlog status", ["proposed", "saved", "researching", "validated", "rejected"]
    )
    search = c.text_input("Search concepts, notes or tags")
    if topic_filter:
        frame = frame[frame.topic.isin(topic_filter)]
    if status_filter:
        frame = frame[frame.status.isin(status_filter)]
    if search:
        frame = frame[
            (frame.title + " " + frame.notes + " " + frame.tags).str.contains(search, case=False, regex=False)
        ]
    st.dataframe(
        frame[["title", "topic", "status", "rating", "tags", "notes"]],
        hide_index=True,
        use_container_width=True,
    )
    a, b = st.columns(2)
    expanded = [
        {**json.loads(r["data"]), **{k: r[k] for k in ["status", "rating", "notes", "tags"]}}
        for r in frame.to_dict("records")
    ]
    a.download_button(
        "Export concepts CSV", safe_csv(pd.DataFrame(expanded)), file_name=f"ideas-{store.mode}.csv"
    )
    b.download_button(
        "Export backlog Markdown",
        idea_markdown(frame.to_dict("records"), store.mode),
        file_name=f"backlog-{store.mode}.md",
    )
    if frame.empty:
        return
    picked = st.selectbox(
        "Review concept", frame.id.tolist(), format_func=lambda x: frame.set_index("id").loc[x, "title"]
    )
    row = next(r for r in rows if r["id"] == picked)
    idea = json.loads(row["data"])
    st.subheader(idea["title"])
    st.info(idea["evidence_strength"])
    for key in [
        "series",
        "subtopic",
        "hook",
        "learning",
        "interest",
        "scenes",
        "complexity",
        "assets",
        "coverage",
        "angle",
        "research",
    ]:
        st.write(f"**{key.title()}:** {idea.get(key, '')}")
    with st.expander("Similar sampled videos"):
        st.json(idea.get("similar_videos", []))
    st.caption("Read-only editorial review. Visitor filters are temporary; no notes or ratings are saved.")
    st.json({key: row[key] for key in ["status", "rating", "tags", "notes"]})
