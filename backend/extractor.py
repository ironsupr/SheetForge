from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class FinancialLineItem(BaseModel):
    particulars: str = Field(..., description="The name of the line item (e.g., 'Revenue from operations')")
    values: Dict[str, Optional[float]] = Field(..., description="Key-value pairs of Year: Value (e.g., {'FY 25': 204813.0})")
    confidence: float = Field(..., description="AI confidence score for this specific line item (0.0 to 1.0)")
    notes: Optional[str] = Field(None, description="Any additional context or notes about this item")

class IncomeStatement(BaseModel):
    items: List[FinancialLineItem] = Field(..., description="List of financial line items extracted from the statement")
    currency: str = Field(..., description="The currency of the financial data (e.g., 'INR', 'USD')")
    units: str = Field(..., description="The units used (e.g., 'Millions', 'Crores', 'Absolute')")

def extract_financial_data(text: str) -> IncomeStatement:
    """Uses LLM to extract structured financial data from raw text."""
    print("DEBUG: Calling real LLM extract_financial_data")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY not found. Please set it in .env file.")
        # Fallback to a placeholder or raise an error
        raise ValueError("OPENAI_API_KEY is missing. Please add it to your .env file in the backend directory.")

    prompt = f"""
    You are an expert financial analyst. Extract the Income Statement data from the provided text.
    
    Guidelines:
    1. Identify all revenue, expense, and profitability line items.
    2. Extract values for multiple years if present (e.g., FY 2024, FY 2023).
    3. Normalize year labels to a standard format like 'FY 24', 'FY 23'.
    4. Detect the currency (e.g., INR, USD) and units (e.g., Millions, Crores).
    5. Provide a confidence score for each item based on the clarity of the source text.
    6. If a value is missing for a particular year, use null.
    
    Raw Text:
    {text}
    """

    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini", # Using a fast and capable model for extraction
            messages=[
                {"role": "system", "content": "You extract structured financial data from text using provided schemas."},
                {"role": "user", "content": prompt}
            ],
            response_format=IncomeStatement,
        )
        
        return response.choices[0].message.parsed
    except Exception as e:
        print(f"ERROR during LLM extraction: {e}")
        # In case of failure, we might want to return an empty statement or re-raise
        raise e
