import logging
from openai import OpenAI  # Changed from AsyncAzureOpenAI
from .base_agent import BaseAgent
import re
import asyncio
import time

logger = logging.getLogger('kidsbook')

class EditorAgent(BaseAgent):
    RETRYABLE_ERROR_TOKENS = ("timeout", "connection", "ratelimit", "temporary")

    def __init__(self, config_path='azure_config.json'):
        """
        Initialize the EditorAgent using Azure OpenAI (GPT-4o) and configure the OpenAI SDK.
        """
        super().__init__(config_path, 'editor_agent')
        self.client = self._configure_openai()

    def _configure_openai(self):
        """Configure Azure OpenAI client."""
        try:
            # Format the base_url correctly for Azure OpenAI
            azure_endpoint = self.config['azure_ai']['endpoint'].rstrip('/')
            deployment_name = self.config['deployment_name']
            base_url = f"{azure_endpoint}/openai/deployments/{deployment_name}"
            
            client = OpenAI(
                api_key=self.config['azure_ai']['api_key'],
                base_url=base_url,
                default_query={'api-version': '2025-01-01-preview'}  # API version as default query parameter
            )
            logger.info("Azure OpenAI client configured successfully.")
            return client
        except Exception as e:
            logger.exception(f"Error configuring Azure OpenAI client: {str(e)}")
            raise

    def edit_story(self, story: str):
        """
        Synchronous story editing call for Azure OpenAI.
        Callers in async paths should use `process_story`.
        Retries transient failures with exponential backoff and returns:
        {"final_story": str, "illustrator_prompt": str}
        """
        max_retries = int(self.config.get("max_retries", 2))
        max_attempts = max_retries + 1
        for attempt in range(max_attempts):
            try:
                response = self.client.chat.completions.create(
                    model=self.config['deployment_name'],
                    messages=[
                        {"role": "system", "content": self.config['prompt']['system']},
                        {"role": "user", "content": story}
                    ],
                    temperature=self.config['temperature'],
                    max_tokens=self.config['max_tokens']
                )

                edited_story = response.choices[0].message.content
                return {
                    "final_story": edited_story,
                    "illustrator_prompt": "Create illustrations for: " + edited_story[:200]
                }
            except Exception as e:
                should_retry = attempt < max_attempts - 1 and self._is_retryable_error(e)
                if not should_retry:
                    logger.exception(f"Error editing story: {str(e)}")
                    raise
                backoff = 2 ** attempt
                logger.warning(f"Retrying story edit in {backoff}s after error: {str(e)}")
                time.sleep(backoff)

    def _is_retryable_error(self, error: Exception) -> bool:
        status_code = getattr(error, "status_code", None)
        if status_code in {408, 429}:
            return True
        if isinstance(status_code, int) and status_code >= 500:
            return True
        error_name = error.__class__.__name__.lower()
        error_message = str(error).lower()
        return any(
            token in error_name or token in error_message
            for token in self.RETRYABLE_ERROR_TOKENS
        )

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

    async def process_story(self, story: str):
        """
        Filters and then starts asynchronous editing of the story.
        """
        filtered_story = self.filter_content(story)
        return await asyncio.to_thread(self.edit_story, filtered_story)
