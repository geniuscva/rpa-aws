"""Đọc cấu hình robot từ data/config.yaml.

Secrets (user/pass, client_secret) để trong config.yaml (không hardcode, không
commit). Không log giá trị secret.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import yaml


@dataclass
class KafkaConfig:
    bootstrap_servers: str = "localhost:9092"
    topic: str = "RPA_STR_NHNN_INPUT"
    group_id: str = "rpa-str-consumer"
    security_protocol: str = "PLAINTEXT"
    sasl_mechanism: str = "PLAIN"
    sasl_plain_username: str = ""
    sasl_plain_password: str = ""


@dataclass
class EcmConfig:
    base_url: str = "http://localhost:8831"
    token_path: str = "/auth/realms/ms-core/protocol/openid-connect/token"
    client_id: str = ""
    client_secret: str = ""
    business_codes: list[str] = field(default_factory=list)
    timeout_seconds: int = 30
    retries: int = 3


@dataclass
class LoggingConfig:
    file: str = "./logs/robot.json.log"
    level: str = "INFO"


@dataclass
class AmldConfig:
    attachment_page_count_default: int = 1
    part_i_co_bs_tt: str = "Không"
    part_i_dien_thoai_doi_tuong: str = ""
    part_i_email_don_vi: str = ""
    part_i_aml_ho_ten: str = ""
    part_i_aml_dt_lam_viec: str = ""
    part_i_aml_dt_di_dong: str = ""
    part_i_aml_chuc_vu: str = ""
    part_i_bo_phan_cong_tac: str = ""
    msg_part_i: str = ""
    msg_part_ii: str = ""
    part_iv_other_crime_code: str = ""
    part_iv_other_crime_placeholder: str = ""
    msg_part_iv: str = ""
    msg_part_v: str = ""
    part_vi_required_document_types: list[str] = field(default_factory=list)
    part_vi_default_document_type: str = ""
    part_vi_time_out_upload: int = 300000
    msg_part_vi: str = ""
    almd_url: str = ""
    almd_url_report_two: str = ""
    username_almd: str = "01311001I.02"
    password_almd: str = "Mb@12345"
    almd_list_user: str = "[]"
    almd_run_mode: str = "LIVE"
    almd_list_extension_file: list[str] = field(default_factory=lambda: ["pdf", "xlsx"])
    almd_login_hang_timeout_ms: int = 300000

@dataclass
class AccuityConfig:
    base_url: str = "http://localhost:5005"
    username: str = "admin"
    password: str = "admin"

@dataclass
class Config:
    source_root: str = "/Users/hainguyen/Projects/RPA/AMLD"
    output_root: str = "./output"
    kafka: KafkaConfig = field(default_factory=KafkaConfig)
    ecm: EcmConfig = field(default_factory=EcmConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    amld: AmldConfig = field(default_factory=AmldConfig)
    accuity: AccuityConfig = field(default_factory=AccuityConfig)


class ConfigError(Exception):
    """Lỗi khi đọc/định dạng cấu hình."""


DEFAULT_CONFIG_PATH = os.path.join("data", "config.yaml")


def load_config(path: str = DEFAULT_CONFIG_PATH) -> Config:
    """Đọc cấu hình từ YAML. Raise ConfigError nếu file thiếu hoặc sai định dạng."""
    if not os.path.isfile(path):
        raise ConfigError(
            f"Không tìm thấy file cấu hình: {path}. "
            f"Hãy copy data/config.example.yaml sang {path} và điền giá trị."
        )
    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw: dict[str, Any] = yaml.safe_load(fh) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"config.yaml sai định dạng YAML: {exc}") from exc

    return _from_dict(raw)


def _from_dict(raw: dict[str, Any]) -> Config:
    kafka_raw = raw.get("kafka", {}) or {}
    ecm_raw = raw.get("ecm", {}) or {}
    log_raw = raw.get("logging", {}) or {}
    accuity_raw = raw.get("accuity", {}) or {}

    amld_raw = raw.get("amld", {}) or {}

    amld_defaults = AmldConfig()
    accuity_defaults = AccuityConfig()
    cfg = Config(
        source_root=raw.get("source_root", Config.source_root),
        output_root=raw.get("output_root", Config.output_root),
        kafka=KafkaConfig(
            bootstrap_servers=kafka_raw.get("bootstrap_servers", KafkaConfig.bootstrap_servers),
            topic=kafka_raw.get("topic", KafkaConfig.topic),
            group_id=kafka_raw.get("group_id", KafkaConfig.group_id),
            security_protocol=kafka_raw.get("security_protocol", KafkaConfig.security_protocol),
            sasl_mechanism=kafka_raw.get("sasl_mechanism", KafkaConfig.sasl_mechanism),
            sasl_plain_username=kafka_raw.get("sasl_plain_username", KafkaConfig.sasl_plain_username),
            sasl_plain_password=kafka_raw.get("sasl_plain_password", KafkaConfig.sasl_plain_password),
        ),
        ecm=EcmConfig(
            base_url=ecm_raw.get("base_url", EcmConfig.base_url),
            token_path=ecm_raw.get("token_path", EcmConfig.token_path),
            client_id=ecm_raw.get("client_id", ""),
            client_secret=ecm_raw.get("client_secret", ""),
            business_codes=list(ecm_raw.get("business_codes", []) or []),
            timeout_seconds=int(ecm_raw.get("timeout_seconds", EcmConfig.timeout_seconds)),
            retries=int(ecm_raw.get("retries", EcmConfig.retries)),
        ),
        logging=LoggingConfig(
            file=log_raw.get("file", LoggingConfig.file),
            level=log_raw.get("level", LoggingConfig.level),
        ),
        amld=AmldConfig(
            attachment_page_count_default=int(amld_raw.get("attachment_page_count_default", amld_defaults.attachment_page_count_default)),
            part_i_co_bs_tt=amld_raw.get("part_i_co_bs_tt", amld_defaults.part_i_co_bs_tt),
            part_i_dien_thoai_doi_tuong=amld_raw.get("part_i_dien_thoai_doi_tuong", amld_defaults.part_i_dien_thoai_doi_tuong),
            part_i_email_don_vi=amld_raw.get("part_i_email_don_vi", amld_defaults.part_i_email_don_vi),
            part_i_aml_ho_ten=amld_raw.get("part_i_aml_ho_ten", amld_defaults.part_i_aml_ho_ten),
            part_i_aml_dt_lam_viec=amld_raw.get("part_i_aml_dt_lam_viec", amld_defaults.part_i_aml_dt_lam_viec),
            part_i_aml_dt_di_dong=amld_raw.get("part_i_aml_dt_di_dong", amld_defaults.part_i_aml_dt_di_dong),
            part_i_aml_chuc_vu=amld_raw.get("part_i_aml_chuc_vu", amld_defaults.part_i_aml_chuc_vu),
            part_i_bo_phan_cong_tac=amld_raw.get("part_i_bo_phan_cong_tac", amld_defaults.part_i_bo_phan_cong_tac),
            msg_part_i=amld_raw.get("msg_part_i", amld_defaults.msg_part_i),
            msg_part_ii=amld_raw.get("msg_part_ii", amld_defaults.msg_part_ii),
            part_iv_other_crime_code=amld_raw.get("part_iv_other_crime_code", amld_defaults.part_iv_other_crime_code),
            part_iv_other_crime_placeholder=amld_raw.get("part_iv_other_crime_placeholder", amld_defaults.part_iv_other_crime_placeholder),
            msg_part_iv=amld_raw.get("msg_part_iv", amld_defaults.msg_part_iv),
            msg_part_v=amld_raw.get("msg_part_v", amld_defaults.msg_part_v),
            part_vi_required_document_types=amld_raw.get("part_vi_required_document_types", amld_defaults.part_vi_required_document_types),
            part_vi_default_document_type=amld_raw.get("part_vi_default_document_type", amld_defaults.part_vi_default_document_type),
            part_vi_time_out_upload=int(amld_raw.get("part_vi_time_out_upload", amld_defaults.part_vi_time_out_upload)),
            msg_part_vi=amld_raw.get("msg_part_vi", amld_defaults.msg_part_vi),
            almd_url=amld_raw.get("almd_url", amld_defaults.almd_url),
            almd_url_report_two=amld_raw.get("almd_url_report_two", amld_defaults.almd_url_report_two),
            username_almd=amld_raw.get("username_almd", amld_defaults.username_almd),
            password_almd=amld_raw.get("password_almd", amld_defaults.password_almd),
            almd_list_user=amld_raw.get("almd_list_user", amld_defaults.almd_list_user),
            almd_run_mode=amld_raw.get("almd_run_mode", amld_defaults.almd_run_mode),
            almd_list_extension_file=amld_raw.get("almd_list_extension_file", amld_defaults.almd_list_extension_file),
            almd_login_hang_timeout_ms=int(amld_raw.get("almd_login_hang_timeout_ms", amld_defaults.almd_login_hang_timeout_ms)),
        ),
        accuity=AccuityConfig(
            base_url=accuity_raw.get("base_url", accuity_defaults.base_url),
            username=accuity_raw.get("username", accuity_defaults.username),
            password=accuity_raw.get("password", accuity_defaults.password),
        ),
    )
    return cfg
