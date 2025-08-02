"""
Main entry point for the Plant Care API application.
"""
import os
import uvicorn
from app.main import app

if __name__ == "__main__":
    # Render provides the PORT env var; default to 8000 locally if not set
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 