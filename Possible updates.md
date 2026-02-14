# Possible Updates

## High priority

1. **Avoid exposing internal exceptions to clients**  
   `main.py` currently returns `detail=str(e)` for 500 errors. Return a generic error message to users and keep detailed errors in logs only.

2. **Add automated tests for core flows**  
   There are no `test*.py` files in the repository. Add tests for:
   - `POST /create_kids_book/` success and failure paths (`main.py`)
   - Agent behavior and failure handling (`agents/editor_agent.py`, `agents/illustrator_agent.py`)
   - HTML output generation (`agents/story_processor.py`)

3. **Fix async/sync inconsistencies in story editing path**  
   `EditorAgent.edit_story` is declared async but performs a synchronous OpenAI call. `process_story` then wraps that async method with `asyncio.to_thread`, which is an incorrect pattern (`agents/editor_agent.py`). Align this implementation to a single, correct async model.

4. **Remove or reconcile unused Django implementation**  
   `webapp/views.py` includes a Django async view that is not used by the FastAPI app in `main.py`. Keeping both patterns increases maintenance overhead and confusion.

## Medium priority

5. **Strengthen input validation and request limits**  
   `story` input is required but has no length/size constraints (`main.py`). Add limits and validation to reduce abuse risk and control cost.

6. **Improve resilience around external API calls**  
   Add retries with exponential backoff and better handling for transient failures/rate limits in Azure OpenAI calls (`agents/editor_agent.py`, `agents/illustrator_agent.py`).

7. **Resolve incomplete Text Analytics wiring**  
   `StoryProcessor.create_text_analytics_client` expects `self.azure_config`, but that attribute is never initialized (`agents/story_processor.py`). Either complete integration or remove dead code paths.

8. **Cache agent initialization where safe**  
   Agents are instantiated per request (`main.py`), which repeatedly loads config and client setup. Consider app-lifecycle initialization for reusable clients.

## Low priority

9. **Consolidate dependency declarations**  
   `requirements.txt` contains comments like “Add this line” and “Add these new dependencies”. Clean and pin versions where appropriate for reproducibility.

10. **Improve contributor/developer documentation**  
   Expand local setup instructions with a minimal `.env` template, expected services, and a clear testing command once tests are added (`README.md`).
