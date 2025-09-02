from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import tempfile
import os
import shutil
import uuid
from pathlib import Path
import asyncio

# Import your existing modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spatial_detector import SimpleSpatialDetector
from ai_agent import SimpleAIAgent

app = FastAPI(title="Vision Detection API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global detector instance
detector = None

def get_detector():
    """Initialize detector lazily"""
    global detector
    if detector is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is required")
        
        agent = SimpleAIAgent(api_key)
        detector = SimpleSpatialDetector(agent)
    return detector

class DetectionResult(BaseModel):
    object: str
    confidence: str
    confidence_score: float
    bbox: List[int]

class ApiResponse(BaseModel):
    ok: bool
    imageUrl: str
    targets: List[str]
    results: List[DetectionResult]
    message: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Vision Detection API is running"}

@app.post("/api/detect", response_model=ApiResponse)
async def detect_objects(file: UploadFile = File(...), targets: str = Form(...)):
    """Detect objects in uploaded image using existing detection logic"""
    
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    target_list = [t.strip() for t in targets.split(",") if t.strip()]
    if not target_list:
        raise HTTPException(status_code=400, detail="At least one target object is required")
    
    # Use temporary files for serverless environment
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Save uploaded file
        file_extension = Path(file.filename or "image.jpg").suffix.lower()
        if file_extension not in [".jpg", ".jpeg", ".png", ".webp"]:
            file_extension = ".jpg"
        
        temp_filename = f"{uuid.uuid4()}{file_extension}"
        temp_path = Path(temp_dir) / temp_filename
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get detector instance
        detector_instance = get_detector()
        
        # Run detection in thread pool
        loop = asyncio.get_event_loop()
        detections = await loop.run_in_executor(None, detector_instance.detect_multiple, str(temp_path), target_list)
        
        # Convert to API format
        api_results = [
            DetectionResult(
                object=d["object"],
                confidence=d["confidence"], 
                confidence_score=d["confidence_score"],
                bbox=[int(x) for x in d["bbox"]]
            ) for d in detections
        ]
        
        # For serverless, we can't persist files, so we'll return base64 or use temp URLs
        # This is a simplified version - you might want to upload to cloud storage
        image_url = f"data:image/{file_extension.lstrip('.')};base64,processed_image"
        
        return ApiResponse(
            ok=True,
            imageUrl=image_url,
            targets=target_list,
            results=api_results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)

# This is the handler that Vercel will call
def handler(request, context):
    return app