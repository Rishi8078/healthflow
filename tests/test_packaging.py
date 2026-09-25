"""Packaging and documentation checks for Healthflow."""

from __future__ import annotations

import json
import re
from pathlib import Path

from custom_components.healthflow.const import (
    NUTRITION_SCOPE,
    SCOPES,
    SETTINGS_SCOPE,
)

ROOT = Path(__file__).resolve().parents[1]
def test_hacs_metadata_marks_custom_integration() -> None:
    metadata = json.loads((ROOT / "hacs.json").read_text(encoding="utf-8"))

    assert metadata["name"] == "Healthflow"
    assert metadata["content_in_root"] is False
    assert metadata["render_readme"] is True
    assert metadata["homeassistant"] == "2026.7.2"
    assert set(metadata) == {
        "name",
        "content_in_root",
        "render_readme",
        "homeassistant",
    }


def test_readme_documents_baseline_and_optional_read_only_scopes() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for scope in (*SCOPES, NUTRITION_SCOPE, SETTINGS_SCOPE):
        assert scope in readme
    assert "three baseline read-only scopes" in readme
    assert "two optional read-only scopes" in readme
    assert "write" not in readme.lower()
    assert "writeonly" not in readme.lower()
    assert "Energy dashboard remains outside this integration" in readme


def test_readme_uses_public_identity_without_stale_release_claims() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert readme.startswith("# Healthflow\n")
    assert "Release 1.0.3" not in readme
    assert "Release 1.0.4" not in readme
    assert "0.3.0" not in readme


def test_readme_documents_expanded_metrics_release_contract() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for documented_text in (
        "## Expanded Metrics",
        "Enabled by default",
        "Active-zone minutes",
        "Daily VO2 max",
        "Daily oxygen saturation",
        "Daily respiratory rate",
        "Sleep respiratory rate",
        "Floors today",
        "Sedentary minutes today",
        "Heart-rate-zone minutes",
        "Disabled by default",
        "active-zone minutes for fat-burn, cardio, and peak zones",
        "heart-rate-zone minutes for light, moderate, vigorous, and peak zones",
        "calories for light, moderate, vigorous, and peak heart-rate zones",
        "sleep respiratory rate for deep, light, and REM sleep",
        "Weight",
        "Body-fat percentage",
        "Height",
        "include_body_measurements",
        "include_nutrition",
        "include_paired_devices",
        "90-day normalized backfill",
        "reconciled daily summaries and daily rollups",
        "Nutrition has no historical backfill in this release.",
        "Paired-device last sync",
        "unavailable",
        "valid zero",
        "raw API payloads",
        "Google identifiers",
        "## Installation and upgrade",
    ):
        assert documented_text in readme


def test_readme_documents_reconciliation_and_exact_poll_request_counts() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for documented_text in (
        "Google-reconciled all-source stream",
        "fully successful, non-paginated refresh",
        "36 logical data requests",
        "39 when body measurements are enabled",
        "Nutrition adds two",
        "Paired devices add one",
        "one-time authentication retry",
        "Pagination can increase the actual HTTP request count",
        "Authentication failure stops the remaining poll immediately",
        "individual metric failures are isolated",
        "Only expanded-metric polling avoids raw high-volume streams",
    ):
        assert documented_text in readme


def test_manifest_preserves_required_public_codeowner() -> None:
    manifest = json.loads(
        (ROOT / "custom_components" / "healthflow" / "manifest.json").read_text(
            encoding="utf-8"
        )
    )

    assert manifest["codeowners"] == ["@Rishi8078"]


def test_changelog_documents_expanded_metrics_and_backfill_release() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    release = changelog.split("## 1.0.0", maxsplit=1)[1]

    assert "Expanded active-zone" in release
    assert "history backfill" in release
    assert "strict normalized history validation" in release


def test_changelog_documents_bounded_backfill_fix() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    release = changelog.split("## 1.0.1", maxsplit=1)[1].split("## 1.0.0", maxsplit=1)[0]

    assert "seven-day windows" in release
    assert "pagination safety limits" in release
    assert "restart Home Assistant once" in release


def test_changelog_documents_optional_health_capabilities_beta_release() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    assert changelog.index("## 1.1.0-beta.1") < changelog.index("## 1.0.4")
    beta_release = changelog.split("## 1.1.0-beta.1", maxsplit=1)[1].split(
        "## 1.0.4", maxsplit=1
    )[0]
    for phrase in (
        "include_nutrition",
        "include_paired_devices",
        "Total calories burned today",
        "Body-fat percentage",
        "Paired-device last sync",
        "no historical nutrition backfill",
        "existing config entries",
        "per person",
    ):
        assert phrase in beta_release


def test_changelog_documents_beta_two_data_fixes() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    assert changelog.index("## 1.1.0-beta.2") < changelog.index("## 1.1.0-beta.1")
    beta_release = changelog.split("## 1.1.0-beta.2", maxsplit=1)[1].split(
        "## 1.1.0-beta.1", maxsplit=1
    )[0]
    for phrase in (
        "Total calories burned today",
        "historical Height",
        "release branch",
        "restart Home Assistant once",
    ):
        assert phrase in beta_release


