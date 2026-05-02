import openpyxl

def dump_bin_logic(file_path, sheet_name):
    wb = openpyxl.load_workbook(file_path, data_only=False)
    sheet = wb[sheet_name]
    
    # Range CJ7 to CZ49
    cols = ['CJ', 'CK', 'CL', 'CM', 'CN', 'CO', 'CP', 'CQ', 'CR', 'CS', 'CT', 'CU', 'CV', 'CW', 'CX', 'CY', 'CZ']
    for row in range(5, 51):
        row_data = []
        for col_name in cols:
            cell = sheet[f"{col_name}{row}"]
            row_data.append(f"[{col_name}{row}]: {cell.value}")
        print(" | ".join(row_data))

if __name__ == "__main__":
    dump_bin_logic('20181107 ISO16358-1_AMD1 Calculation_tool_FINAL (1).xlsm', 'Variable Capacity unit')
