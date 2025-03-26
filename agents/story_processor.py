from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import json
import re
import logging
from datetime import datetime

logger = logging.getLogger('kidsbook')

class StoryProcessor:
    def __init__(self, azure_config_path="azure_config.json"):
        self.azure_config_path = azure_config_path
        # Add any initialization that depends on the config here

    def load_azure_config(self, path):
        with open(path) as config_file:
            return json.load(config_file)

    def create_text_analytics_client(self):
        endpoint = self.azure_config['endpoint']
        key = self.azure_config['key']
        return TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    def filter_content(self, story):
        # Implement content filtering logic here
        # This should include checks for appropriateness and adherence to responsible AI principles
        return story  # Placeholder for filtered story

    def process_story(self, story):
        filtered_story = self.filter_content(story)
        # Additional processing logic can be added here
        return filtered_story

    def analyze_story(self, story):
        processed_story = self.process_story(story)
        # Call Azure AI services for further analysis if needed
        return processed_story

    def process(self, final_story: str, cover_image_url: str, illustrator_prompt: str):
        """
        Creates an HTML document combining the cover image and story.
        """
        try:
            # Split story into paragraphs
            paragraphs = final_story.split('\n')
            
            # Create HTML with modern styling
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Your Kids Book</title>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        line-height: 1.6;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f9f9f9;
                    }}
                    .cover {{
                        text-align: center;
                        margin-bottom: 2em;
                    }}
                    .cover img {{
                        max-width: 100%;
                        height: auto;
                        border-radius: 10px;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    }}
                    .story {{
                        background: white;
                        padding: 2em;
                        border-radius: 10px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .story p {{
                        margin-bottom: 1em;
                    }}
                    .meta {{
                        text-align: center;
                        color: #666;
                        font-size: 0.9em;
                        margin-top: 2em;
                    }}
                </style>
            </head>
            <body>
                <div class="cover">
                    <img src="{cover_image_url}" alt="Story Cover Image">
                </div>
                <div class="story">
                    {"".join(f'<p>{paragraph}</p>' for paragraph in paragraphs if paragraph.strip())}
                </div>
                <div class="meta">
                    <p>Generated on {datetime.now().strftime('%B %d, %Y')}</p>
                </div>
            </body>
            </html>
            """
            
            logger.info("StoryProcessor: HTML content generated successfully")
            return html_content
            
        except Exception as e:
            logger.error(f"Error generating HTML content: {str(e)}")
            raise