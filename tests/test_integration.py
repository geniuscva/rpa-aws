import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal

from robot.config import Config
from robot.logging_setup import StructuredLogger
from robot.models import StrRecord, CustomerType
from robot.pipeline import StageContext, run_pipeline

# Import stages
from robot.u1_consume.consume_stage import ConsumeDataStage
from robot.u1_consume.cashflow import CashFlowSide
from robot.u2_accuity.accuity_stage import AccuityStage
from robot.u3_tracuuthue.tax_stage import TaxAuthorityStage
from robot.u4_amld.amld_stage import AmldStage
from robot.u5_tonghop.tonghop_stage import TongHopStage
from robot.u5_tonghop.email_sender import SendResult

@pytest.fixture
def mock_context():
    cfg = Config()
    logger = StructuredLogger(cfg.logging.file)
    return StageContext(config=cfg, logger=logger)

@pytest.fixture
def base_record():
    return StrRecord(cif="123456")

def test_tc01_happy_path_success(mock_context, base_record):
    # Given
    mock_ecm_adapter = MagicMock()
    # fetch_dossier trả tuple (danh sách path PDF, mã số thuế trích xuất)
    mock_ecm_adapter.fetch_dossier.return_value = (["/tmp/pdf1.pdf"], "")
    ecm_factory = lambda cif, out: mock_ecm_adapter
    
    mock_resolver = MagicMock()
    mock_resolver.resolve.return_value = "/tmp/cif"
    mock_resolver.missing_required_files.return_value = []
    
    u1 = ConsumeDataStage(ecm_factory, resolver=mock_resolver)
    
    with patch("robot.u1_consume.consume_stage.CustomerClassifier") as MockClassifier, \
         patch("robot.u1_consume.consume_stage.ExcelReader") as MockReader, \
         patch("robot.u1_consume.consume_stage.CashFlowCalculator") as MockCalc, \
         patch("robot.u1_consume.consume_stage.CashFlowPdfRenderer") as MockRenderer, \
         patch("robot.u5_tonghop.tonghop_stage.BatchStatusReport") as MockReport:
         
        MockClassifier.classify.return_value = CustomerType.KHCN
        
        mock_reader_inst = MockReader.return_value
        mock_reader_inst.read_input_str.return_value = [{"STR_TEN_KH": "Nguyen Van A", "EMAIL_NGUOI_LAP_BAO_CAO": "nguyendinhhai1996@hotmail.com"}]
        mock_reader_inst.read_statement.return_value = []
        
        MockCalc.compute.return_value = (CashFlowSide(1, 1, Decimal("100")), CashFlowSide(1, 1, Decimal("200")))
        
        # Mocks for U2, U3, U4
        u2 = AccuityStage(port_factory=lambda ctx: MagicMock())
        u3 = TaxAuthorityStage(port_factory=lambda ctx: MagicMock())
        
        mock_retry = MagicMock()
        mock_retry.run.return_value = "trasoat_123"
        u4 = AmldStage(port_factory=lambda ctx: MagicMock(), retry_policy=mock_retry, attachment_uploader=MagicMock())
        
        # Mocks for U5
        mock_email_port = MagicMock()
        mock_email_port.send.return_value = SendResult(ok=True)
        email_factory = lambda ctx: mock_email_port
        u5 = TongHopStage(email_port_factory=email_factory, status_report=MockReport.return_value)
        
        # When
        stages = [u1, u2, u3, u4]
        final_record = run_pipeline(base_record, mock_context, stages)
        batch_result = u5.process_batch([final_record], mock_context)
        
        # Then
        assert final_record.processing_stopped is False
        assert final_record.ten_khach_hang == "Nguyen Van A"
        assert final_record.email_nguoi_lap_bao_cao == "nguyendinhhai1996@hotmail.com"
        
        # Assert Email is sent with success
        assert mock_email_port.send.called
        assert batch_result.success_count == 1
        assert batch_result.fail_count == 0

def test_tc02_exception_missing_data(mock_context, base_record):
    # Given
    mock_ecm_adapter = MagicMock()
    ecm_factory = lambda cif, out: mock_ecm_adapter
    
    mock_resolver = MagicMock()
    mock_resolver.resolve.return_value = "/tmp/cif"
    mock_resolver.missing_required_files.return_value = ["file1.xlsx"]
    
    u1 = ConsumeDataStage(ecm_factory, resolver=mock_resolver)
    
    with patch("robot.u1_consume.consume_stage.CustomerClassifier") as MockClassifier, \
         patch("robot.u5_tonghop.tonghop_stage.BatchStatusReport") as MockReport:
         
        MockClassifier.classify.return_value = CustomerType.KHCN
        
        u2 = AccuityStage(port_factory=lambda ctx: MagicMock())
        u2.process = MagicMock(return_value=base_record)
        
        u3 = TaxAuthorityStage(port_factory=lambda ctx: MagicMock())
        u4 = AmldStage(port_factory=lambda ctx: MagicMock(), retry_policy=MagicMock())
        
        mock_email_port = MagicMock()
        mock_email_port.send.return_value = SendResult(ok=True)
        email_factory = lambda ctx: mock_email_port
        u5 = TongHopStage(email_port_factory=email_factory, status_report=MockReport.return_value)
        
        # When
        stages = [u1, u2, u3, u4]
        final_record = run_pipeline(base_record, mock_context, stages)
        batch_result = u5.process_batch([final_record], mock_context)
        
        # Then
        assert final_record.processing_stopped is True
        assert "Thieu file bat buoc" in final_record.bot_ghichu
        
        # U2 should not be called
        u2.process.assert_not_called()
        
        assert mock_email_port.send.called
        assert batch_result.success_count == 0
        assert batch_result.fail_count == 1
