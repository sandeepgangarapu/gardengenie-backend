from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal, Union

class PlantCareInput(BaseModel):
    plant_name: str = Field(..., min_length=1, description="The user-provided plant name (e.g., tomato, Fiddle Leaf Fig).")
    user_zone: str = Field(..., pattern=r"^\d{1,2}[ab]?$", description="The user's USDA Hardiness Zone (e.g., 7a, 8b, 5).")
    persist: bool = Field(default=True, description="Whether to upsert the generated care into Supabase. Defaults to True.")


class PlantIdentificationResponse(BaseModel):
    is_plant: bool = Field(..., description="Whether the uploaded image contains a plant, tree, or shrub.")
    common_name: Optional[str] = Field(None, description="The common name of the plant if identified, null if not a plant.")
    confidence: Optional[str] = Field(None, description="Confidence level of the identification (high, medium, low).")
    message: str = Field(..., description="Human-readable message about the identification result.") 


# --- Plant Care Structured Response Models ---

class CarePlanItem(BaseModel):
    text: str
    when: Optional[str] = None
    priority: Optional[Literal["must do", "good to do", "optional"]] = None


class CarePlanTab(BaseModel):
    key: Optional[str] = None
    label: Optional[str] = None
    items: List[CarePlanItem] = Field(default_factory=list)


class CarePlan(BaseModel):
    style: Optional[Literal["seasons", "indoor", "lifecycle"]] = None
    tabs: List[CarePlanTab] = Field(default_factory=list)


class LegacyCareStep(BaseModel):
    step: str
    months: Optional[str] = None
    priority: Optional[Literal["must do", "good to do", "optional"]] = None
    timing: Optional[str] = None


class PlantCareResponse(BaseModel):
    # Core
    plantName: str
    description: Optional[str] = None
    type: Optional[str] = None
    sun: Optional[str] = None
    zoneSuitability: Optional[str] = None
    seasonality: Optional[str] = None

    # LLM-structured fields
    requirements: Optional[Dict[str, Any]] = None
    typeSpecific: Optional[Dict[str, Any]] = None
    seed_starting: Optional[Union[Dict[str, Any], List[Any]]] = None
    planting: Optional[Union[Dict[str, Any], List[Any]]] = None
    care_plan: Optional[CarePlan] = None

    # Legacy fallback care structure
    care: Optional[Dict[str, List[LegacyCareStep]]] = None

    # Optional extras that may appear from prompts
    seedStartingMonth: Optional[str] = None
    plantingMonth: Optional[str] = None
    seedStartingInstructions: Optional[List[Any]] = None
    plantingInstructions: Optional[List[Any]] = None

    class Config:
        extra = "allow"  # tolerate extra keys from LLM output