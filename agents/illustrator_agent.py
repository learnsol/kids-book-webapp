from PIL import Image, ImageDraw, ImageFont
import random
import os
import logging
import openai  # Using OpenAI's official python SDK for image generation
from .base_agent import BaseAgent
import json

logger = logging.getLogger('kidsbook')

class IllustratorAgent(BaseAgent):
    def __init__(self, config_path='azure_config.json'):
        """
        Initialize the IllustratorAgent.

        Loads configuration via BaseAgent and configures the OpenAI SDK for image generation
        (using DALL-E3 through Azure OpenAI).
        """
        super().__init__(config_path, 'illustrator_agent')
        # Configure OpenAI for Azure OpenAI image generation.
        self._configure_openai()

    def _configure_openai(self):
        """
        Configures the OpenAI SDK with Azure OpenAI credentials for image generation.
        """
        try:
            openai.api_key = self.config['azure_ai']['api_key']
            openai.api_base = self.config['azure_ai']['endpoint']
            openai.api_type = "azure"
            openai.api_version = "2024-02-01"
            logger.info("OpenAI SDK configured for image generation successfully.")
        except KeyError as e:
            logger.error(f"Missing Azure AI configuration: {str(e)}")
            raise
        except Exception as e:
            logger.exception(f"Error configuring OpenAI SDK for image generation: {str(e)}")
            raise

    async def generate_illustration(self, scene_description: str):
        """
        Asynchronously generates an illustration based on the provided scene description using OpenAI's image API.

        Args:
            scene_description (str): Text describing the scene.

        Returns:
            URL of the generated illustration, or None on failure.
        """
        try:
            # Create the full prompt by combining system prompt and scene description.
            prompt = self._create_prompt(scene_description)
            # Call the image creation endpoint asynchronously.
            response = await openai.Image.acreate(
                prompt=prompt,
                n=self.config['generation_params']['n'],
                size=self.config['image_size'],
                response_format=self.config['generation_params']['response_format']
            )
            # Return the URL of the first generated image.
            logger.info("Illustration generated successfully.")
            return response.data[0].url
        except openai.error.OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
        except Exception as e:
            logger.exception(f"Image generation failed: {str(e)}")
            raise

    async def generate_illustrations(self, illustrator_prompt: str):
        """
        Asynchronously generates multiple illustrations based on the interesting points
        extracted from the story.

        Args:
            illustrator_prompt (str): Concatenated interesting points separated by delimiter.

        Returns:
            list: URLs of the generated illustrations (up to 5).
        """
        try:
            # Split the prompt into individual scenes (max 5)
            scenes = [p.strip() for p in illustrator_prompt.split("||")][:5]
            illustration_urls = []

            # Generate an illustration for each scene
            for scene in scenes:
                illustration_url = await self.generate_illustration(scene)
                if illustration_url:
                    illustration_urls.append(illustration_url)

            logger.info(f"Generated {len(illustration_urls)} illustrations successfully.")
            return illustration_urls
        except Exception as e:
            logger.exception(f"Failed to generate illustrations: {str(e)}")
            return None

    def _create_prompt(self, scene_description: str):
        """
        Creates a prompt for image generation by combining the system prompt, style guidelines,
        and the interesting points extracted from the story.

        Args:
            scene_description (str): Concatenated interesting points from the editor agent.

        Returns:
            str: A full text prompt instructing the illustrator agent to generate a kid-appropriate image.
        """
        # Retrieve configuration values
        system_prompt = self.config['prompt_config']['system']
        art_style = self.config['prompt_config']['style_guide'].get('art_style', 'cartoon')
        
        # Build additional instructions tailored for kids' book illustrations.
        instructions = (
            "Use the following interesting points to create a colorful, engaging and age-appropriate illustration "
            "for a children's book. Ensure the style is bright and playful, suitable for children ages 4-10."
        )
        
        # Combine all pieces to form the final prompt.
        full_prompt = (
            f"{system_prompt} "
            f"{instructions} "
            f"Style: {art_style}. "
            f"Details: {scene_description}."
        )
        
        return full_prompt