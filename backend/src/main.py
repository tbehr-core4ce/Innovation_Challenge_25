"""
/services/service_name/src/main.py
FastAPI application for document processing with Azure Blob Storage
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import uuid
import os
from settings import settings
from azure_storage import get_storage_client
from models.workflow import JobSubmission
from models.microsoft import UploadSasResponse, DownloadSasResponse


app = FastAPI(title="Document Processor API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# In backend_api.py, add:
# Connect parser to the FastAPI backend
@app.post("/api/ingest-csv")
async def ingest_csv_data(file: UploadFile):
    """
    Upload and ingest CSV file of H5N1 cases
    """
    # Save uploaded file
    contents = await file.read()
    with open(f"/tmp/{file.filename}", "wb") as f:
        f.write(contents)
    
    # Parse CSV
    cases = parse_h5n1_csv(f"/tmp/{file.filename}")
    
    # Validate
    validator = DataValidator()
    valid_cases = [c for c in cases if validator.validate_case(c)]
    
    # Store in database (or update mock_cases for now)
    mock_cases.extend(valid_cases)
    
    return {
        "message": f"Ingested {len(valid_cases)} cases",
        "validation_report": validator.get_report()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)