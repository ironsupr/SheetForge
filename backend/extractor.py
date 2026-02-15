from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import os
import json
# from openai import OpenAI # Future implementation

class FinancialLineItem(BaseModel):
    particulars: str
    values: Dict[str, Optional[float]]  # Year: Value
    confidence: float
    notes: Optional[str] = None

class IncomeStatement(BaseModel):
    items: List[FinancialLineItem]
    currency: str
    units: str

def extract_financial_data(text: str) -> IncomeStatement:
    """Uses LLM to extract structured financial data from raw text."""
    print("DEBUG: Calling extract_financial_data")
    
    # Updated mock data based on the full sample CSV provided - Massive Granular Detail
    items = [
        # Revenue Section
        FinancialLineItem(particulars="Revenue from ops", values={"FY 25": 204813.0, "FY 24": 163210.0, "FY 23": 133905.0, "FY 22": 89582.0, "FY 21": 65557.0, "FY 20": 72484.0}, confidence=0.99),
        FinancialLineItem(particulars="Other sources", values={"FY 25": 1212.0, "FY 24": 793.6, "FY 23": 388.49, "FY 22": 679.0, "FY 21": 369.0, "FY 20": 425.2}, confidence=0.98),
        FinancialLineItem(particulars="Total Revenue", values={"FY 25": 206025.0, "FY 24": 164003.6, "FY 23": 134293.49, "FY 22": 90262.0, "FY 21": 65927.0, "FY 20": 72909.0}, confidence=0.99),
        
        # Materials Consumed
        FinancialLineItem(particulars="Inventories at beginning of year", values={"FY 25": 9756.31, "FY 24": 9613.51, "FY 23": 8070.05, "FY 22": 3965.62, "FY 21": 3925.27, "FY 20": 2595.55}, confidence=0.96),
        FinancialLineItem(particulars="Purchases during the year (net)", values={"FY 25": 87635.34, "FY 24": 72762.19, "FY 23": 72052.48, "FY 22": 46890.27, "FY 21": 28499.0, "FY 20": 32713.89}, confidence=0.95),
        FinancialLineItem(particulars="Less: Sold during the year", values={"FY 25": -1308.84, "FY 24": -2354.78, "FY 23": 6338.1, "FY 22": 3096.71, "FY 21": 1573.56, "FY 20": 2039.19}, confidence=0.92),
        FinancialLineItem(particulars="Less: Inventories at end of the year", values={"FY 25": -13786.1, "FY 24": -9756.31, "FY 23": 9613.51, "FY 22": 8070.05, "FY 21": 3965.62, "FY 20": 3925.27}, confidence=0.93),
        FinancialLineItem(particulars="Cost of materials consumed", values={"FY 25": 82937.43, "FY 24": 70264.61, "FY 23": 64170.92, "FY 22": 39689.13, "FY 21": 26885.09, "FY 20": 29395.56}, confidence=0.95),
        
        # Employee Costs
        FinancialLineItem(particulars="Salaries, wages and bonus", values={"FY 25": 17067.81, "FY 24": 13041.12, "FY 23": 11026.09, "FY 22": 9126.69, "FY 21": 8131.06, "FY 20": 7429.61}, confidence=0.98),
        FinancialLineItem(particulars="Contribution to provident fund", values={"FY 25": 816.67, "FY 24": 679.36, "FY 23": 538.82, "FY 22": 483.82, "FY 21": 445.89, "FY 20": 386.82}, confidence=0.97),
        FinancialLineItem(particulars="Total employee benefits expense", values={"FY 25": 18850.26, "FY 24": 14465.87, "FY 23": 12166.42, "FY 22": 10076.99, "FY 21": 8897.36, "FY 20": 8108.15}, confidence=0.97),
        
        # Other Expenses - Detailed
        FinancialLineItem(particulars="Power and fuel", values={"FY 25": 6295.08, "FY 24": 5502.85, "FY 23": 4792.2, "FY 22": 3299.25, "FY 21": 2670.0, "FY 20": 2790.62}, confidence=0.94),
        FinancialLineItem(particulars="Repairs to plant and equipment", values={"FY 25": 3837.09, "FY 24": 2973.81, "FY 23": 2577.68, "FY 22": 1679.09, "FY 21": 1328.41, "FY 20": 1195.08}, confidence=0.95),
        FinancialLineItem(particulars="Rent", values={"FY 25": 970.54, "FY 24": 801.6, "FY 23": 542.21, "FY 22": 496.86, "FY 21": 510.55, "FY 20": 559.14}, confidence=0.98),
        FinancialLineItem(particulars="Traveling and conveyance", values={"FY 25": 1550.41, "FY 24": 1215.23, "FY 23": 1064.08, "FY 22": 674.93, "FY 21": 511.45, "FY 20": 840.45}, confidence=0.94),
        FinancialLineItem(particulars="Freight, octroi and insurance", values={"FY 25": 14031.34, "FY 24": 11020.58, "FY 23": 9112.67, "FY 22": 6189.91, "FY 21": 4588.28, "FY 20": 4554.66}, confidence=0.96),
        FinancialLineItem(particulars="Distribution expenses", values={"FY 25": 3064.82, "FY 24": 2250.15, "FY 23": 2100.79, "FY 22": 1440.23, "FY 21": 103.38, "FY 20": 116.14}, confidence=0.95),
        
        # Final Profitability
        FinancialLineItem(particulars="EBITDA", values={"FY 25": 48322.81, "FY 24": 36888.55, "FY 23": 28269.05, "FY 22": 17225.93, "FY 21": 12387.67, "FY 20": 14900.34}, confidence=0.96),
        FinancialLineItem(particulars="Finance Costs", values={"FY 25": 4503.86, "FY 24": 2680.99, "FY 23": 1861.22, "FY 22": 1847.0, "FY 21": 2811.04, "FY 20": 3096.42}, confidence=0.94),
        FinancialLineItem(particulars="Depreciation", values={"FY 25": 9473.86, "FY 24": 6809.0, "FY 23": 6171.0, "FY 22": 5312.0, "FY 21": 5287.0, "FY 20": 4886.0}, confidence=0.95),
        FinancialLineItem(particulars="Profit After Tax", values={"FY 25": 26342.27, "FY 24": 21018.3, "FY 23": 15501.77, "FY 22": 7461.93, "FY 21": 3572.63, "FY 20": 4720.25}, confidence=0.98),
    ]
    
    return IncomeStatement(
        items=items,
        currency="INR",
        units="Millions"
    )
