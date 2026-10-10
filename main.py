import os
import sys

from robot.config import load_config, ConfigError
from robot.logging_setup import StructuredLogger
from robot.models import StrRecord
from robot.pipeline import StageContext

from robot.u1_consume.consume_stage import ConsumeDataStage
from robot.u1_consume.ecm_client import EcmClientAdapter, HttpxEcmTransport
from robot.u2_accuity.accuity_stage import AccuityStage
from robot.u2_accuity.accuity_adapter import PlaywrightAccuityPort
from robot.u3_tracuuthue.tax_stage import TaxAuthorityStage
from robot.u3_tracuuthue.tax_authority_adapter import PlaywrightTaxAuthorityPort
from robot.u4_amld.amld_stage import AmldStage
from robot.u4_amld.amld_portal_adapter import PlaywrightAmldPortalPort
from robot.u5_tonghop.tonghop_stage import TongHopStage
from robot.u5_tonghop.email_sender import SmtpEmailPort, MockEmailPort
from robot.u1_consume.kafka_consumer import KafkaConsumerAdapter, RealKafkaMessageSource

def main():
    try:
        config = load_config()
    except ConfigError as exc:
        print(f"Lỗi cấu hình: {exc}")
        sys.exit(1)

    logger = StructuredLogger(file_path=config.logging.file, level=config.logging.level)
    context = StageContext(config=config, logger=logger)
    logger.info("Bắt đầu tiến trình xử lý RPA")

    # Đọc input từ Kafka thật
    source = RealKafkaMessageSource(config.kafka)
    adapter = KafkaConsumerAdapter(config.kafka, logger, source)
    
    cifs = []
    for event in adapter.events():
        if event.cif not in cifs:
            cifs.append(event.cif)

    if not cifs:
        logger.info(f"Không có CIF nào được parse từ Kafka message")
        sys.exit(0)

    stages = [
        ConsumeDataStage(ecm_client_factory=lambda cif, out_dir: EcmClientAdapter(config.ecm, logger, HttpxEcmTransport(), out_dir)),
        AccuityStage(port_factory=lambda ctx: PlaywrightAccuityPort(ctx.config, ctx.logger)),
        TaxAuthorityStage(port_factory=lambda ctx: PlaywrightTaxAuthorityPort(ctx.config, ctx.logger)),
        AmldStage(port_factory=lambda ctx: PlaywrightAmldPortalPort(ctx.config, ctx.logger))
    ]

    processed_records = []
    for cif in cifs:
        logger.info(f"Đang xử lý CIF: {cif}")
        record = StrRecord(cif=cif)
        
        # Chạy tuần tự qua các stage (U1 -> U4)
        for stage in stages:
            stage_name = stage.__class__.__name__
            logger.info(f"Bắt đầu chạy {stage_name} cho CIF {cif}")
            if record.processing_stopped:
                logger.info(f"Dừng xử lý CIF {cif} trước {stage_name} vì processing_stopped=True")
                break
            try:
                record = stage.process(record, context)
                logger.info(f"Hoàn thành {stage_name} cho CIF {cif}", processing_stopped=record.processing_stopped)
            except Exception as e:
                logger.error(f"Lỗi khi chạy {stage_name} cho CIF {cif}", error=str(e), exc_info=True)
                break
            
        processed_records.append(record)

    logger.info("Chạy cấu phần U5 - Tổng hợp trạng thái và gửi mail")
    # Sử dụng SmtpEmailPort nếu có config mail, ngược lại dùng MockEmailPort
    if hasattr(config, "mail") and config.mail:
        email_port = SmtpEmailPort(config.mail)
    else:
        email_port = MockEmailPort()
        
    u5_stage = TongHopStage(email_port_factory=lambda ctx: email_port)
    batch_result = u5_stage.process_batch(processed_records, context)

    logger.info(
        "Hoàn tất toàn bộ tiến trình",
        success=batch_result.success_count,
        fail=batch_result.fail_count,
        sent_email=batch_result.sent
    )

if __name__ == "__main__":
    main()
