from pydantic import BaseModel, Field
from typing import Optional

class PlantCareInput(BaseModel):
    plant_name: str = Field(..., min_length=1, description="The user-provided plant name (e.g., tomato, Fiddle Leaf Fig).")
    user_zone: str = Field(..., pattern=r"^\d{1,2}[ab]?$", description="The user's USDA Hardiness Zone (e.g., 7a, 8b, 5).")


class PlantIdentificationResponse(BaseModel):
    is_plant: bool = Field(..., description="Whether the uploaded image contains a plant, tree, or shrub.")
    common_name: Optional[str] = Field(None, description="The common name of the plant if identified, null if not a plant.")
    confidence: Optional[str] = Field(None, description="Confidence level of the identification (high, medium, low).")
    message: str = Field(..., description="Human-readable message about the identification result.") 