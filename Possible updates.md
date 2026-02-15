# Possible Updates

## High priority

- [x] **Avoid exposing internal exceptions to clients**  
  Updated `main.py` to return a generic `Internal server error` for unexpected failures while keeping full details in server logs.

- [x] **Add automated tests for core flows**  
  Added `tests/test_agents_and_processor.py` with focused tests for:
  - Agent content filtering behavior
  - Agent retry behavior in `EditorAgent.edit_story`
  - Story HTML output generation
  - Text Analytics client guard behavior when config is missing

- [x] **Fix async/sync inconsistencies in story editing path**  
  Converted `EditorAgent.edit_story` to synchronous and kept async orchestration in `main.py`/`process_story` with `asyncio.to_thread`.

- [x] **Remove or reconcile unused Django implementation**  
  Replaced legacy Django-specific view code in `webapp/views.py` with explicit compatibility stubs directing usage to FastAPI routes in `main.py`.

## Medium priority

- [x] **Strengthen input validation and request limits**  
  Added `min_length`/`max_length` form validation and trimming checks in `main.py`.

- [x] **Improve resilience around external API calls**  
  Added bounded retry + exponential backoff for OpenAI text and image generation paths in:
  - `agents/editor_agent.py`
  - `agents/illustrator_agent.py`

- [x] **Resolve incomplete Text Analytics wiring**  
  `StoryProcessor` now safely initializes `azure_config` and returns `None` with a warning when endpoint/key are missing, preventing attribute errors.

- [x] **Cache agent initialization where safe**  
  Added lazy shared agent initialization in `main.py` (`get_agents`) and warm-up on app startup.

## Low priority

- [x] **Consolidate dependency declarations**  
  Cleaned comment-only lines from `requirements.txt` and kept a plain dependency list.

- [x] **Improve contributor/developer documentation**  
  Updated `README.md` with:
  - A minimal `.env` local template
  - A documented test command (`python -m unittest discover ...`)
