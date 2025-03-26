import os
import asyncio
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import logging

from agents.editor_agent import EditorAgent
from agents.illustrator_agent import IllustratorAgent
from agents.story_processor import StoryProcessor

# Load environment variables from .env
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Kids Book Web App")

# Set up logging
logger = logging.getLogger("kidsbook")
logging.basicConfig(level=logging.DEBUG)

# Mount static files (assuming your static assets are in webapp/static)
app.mount("/static", StaticFiles(directory="webapp/static"), name="static")

# Configure Jinja2 templates (assuming templates are in webapp/templates)
templates = Jinja2Templates(directory="webapp/templates")

# Home page endpoint - renders the index template
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Endpoint to process the creation of the kids book
@app.post("/create_kids_book/")
async def create_kids_book(request: Request, story: str = Form(...)):
    """Async endpoint to create a kids book."""
    if not story:
        logger.warning("No story provided in request")
        raise HTTPException(status_code=400, detail="No story provided")

    # Initialize agents
    editor = EditorAgent()
    illustrator = IllustratorAgent()
    story_processor = StoryProcessor()

    try:
        async with asyncio.timeout(300):  # 5 minute timeout
            # Process with editor
            editor_result = await editor.edit_story(story)
            if not editor_result:
                raise HTTPException(status_code=500, detail="Story editing failed")

            final_story = editor_result.get("final_story")
            illustrator_prompt = editor_result.get("illustrator_prompt")

            # Generate cover image
            cover_image_url = await illustrator.generate_cover_image(final_story)
            if not cover_image_url:
                raise HTTPException(status_code=500, detail="Cover image generation failed")

            # Create composite HTML
            html_content = await asyncio.to_thread(
                story_processor.process,
                final_story=final_story,
                cover_image_url=cover_image_url,
                illustrator_prompt=illustrator_prompt
            )

            # Return both HTML and JSON data
            return JSONResponse(content={
                "status": "success",
                "html_content": html_content,
                "cover_image_url": cover_image_url,
                "final_story": final_story
            })

    except asyncio.TimeoutError:
        logger.error("Operation timed out")
        raise HTTPException(status_code=504, detail="Operation timed out")
    except Exception as e:
        logger.exception(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))