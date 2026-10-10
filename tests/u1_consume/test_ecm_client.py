"""Test EcmClientAdapter với transport mock."""
import pytest

from robot.config import EcmConfig
from robot.logging_setup import StructuredLogger
from robot.u1_consume.ecm_client import EcmClientAdapter, EcmError


def _logger(tmp_path):
    return StructuredLogger(str(tmp_path / "log.json"), echo_stdout=False)


class FakeTransport:
    def __init__(self, files_by_code=None, fail_token=False):
        self.files_by_code = files_by_code or {}
        self.fail_token = fail_token

    def post_token(self, config):
        if self.fail_token:
            raise RuntimeError("token lỗi")
        return "fake-token"

    def search_files(self, config, token, business_code, cif):
        return self.files_by_code.get(business_code, [])

    def download_content(self, config, token, doc_id):
        return b"%PDF-1.4 fake"


def _config():
    return EcmConfig(business_codes=["mb_smart_channel", "customer_info_ca"], retries=1)


def test_fetch_dossier_gathers_pdfs(tmp_path):
    transport = FakeTransport(files_by_code={"mb_smart_channel": [{"doc_id": "d1"}, {"doc_id": "d2"}]})
    client = EcmClientAdapter(_config(), _logger(tmp_path), transport, str(tmp_path / "out"))
    # fetch_dossier trả (danh sách path PDF, mã số thuế trích xuất) — tuple[list[str], str]
    paths, _mst = client.fetch_dossier("6670501")
    assert len(paths) == 2
    import os

    assert all(os.path.isfile(p) for p in paths)


def test_fetch_dossier_token_failure_raises(tmp_path):
    transport = FakeTransport(fail_token=True)
    client = EcmClientAdapter(_config(), _logger(tmp_path), transport, str(tmp_path / "out"))
    with pytest.raises(EcmError):
        client.fetch_dossier("6670501")


def test_fetch_dossier_no_files_returns_empty(tmp_path):
    transport = FakeTransport(files_by_code={})
    client = EcmClientAdapter(_config(), _logger(tmp_path), transport, str(tmp_path / "out"))
    # Không có file: danh sách path rỗng (MST trích xuất rỗng)
    paths, _mst = client.fetch_dossier("6670501")
    assert paths == []
