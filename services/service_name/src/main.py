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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)