from __future__ import annotations

import re


def test_index_page_served_with_main_elements(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    html = resp.text
    for marker in (
        'id="robots-table"',
        "btn-start",
        "btn-stop",
        'id="alerts-section"',
        'id="robot-form"',
    ):
        assert marker in html


def test_ui_refresh_interval_within_5_seconds(client):
    html = client.get("/").text
    match = re.search(r"REFRESH_MS\s*=\s*(\d+)", html)
    assert match is not None
    assert int(match.group(1)) <= 5000
    assert "setInterval(refresh, REFRESH_MS)" in html
