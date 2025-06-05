from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import traceback

from app.services.scraper import AdvancedWebsiteScraper, ScrapingConfig
from app.services.llm_cloner import (
    HighPrecisionLLMCloner,
    PrecisionCloneConfig,
    CloneAccuracy
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Website Cloning API")

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class CloneRequest(BaseModel):
    url: HttpUrl
    scrape_options: Optional[Dict[str, Any]] = None
    clone_options: Optional[Dict[str, Any]] = None

class CloneResponse(BaseModel):
    html: str
    message: str

@app.post("/api/clone", response_model=CloneResponse)
async def clone_website(request: CloneRequest):
    try:
        # Build config from request or use default
        scrape_config = ScrapingConfig(**request.scrape_options) if request.scrape_options else ScrapingConfig()
        clone_config = PrecisionCloneConfig(**request.clone_options) if request.clone_options else PrecisionCloneConfig()

        # Initialize scraper + cloner
        scraper = AdvancedWebsiteScraper(scrape_config)
        cloner = HighPrecisionLLMCloner(clone_config)

        # Scrape the design context (sync)
        design_context = scraper.scrape_comprehensive(str(request.url))

        # Generate HTML (async)
        html = await cloner.generate_pixel_perfect_html(design_context)

        # Log the generated HTML for debugging
        print("--- Generated HTML ---")
        print(html)
        print("----------------------")

        return CloneResponse(
            html=html,
            message="Website cloned successfully."
        )

    except Exception as e:
        print(f"❌ Clone error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error during website cloning.")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
