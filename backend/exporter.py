import pandas as pd
from typing import List, Dict
import io

def generate_excel(data: Dict) -> io.BytesIO:
    """Generates an Excel file from extracted financial data with formatting."""
    items = data.get('items', [])
    if not items:
        return io.BytesIO()

    # Get all years dynamically
    years = sorted(list(items[0]['values'].keys()), reverse=True)
    
    # Build dataframe rows
    rows = []
    for item in items:
        row = {"Particulars": item['particulars']}
        for year in years:
            val = item['values'].get(year)
            row[year] = val if val is not None else ""
        rows.append(row)
        
    df = pd.DataFrame(rows)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Financials')
        
        # Add basic formatting
        workbook = writer.book
        worksheet = writer.sheets['Financials']
        
        # Adjust column widths
        for i, col in enumerate(df.columns):
            worksheet.column_dimensions[chr(65 + i)].width = 25 if i == 0 else 15
            
    output.seek(0)
    return output
