import time
import asyncio
import json
import logging
from openai import AsyncAzureOpenAI  # Changed to AsyncAzureOpenAI
from httpx import AsyncClient, Request, Response, AsyncHTTPTransport
from .base_agent import BaseAgent

logger = logging.getLogger('kidsbook')

class IllustratorAgent(BaseAgent):
    def __init__(self, config_path='azure_config.json'):
        """Initialize the IllustratorAgent with configuration for DALL-E 3."""
        super().__init__(config_path, 'illustrator_agent')
        self.client = self._configure_openai()

    def _configure_openai(self):
        """Configure Azure OpenAI client."""
        try:
            client = AsyncAzureOpenAI(  # Using AsyncAzureOpenAI
                api_key=self.config['azure_ai']['api_key'],
                api_version="2024-02-01",
                azure_endpoint=self.config['azure_ai']['endpoint']
            )
            logger.info("Azure OpenAI client configured successfully.")
            return client
        except Exception as e:
            logger.exception(f"Error configuring Azure OpenAI client: {str(e)}")
            raise

    async def generate_cover_image(self, final_story: str):
        """
        Generate a cover image using DALL-E 3 via Azure OpenAI.
        
        Args:
            final_story (str): The final story text from the EditorAgent.
        Returns:
            str: URL of the generated cover image.
        """
        try:
            prompt = self._create_cover_prompt(final_story)
            
            response = await self.client.images.generate(
                model=self.config['deployment_name'],
                prompt=prompt,
                n=self.config['generation_params']['n'],
                size=self.config['image_size'],
                quality="standard"
            )
            
            logger.info("Cover image generated successfully.")
            return response.data[0].url
            
        except Exception as e:
            logger.exception(f"Cover image generation failed: {str(e)}")
            raise

    def _create_cover_prompt(self, final_story: str):
        """Create a prompt for the cover image."""
        story_summary = final_story[:200]
        cover_instructions = (
            "Create a captivating and colorful cover image for a children's book based on the following narrative. "
            "The cover should be engaging, playful, and visually reflect the story's themes."
        )
        full_prompt = f"{cover_instructions}\n\nStory Summary: {story_summary}"
        return full_prompt