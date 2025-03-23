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
    """
    Async endpoint that:
      - Retrieves the story from the submitted form,
      - Initializes the EditorAgent, IllustratorAgent, and StoryProcessor,
      - Processes the story asynchronously (with a 5-minute timeout),
      - Returns a JSON response containing the composite story, final edited story, and illustration.
    """
    if not story:
        logger.warning("No story provided in the request")
        raise HTTPException(status_code=400, detail="No story provided")

    logger.info("Initializing agents")
    # Initialize agents
    editor = EditorAgent()
    illustrator = IllustratorAgent()
    story_processor = StoryProcessor()

    try:
        # Set an overall timeout for processing (5 minutes)
        async with asyncio.timeout(300):
            logger.info("Calling editor.edit_story()")
            editor_result = await editor.edit_story(story)
            if not editor_result:
                logger.error("Editor returned no result")
                raise HTTPException(status_code=500, detail="Story editing failed")

            final_story = editor_result.get("final_story")
            illustrator_prompt = editor_result.get("illustrator_prompt")
            logger.debug(f"Final story obtained, length: {len(final_story)}")
            logger.debug(f"Illustrator prompt: {illustrator_prompt}")

            logger.info("Calling illustrator.generate_illustration()")
            illustrations = await illustrator.generate_illustration(illustrator_prompt)
            if not illustrations:
                logger.error("Illustrator returned no illustrations")
                raise HTTPException(status_code=500, detail="Illustration generation failed")

            logger.info("Calling story_processor.process() in thread pool")
            composite_story = await asyncio.to_thread(
                story_processor.process,
                final_story=final_story,
                illustrations=illustrations,
                illustrator_prompt=illustrator_prompt
            )

    except asyncio.TimeoutError:
        logger.error("Operation timed out")
        raise HTTPException(status_code=504, detail="Operation timed out")
    except Exception as e:
        logger.exception(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    logger.info("All async operations complete. Returning JSON response")
    return JSONResponse(content={
        "status": "success",
        "composite_story": composite_story,
        "final_story": final_story,
        "illustrations": illustrations
    })