def test_changelog_documents_stable_official_integration_parity_release() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    assert changelog.index("## 1.1.0 -") < changelog.index("## 1.1.0-beta.2")
    release = changelog.split("## 1.1.0 -", maxsplit=1)[1].split(
        "## 1.1.0-beta.2", maxsplit=1
    )[0]
    for phrase in (
        "Total calories burned today",
        "Body-fat percentage",
        "Water consumed today",
        "googlehealth.nutrition.readonly",
        "Reauthenticate",
        "Do not delete or re-add",
        "existing entity IDs",
    ):
        assert phrase in release


def test_changelog_documents_performance_diagnostics_beta() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    assert changelog.index("## 1.1.1-beta.1") < changelog.index("## 1.1.0 -")
    release = " ".join(
        changelog.split("## 1.1.1-beta.1", maxsplit=1)[1]
        .split("## 1.1.0 -", maxsplit=1)[0]
        .split()
    )
    for phrase in (
        "latest 12 operations",
        "downloadable diagnostics",
        "not a claimed CPU fix",
        "four normal 15-minute polling cycles",
        "diagnostics for every configured person",
        "No OAuth reauthorization is required",
        "No new sensors",
        "existing entity IDs",
    ):
        assert phrase in release


def test_fixture_provenance_is_documented() -> None:
    provenance = (ROOT / "tests" / "fixtures" / "README.md").read_text(encoding="utf-8")
    normalized = " ".join(provenance.split())

    for required_text in (
        "All fixtures in this directory are synthetic test data",
        "generate_steps_fixture.py",
        "fixed fictional date in 2042",
        "no random input or external data source",
        "hand-authored synthetic contract examples",
        "not copied from an account, device, diagnostic, or live response",
    ):
        assert required_text in normalized


def test_test_data_uses_future_dates_except_documented_dst_boundaries() -> None:
    legacy_year = "".join(("20", "26"))
    serialized_date = re.compile(rf"{legacy_year}-(?P<month>\d{{2}})-")
    constructed_date = re.compile(
        rf"(?:date|datetime)\({legacy_year}, (?P<month>\d{{1,2}}),"
    )
    mapping_date = re.compile(
        rf"[\"']year[\"']\s*:\s*[\"']?{legacy_year}[\"']?\s*,\s*"
        r"[\"']month[\"']\s*:\s*(?P<month>\d{1,2})\s*,"
    )
    permitted_dst_files = {"test_api.py", "test_coordinator.py"}
    paths = (*sorted((ROOT / "tests").glob("*.py")), ROOT / "tests" / "fixtures")

    for path in paths:
        if path.is_dir():
            fixture_text = "\n".join(
                child.read_text(encoding="utf-8")
                for child in sorted(path.iterdir())
                if child.is_file()
            )
            texts = ((path, fixture_text),)
        else:
            texts = ((path, path.read_text(encoding="utf-8")),)

        for source, text in texts:
            for pattern in (serialized_date, constructed_date, mapping_date):
                for match in pattern.finditer(text):
                    assert source.name in permitted_dst_files
                    assert int(match.group("month")) in {3, 11}


def test_inline_payloads_exclude_record_and_device_identifier_fields() -> None:
    identifier_keys = (
        "".join(("external", "Id")),
        "".join(("health", "UserId")),
        "".join(("record", "Id")),
        "".join(("resource", "Name")),
        "".join(("source", "Id")),
        "".join(("user", "Id")),
        "".join(("web", "ClientId")),
        "".join(("device", "Id")),
        "".join(("device", "Identifier")),
    )
    assignment = re.compile(
        rf"[\"'](?:{'|'.join(re.escape(key) for key in identifier_keys)})[\"']\s*:"
    )

    for path in (*sorted((ROOT / "tests").glob("*.py")), ROOT / "tests" / "fixtures"):
        if path.is_dir():
            text = "\n".join(
                child.read_text(encoding="utf-8")
                for child in sorted(path.iterdir())
                if child.is_file()
            )
        else:
            text = path.read_text(encoding="utf-8")
        assert assignment.search(text) is None, path


def test_readme_documents_exactly_one_post_download_restart() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    install_first = (
        "1. Install or update Healthflow in HACS and wait until the download "
        "is fully complete."
    )
    restart_lines = [
        line.strip() for line in readme.splitlines() if "restart home assistant" in line.lower()
    ]

    assert install_first in readme
    assert restart_lines == [
        "2. Do not restart Home Assistant earlier, even if HACS prompts you.",
        "3. After the install or update is fully downloaded, restart Home Assistant exactly once.",
    ]
    assert (
        readme.index(install_first)
        < readme.index(restart_lines[0])
        < readme.index(restart_lines[1])
    )


def test_manifest_versions_performance_diagnostics_beta() -> None:
    manifest = json.loads(
        (ROOT / "custom_components" / "healthflow" / "manifest.json").read_text(
            encoding="utf-8"
        )
    )

    assert manifest["version"] == "1.1.1-beta.1"


def test_gitignore_blocks_credential_artifacts() -> None:
    ignored = set((ROOT / ".gitignore").read_text(encoding="utf-8").splitlines())

    assert "client_secret*.json" in ignored
    assert "*token*.json" in ignored
    assert ".env" in ignored
    assert "*.credentials.json" in ignored
    assert ".pytest_cache/" in ignored
    assert ".mypy_cache/" in ignored
    assert ".ruff_cache/" in ignored
