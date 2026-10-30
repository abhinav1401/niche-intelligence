"""Portable research bundles with source links, scoring assumptions, and mode labels."""

import json
import zipfile
from io import BytesIO

import pandas as pd

from .classification import taxonomy
from .config import DEFAULT_WEIGHTS
from .db import utcnow
from .public_mode import blocked


def safe_csv(frame):
    frame = frame.copy()

    def cell(value):
        if isinstance(value, (list, dict)):
            value = json.dumps(value, ensure_ascii=False)
        if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")):
            return "'" + value
        return value

    return frame.map(cell).to_csv(index=False)


def idea_markdown(ideas, mode):
    lines = [
        f"# Content backlog — {mode.upper()}",
        "",
        "Concepts are research proposals. Verify factual claims and coverage before production.",
        "",
    ]
    for idea in ideas:
        data = json.loads(idea["data"]) if "data" in idea else idea
        lines.extend(
            [
                f"## {data['title']}",
                "",
                f"Niche: {data['topic']}",
                f"Status: {idea.get('status', 'proposed')} · Rating: {idea.get('rating', 0)}",
                "",
            ]
        )
        for key in [
            "question",
            "series",
            "hook",
            "learning",
            "interest",
            "scenes",
            "complexity",
            "assets",
            "evidence_strength",
            "coverage",
            "angle",
            "research",
        ]:
            lines.extend([f"**{key.replace('_', ' ').title()}:** {data.get(key, '')}", ""])
        for video in data.get("similar_videos", []):
            lines.append(
                f"- [{video['title']}]({video['url']})"
                if video.get("url")
                else f"- {video['title']} (synthetic demo example)"
            )
        lines.extend(["", f"Notes: {idea.get('notes', '')}", ""])
    return "\n".join(lines)


def research_markdown(store, ranking, videos):
    lines = [
        f"# Niche Intelligence — {store.mode.upper()}",
        "",
        f"Exported: {utcnow()}",
        "",
        "**DEMO: entirely fictional; no real market recommendation.**"
        if store.mode == "demo"
        else "Public-metadata sample; opportunity scores are heuristic hypotheses, not market forecasts.",
        "",
        f"Weights: {json.dumps(store.setting('weights', DEFAULT_WEIGHTS))}",
        "",
        "Lifetime view totals are compared within channel, duration group, view-definition era, "
        "180-day publication window, and age cohort. Actual growth requires observed snapshots.",
        "",
    ]
    for _, row in ranking.iterrows():
        lines.extend(
            [
                f"## {row.niche}",
                "",
                row.description,
                "",
                f"Confidence-adjusted score: {row.score}/100; raw: {row.raw_score}/100; "
                f"confidence: {row.confidence_level} ({row.confidence:.0%})",
                "",
                f"Demand {row.demand}; competition {row.competition}; underserved {row.underserved}; "
                f"3D prior {row.advantage}; repeatability {row.repeatability}; momentum {row.momentum}.",
                "",
                f"{row.videos} sampled videos; {row.comparable_videos} comparable; "
                f"{row.successful_creators} independently successful creator groups.",
                "",
                f"**Evidence status:** {row.status}",
                "",
                f"**Gap:** {row.why_underserved}",
                "",
                f"**3D advantage:** {row.why_3d}",
                "",
                f"**Reusable assets:** {row.assets}",
                "",
                f"**Production complexity:** {row.complexity}",
                "",
                f"**Curiosity:** {row.curiosity}",
                "",
                f"**Validation:** {row.experiment}",
                "",
                f"**Research:** {row.research_requirements}",
                "",
                f"**Demand calculation:** {json.dumps(row.demand_calculation)}",
                "",
                f"**Performance basis:** {row.evidence_basis}",
                "",
                f"**Momentum basis:** {row.momentum_basis}",
                "",
                "**Risks and assumptions:**",
                "",
            ]
        )
        lines.extend("- " + warning for warning in row.warnings)
        lines.extend(["", "**Examples from this dataset:**", ""])
        for _, video in videos[videos.id.isin(row.evidence_video_ids)].iterrows():
            label = f"{video.title} — {video.channel_name}; {int(video.views):,} lifetime views"
            lines.append(f"- [{label}]({video.url})" if video.url else "- " + label + " (synthetic)")
        for search in row.coverage_searches:
            lines.append(
                f"- Search: {search['query']} ({search['searched_at']}); sampled IDs: {search['result_ids']}"
            )
        for signal in row.signal_evidence:
            lines.append(f"- Imported {signal['kind']}: {signal['source_url']} — {signal['notes']}")
        lines.append("")
    return "\n".join(lines)


def bundle(store, videos, ranking):
    output = BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("research.md", research_markdown(store, ranking, videos))
        archive.writestr("ranking.csv", safe_csv(ranking))
        archive.writestr("videos.csv", safe_csv(videos))
        ideas = store.rows("SELECT * FROM ideas ORDER BY rating DESC,title")
        expanded = [
            {**json.loads(r["data"]), **{k: r[k] for k in ["status", "rating", "notes", "tags"]}}
            for r in ideas
        ]
        archive.writestr("ideas.csv", safe_csv(pd.DataFrame(expanded)))
        archive.writestr("backlog.md", idea_markdown(ideas, store.mode))
        for table in [
            "channels",
            "snapshots",
            "classifications",
            "runs",
            "searches",
            "signals",
            "reviews",
            "audit",
            "api_requests",
        ]:
            archive.writestr(f"{table}.csv", safe_csv(store.frame(f"SELECT * FROM {table}")))
        archive.writestr("taxonomy.json", json.dumps(taxonomy(store), indent=2))
        if store.rows("SELECT name FROM sqlite_master WHERE type='table' AND name='authorised_metrics'"):
            archive.writestr(
                "authorised_metrics.csv", safe_csv(store.frame("SELECT * FROM authorised_metrics"))
            )
        archive.writestr(
            "manifest.json",
            json.dumps(
                {
                    "mode": store.mode,
                    "exported_at": utcnow(),
                    "heuristic_version": "1.0",
                    "weights": store.setting("weights", DEFAULT_WEIGHTS),
                    "synthetic": store.mode == "demo",
                    "min_peers": store.setting("min_peers", 8),
                    "include_uncertain": store.setting("include_uncertain", False),
                    "analysis_as_of": store.setting("analysis_as_of", utcnow()),
                },
                indent=2,
            ),
        )
    return output.getvalue()



export_to = blocked
