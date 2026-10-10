"""Test SourceFolderResolver + kiểm file bắt buộc."""
from datetime import date

from robot.u1_consume.source_folder import (
    INDIVIDUAL_FILE,
    ORG_FILE,
    REQUIRED_FILES_COMMON,
    SourceFolderResolver,
)


def _make_cif_folder(tmp_path, cif, files):
    d = date.today()
    folder = tmp_path / d.strftime("%Y%m") / d.strftime("%Y%m%d") / cif
    folder.mkdir(parents=True)
    for name in files:
        (folder / name).write_text("x", encoding="utf-8")
    return folder


def test_resolve_found(tmp_path):
    _make_cif_folder(tmp_path, "6670501", [])
    resolver = SourceFolderResolver(str(tmp_path))
    assert resolver.resolve("6670501") is not None


def test_resolve_not_found(tmp_path):
    resolver = SourceFolderResolver(str(tmp_path))
    assert resolver.resolve("9999999") is None


def test_missing_files_detected(tmp_path):
    folder = _make_cif_folder(tmp_path, "C1", [INDIVIDUAL_FILE])  # thiếu 3 common
    missing = SourceFolderResolver.missing_required_files(str(folder))
    assert set(missing) == set(REQUIRED_FILES_COMMON)


def test_all_required_present_khcn(tmp_path):
    folder = _make_cif_folder(tmp_path, "C2", REQUIRED_FILES_COMMON + [INDIVIDUAL_FILE])
    assert SourceFolderResolver.missing_required_files(str(folder)) == []


def test_missing_individual_and_org(tmp_path):
    folder = _make_cif_folder(tmp_path, "C3", REQUIRED_FILES_COMMON)
    missing = SourceFolderResolver.missing_required_files(str(folder))
    assert any("hoặc" in m for m in missing)
