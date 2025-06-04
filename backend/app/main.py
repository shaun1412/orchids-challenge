from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional
import os
from dotenv import load_dotenv
from .services.scraper import WebsiteScraper
from .services.llm_cloner import LLMCloner
import traceback # Import traceback module

# Load environment variables
load_dotenv()

app = FastAPI(title="Website Cloning API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CloneRequest(BaseModel):
    url: HttpUrl
    options: Optional[dict] = None

class CloneResponse(BaseModel):
    html: str
    message: str

@app.post("/api/clone", response_model=CloneResponse)
async def clone_website(request: CloneRequest):
    try:
        # Initialize services
        scraper = WebsiteScraper()
        cloner = LLMCloner()
        
        # Use async context manager for scraper
        async with scraper as s:
            # Scrape the website
            design_context = await s.scrape(str(request.url))
        
        # Generate cloned HTML using LLM
        cloned_html = await cloner.generate_html(design_context)
        
        return CloneResponse(
            html=cloned_html,
            message="Website cloned successfully"
        )
    except Exception as e:
        # Print the detailed exception and traceback
        print(f"Error during cloning: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e)) # Re-raise the exception to return 500 to frontend

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
