import openpyxl

def dump_formulas(file_path, sheet_name, max_row=100, max_col=15):
    wb = openpyxl.load_workbook(file_path, data_only=False)
    sheet = wb[sheet_name]
    
    for row in range(1, max_row + 1):
        row_data = []
        for col in range(1, max_col + 1):
            cell = sheet.cell(row=row, column=col)
            value = cell.value
            if value is not None:
                row_data.append(f"[{cell.coordinate}]: {value}")
        if row_data:
            print(" | ".join(row_data))

if __name__ == "__main__":
    dump_formulas('20181107 ISO16358-1_AMD1 Calculation_tool_FINAL (1).xlsm', 'Variable Capacity unit')
