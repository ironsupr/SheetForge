from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import List
import os
import shutil
import processor
import extractor
import exporter
from database import create_db_and_tables, engine, get_session
from models import ExtractionRecord
from sqlmodel import Session, select

app = FastAPI(title="SheetForge API")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Welcome to SheetForge API"}

@app.post("/process")
async def process_document(file: UploadFile = File(...), session: Session = Depends(get_session)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Create a temporary file to store the upload
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # 1. Extract text
        text = processor.extract_text_from_pdf(temp_path)
        
        # 2. Extract financial data (LLM Mock)
        data = extractor.extract_financial_data(text)
        
        # 3. Save to database
        record = ExtractionRecord.from_data(file.filename, data.dict())
        session.add(record)
        session.commit()
        session.refresh(record)
        
        return {**data.dict(), "id": record.id}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/extractions", response_model=List[ExtractionRecord])
async def get_extractions(session: Session = Depends(get_session)):
    statement = select(ExtractionRecord).order_by(ExtractionRecord.timestamp.desc())
    results = session.exec(statement).all()
    return results

@app.get("/extractions/{id}", response_model=ExtractionRecord)
async def get_extraction(id: int, session: Session = Depends(get_session)):
    record = session.get(ExtractionRecord, id)
    if not record:
        raise HTTPException(status_code=404, detail="Extraction not found")
    return record

@app.post("/export")
async def export_data(data: dict):
    excel_file = exporter.generate_excel(data)
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=financial_data.xlsx"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
