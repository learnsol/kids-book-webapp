from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import asyncio
import logging
from agents.editor_agent import EditorAgent
from agents.illustrator_agent import IllustratorAgent
from agents.story_processor import StoryProcessor

logger = logging.getLogger('kidsbook')

@csrf_exempt
async def create_kids_book(request):
    """
    Async view that handles story creation and illustration generation.
    Detailed logging is added to trace async operations.
    """
    if request.method != 'POST':
        logger.warning("Request method not allowed")
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        # Get story input from POST data
        story_input = request.POST.get('story')
        if not story_input:
            logger.warning("No story provided in the request")
            return JsonResponse({'error': 'No story provided'}, status=400)

        logger.info("Initializing agents")
        editor = EditorAgent()
        illustrator = IllustratorAgent()
        story_processor = StoryProcessor()

        # Create a timeout for the entire operation
        async with asyncio.timeout(300):  # 5 minutes timeout
            try:
                logger.info("Calling editor.edit_story()")
                editor_result = await editor.edit_story(story_input)
                logger.info("Editor returned its result")
                if not editor_result:
                    logger.error("Editor returned no result")
                    return JsonResponse({'error': 'Story editing failed'}, status=500)

                final_story = editor_result['final_story']
                illustrator_prompt = editor_result['illustrator_prompt']
                logger.debug(f"Final story obtained, length: {len(final_story)}")
                logger.debug(f"Illustrator prompt: {illustrator_prompt}")

                logger.info("Calling illustrator.generate_illustrations()")
                illustrations = await illustrator.generate_illustrations(illustrator_prompt)
                logger.info("Illustrator returned its result")
                if not illustrations:
                    logger.error("Illustrator returned no illustrations")
                    return JsonResponse({'error': 'Illustration generation failed'}, status=500)

                logger.info("Calling story_processor.process() in thread pool")
                composite_story = await asyncio.to_thread(
                    story_processor.process,
                    final_story=final_story,
                    illustrations=illustrations,
                    illustrator_prompt=illustrator_prompt
                )
                logger.info("StoryProcessor returned composite story")

                # Return response only after all processing is complete
                logger.info("All async operations complete. Returning JSON response")
                return JsonResponse({
                    'status': 'success',
                    'composite_story': composite_story,
                    'final_story': final_story,
                    'illustrations': illustrations,
                    'processing_complete': True
                })

            except asyncio.TimeoutError:
                logger.error("Operation timed out")
                return JsonResponse({
                    'error': 'Operation timed out',
                    'status': 'error',
                    'processing_complete': False
                }, status=504)

    except Exception as e:
        logger.exception(f"Error processing request: {str(e)}")
        return JsonResponse({
            'error': str(e),
            'status': 'error',
            'processing_complete': False
        }, status=500)

def index(request):
    """Renders the main page."""
    return render(request, 'index.html')