from pathlib import Path

from streamlit.testing.v1 import AppTest

from nicheintel.dashboard import PAGES

ROOT = Path(__file__).resolve().parents[1]


def launch(path="", consent=True):
    app = AppTest.from_file(str(ROOT / "app.py"))
    if path:
        # Exercise the same page functions through a small Streamlit navigation harness.
        script = f'from nicheintel.public_ui import render\nrender({path!r})'
        app = AppTest.from_string(script)
    if consent:
        app.session_state["public_privacy_accepted"] = True
    return app.run(timeout=90)


def test_initial_gate_requires_privacy_agreement_without_live_controls():
    app = launch(consent=False)
    assert not app.exception
    assert any("Public Demonstration — Synthetic Data" in warning.value for warning in app.warning)
    assert any("I have read and agree" in checkbox.label for checkbox in app.checkbox)
    assert not any("Start Niche Research" in button.label for button in app.button)


def test_all_eight_original_dashboard_pages_render_read_only():
    for page in PAGES:
        app = launch(page)
        assert not app.exception, f"{page}: {app.exception}"
        for button in app.button:
            assert not any(word in button.label for word in ["Collect", "Generate and save", "Start Niche Research", "refresh"]) or button.disabled
        assert not app.text_area and not app.get("file_uploader")


def test_walkthrough_changes_only_temporary_session_state():
    app = launch("Overview")
    slider = next(x for x in app.select_slider if x.label == "Explore the research workflow")
    slider.set_value("Episode concept recommendations").run(timeout=90)
    assert not app.exception
    assert any("Visitors cannot generate" in info.value for info in app.info)


def test_information_and_legal_pages_are_accessible_without_agreement():
    for function, title in [("about", "About This Application"), ("privacy", "Privacy Policy"), ("terms", "Terms of Service")]:
        app = AppTest.from_string(f'from nicheintel.public_ui import {function}\n{function}()').run(timeout=60)
        assert not app.exception
        assert any(title in entry.value for entry in app.markdown)
