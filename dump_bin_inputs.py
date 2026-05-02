import openpyxl

def dump_bin_inputs(file_path, sheet_name):
    wb = openpyxl.load_workbook(file_path, data_only=False)
    sheet = wb[sheet_name]
    
    # Range CC18 to CI48
    cols = ['CC', 'CD', 'CE', 'CF', 'CG', 'CH', 'CI']
    for row in range(15, 50):
        row_data = []
        for col_name in cols:
            cell = sheet[f"{col_name}{row}"]
            row_data.append(f"[{col_name}{row}]: {cell.value}")
        print(" | ".join(row_data))

if __name__ == "__main__":
    dump_bin_inputs('20181107 ISO16358-1_AMD1 Calculation_tool_FINAL (1).xlsm', 'Variable Capacity unit')
