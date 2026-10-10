from robot.models import StrRecord
from robot.u1_consume.consume_stage import ConsumeDataStage
from robot.u1_consume.excel_reader import ExcelReader

reader = ExcelReader("/Users/hainguyen/Projects/RPA/202610/20261009/CUS.T24.6670501")
input_rows = reader.read_input_str()
print("input_rows:", input_rows)

record = StrRecord(cif="6670501")
ConsumeDataStage._fill_input_fields(record, input_rows)
