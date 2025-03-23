import logging
import openai  # Using the openai package (v1.x)
from .base_agent import BaseAgent
import re
import asyncio

logger = logging.getLogger('kidsbook')

class EditorAgent(BaseAgent):
    def __init__(self, config_path='azure_config.json'):
        """
        Initialize the EditorAgent using Azure OpenAI (GPT-4o) and configure the OpenAI SDK.
        """
        super().__init__(config_path, 'editor_agent')
        # Enforce usage of GPT-4o for text completions.
        self.config['model'] = 'gpt-4o-mini'
        self._configure_openai()

    def _configure_openai(self):
        """
        Configure OpenAI SDK credentials for Azure OpenAI.
        """
        try:
            openai.api_key = self.config['azure_ai']['api_key']
            openai.api_base = self.config['azure_ai']['endpoint']
            openai.api_type = "azure"
            openai.api_version = "2025-01-01-preview"
            logger.info("OpenAI SDK configured successfully.")
        except KeyError as e:
            logger.error(f"Missing Azure AI configuration: {str(e)}")
            raise
        except Exception as e:
            logger.exception(f"Error configuring OpenAI SDK: {str(e)}")
            raise

    async def edit_story(self, story: str):
        """
        Asynchronously sends a story for editing and returns a dictionary with the final story
        and a string of concatenated interesting points.
        """
        try:
            # Build messages (system prompt and user story)
            messages = [
                {"role": "system", "content": self.config['prompt']['system']},
                {"role": "user", "content": story}
            ]
            response = await openai.ChatCompletion.acreate(
                engine=self.config['model'],
                messages=messages,
                max_tokens=self.config['max_tokens'],
                temperature=self.config['temperature']
            )
            final_story = response.choices[0].message.content
            # Extract interesting points as a single concatenated prompt string.
            interesting_points = self._extract_interesting_points(final_story)
            logger.info("Story edited successfully.")
            return {
                "final_story": final_story,
                "illustrator_prompt": interesting_points
            }
        except openai.error.OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
        except Exception as e:
            logger.exception(f"An unexpected error occurred during story editing: {str(e)}")
            raise

    def _extract_interesting_points(self, story: str):
        """
        Extracts interesting points from the story.
        """
        # Implementation for extracting interesting points
        # Add your logic here
        return "Interesting points extracted from the story."

    def filter_content(self, story: str):
        """
        Applies content filtering ensuring story appropriateness.
        """
        banned_keywords = [
            'violence', 'murder', 'anger', 'hate',
            'explicit', 'adult', 'sexual', 'scary',
            'blood', 'curse', 'profanity'
        ]
        sentences = re.split(r'(?<=[.!?])\s+', story)
        filtered_sentences = []
        for sentence in sentences:
            if not any(re.search(r'\b' + re.escape(keyword) + r'\b', sentence, flags=re.IGNORECASE)
                       for keyword in banned_keywords):
                filtered_sentences.append(sentence)
        return ' '.join(filtered_sentences)

    def process_story(self, story: str):
        """
        Filters and then starts asynchronous editing of the story.
        """
        filtered_story = self.filter_content(story)
        return self.edit_story(filtered_story)