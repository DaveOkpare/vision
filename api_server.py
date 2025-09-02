from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import os
import shutil
import uuid
from pathlib import Path

from spatial_detector import SimpleSpatialDetector
from ai_agent import SimpleAIAgent

# Global detector instance
detector = None

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Initialize detector on startup"""
    global detector
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is required")
        
        agent = SimpleAIAgent(api_key)
        detector = SimpleSpatialDetector(agent)
        print("✅ Vision detection API initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize detector: {e}")
        raise
    
    yield
    # Cleanup on shutdown if needed

app = FastAPI(title="Vision Detection API", version="1.0.0", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory for storing processed images
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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
    
    # Save uploaded file
    file_extension = Path(file.filename or "image.jpg").suffix.lower()
    if file_extension not in [".jpg", ".jpeg", ".png", ".webp"]:
        file_extension = ".jpg"
    
    temp_filename = f"{uuid.uuid4()}{file_extension}"
    temp_path = UPLOADS_DIR / temp_filename
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Use existing detect_multiple function - handles single and multi-object detection
        # Run in thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        detections = await loop.run_in_executor(None, detector.detect_multiple, str(temp_path), target_list)
        
        # Convert to API format
        api_results = [
            DetectionResult(
                object=d["object"],
                confidence=d["confidence"], 
                confidence_score=d["confidence_score"],
                bbox=[int(x) for x in d["bbox"]]
            ) for d in detections
        ]
        
        # Use combined result image if available, otherwise original
        result_image_path = (detections[0].get("combined_result_image_path") 
                           if detections else None)
        
        if result_image_path and os.path.exists(result_image_path):
            result_filename = f"{uuid.uuid4()}_result{file_extension}"
            result_path = UPLOADS_DIR / result_filename
            shutil.copy2(result_image_path, result_path)
            image_url = f"/uploads/{result_filename}"
            temp_path.unlink()  # Clean up original
        else:
            image_url = f"/uploads/{temp_filename}"
        
        return ApiResponse(
            ok=True,
            imageUrl=image_url,
            targets=target_list,
            results=api_results
        )
        
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)