from sqlmodel import Session, select, create_engine
from models import ExtractionRecord
import os

db_path = os.path.join(os.getcwd(), 'sheetforge.db')
engine = create_engine(f'sqlite:///{db_path}')

with Session(engine) as session:
    print("Testing session.get(ExtractionRecord, 1)...")
    record = session.get(ExtractionRecord, 1)
    if record:
        print(f"Found Record: ID={record.id}, Filename={record.filename}")
    else:
        print("Record NOT FOUND with session.get")
    
    records = session.exec(select(ExtractionRecord)).all()
    print("\nAll Records:")
    for r in records:
        print(f"ID: {r.id}, Filename: {r.filename}")
