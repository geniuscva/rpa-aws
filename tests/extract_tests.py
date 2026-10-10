import pandas as pd
import json

df = pd.read_excel('/Users/khanhnguyen/Downloads/issues - Copy (2).xlsx')

tests = []
for index, row in df.head(5).iterrows():
    def get_val(col_name):
        val = row.get(col_name)
        if pd.isna(val):
            return ""
        return str(val).strip()

    test_case = {
        'Test_ID': get_val('Mã trường hợp kiểm thử'),
        'Summary': get_val('Kịch bản kiểm thử'),
        'Precondition': get_val('Tiền điều kiện'),
        'Steps': get_val('Các bước thực hiện\n'),
        'Expected_Result': get_val('Kết quả mong muốn')
    }
    
    tests.append(test_case)

with open('extracted_tests.json', 'w', encoding='utf-8') as f:
    json.dump(tests, f, ensure_ascii=False, indent=2)

print("Tests extracted successfully.")
