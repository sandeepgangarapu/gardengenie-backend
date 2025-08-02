import os
import logging
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from .config import APP_TITLE, APP_DESCRIPTION, APP_VERSION, CORS_ORIGINS
from .models import PlantCareInput, PlantIdentificationResponse
from .services.plant_care.plant_care import generate_plant_care_instructions
from .services.plant_identification.plant_identification import identify_plant_from_uploaded_image, validate_image_data
from .database.supabase_client import health_check, get_supabase_client

logger = logging.getLogger(__name__)

# --- FastAPI Application Setup ---
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---

@app.post("/plant-care-instructions", response_model=dict)
async def get_plant_care_instructions(payload: PlantCareInput, request: Request):
    """
    Receives a plant name and USDA zone, classifies the plant care category,
    generates appropriate care instructions using an LLM, stores the result
    in Supabase, and returns the care instructions as a JSON object.
    """
    supabase_client = get_supabase_client()
    if supabase_client is None:
        raise HTTPException(status_code=503, detail="Database client is not initialized. Cannot process request.")

    plant_name = payload.plant_name
    user_zone = payload.user_zone
    logger.info(f"Received request for plant care: '{plant_name}' in zone '{user_zone}'")

    # Generate plant care instructions using the service
    care_info = generate_plant_care_instructions(plant_name, user_zone)
    
    if care_info is None:
        raise HTTPException(status_code=503, detail="Error generating plant care instructions.")

    logger.info(f"Successfully generated care instructions for '{plant_name}'")
    return care_info

@app.post("/identify-plant", response_model=PlantIdentificationResponse)
async def identify_plant(file: UploadFile = File(...)):
    """
    Accepts an uploaded image and uses AI vision to determine if it contains a plant
    and identify its common name if it is a plant.
    """
    logger.info(f"Received plant identification request for file: {file.filename}")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400, 
            detail="File must be an image (JPEG, PNG, etc.)"
        )
    
    # Read and validate the file
    try:
        image_data = await file.read()
        validation_result = validate_image_data(image_data)
        
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400,
                detail=validation_result["error"]
            )
            
    except Exception as e:
        logger.error(f"Error reading uploaded file: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error reading uploaded image file."
        )
    
    # Analyze the image
    identification_result = identify_plant_from_uploaded_image(image_data)
    
    if identification_result is None:
        raise HTTPException(
            status_code=503,
            detail="Error analyzing the image. Please try again."
        )
    
    # Create response object
    response = PlantIdentificationResponse(
        is_plant=identification_result.get('is_plant', False),
        common_name=identification_result.get('common_name'),
        confidence=identification_result.get('confidence'),
        message=identification_result.get('message', 'Analysis completed.')
    )
    
    logger.info(f"Plant identification completed: {response.is_plant}, {response.common_name}")
    return response

@app.get("/health", status_code=200)
async def health_check_endpoint():
    """Simple health check endpoint. Checks Supabase connection."""
    return health_check()

# --- Local Development Runner ---
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server for local development...")
    # Render provides the PORT env var; default to 8000 locally if not set
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 