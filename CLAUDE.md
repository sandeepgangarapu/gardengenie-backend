# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Local development (recommended)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Install dependencies
pip install -r requirements.txt
```

### Docker Deployment
```bash
# Build Docker image
docker build -t plant-care-api .

# Run container (PORT env var optional; defaults to 8080 inside container)
docker run -p 8000:8080 -e PORT=8080 plant-care-api
```

## Architecture Overview

This is a FastAPI-based Plant Care API that provides AI-powered plant identification and care instructions. The application is designed for deployment on Render.

### Core Components

**Main Application Structure:**
- `app/main.py` - FastAPI application with endpoints and local dev run guard
- `app/config.py` - Configuration management with environment variables

**Key Services:**
- `app/services/plant_care_service.py` - Orchestrates the complete plant care workflow
- `app/services/plant_classifier.py` - Classifies plants into care categories (houseplants, edible annuals, etc.)
- `app/services/llm_service.py` - Contains specialized LLM prompt functions for different plant types
- `app/services/plant_identifier.py` - AI vision service for plant identification from images
- `app/services/image_service.py` - Unsplash integration for plant images

**Database Layer:**
- `app/database/supabase_client.py` - Supabase integration with comprehensive validation and storage logic
- Uses Supabase tables: `plants`, `care_instructions`, `plant_images`

### API Endpoints

1. `POST /plant-care-instructions` - Generate care instructions for a plant name and USDA zone
2. `POST /identify-plant` - Upload image for AI plant identification
3. `GET /health` - Health check with database connectivity status

### Data Flow

1. **Plant Care Instructions:**
   - Plant name → Classification → Specialized LLM prompt → Care instructions → Database storage
   - Different LLM functions handle different plant categories (houseplants, edible annuals, fruit trees, etc.)

2. **Plant Identification:**
   - Image upload → Validation → AI vision analysis → Plant identification response

### Environment Variables Required

```bash
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENROUTER_API_KEY=your_openrouter_key
UNSPLASH_ACCESS_KEY=your_unsplash_key  # Optional for image fetching
```

### Key Models

- `PlantCareInput` - Input validation for plant name and USDA zone
- `PlantIdentificationResponse` - Structured response for plant identification

### Database Schema Context

The application stores structured care instructions with validation, supporting different plant categories with specialized care guidance. Care instructions are organized by care phases with priority levels and timing information.