# Kids Book Web App

## Overview

The Kids Book Web App is a Python-based application that uses multiple AI agents to create children’s books. The application accepts a short story as input and uses:
- An **Editor Agent** to review and enhance the story.
- An **Illustrator Agent** to generate kid-appropriate illustrations based on interesting points extracted from the story.
- A **Story Processor** to combine the edited story with generated illustrations into a composite output.

This project is built with [FastAPI](https://fastapi.tiangolo.com/) for its asynchronous backend and leverages Azure OpenAI services for advanced AI functionality. The application adheres to responsible AI principles and includes content filters to ensure all generated material is child-friendly.

## Project Structure

```
kids-book-webapp/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py
│   ├── editor_agent.py
│   ├── illustrator_agent.py
│   └── story_processor.py
├── webapp/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
│       └── index.html
├── azure_config.json      # Contains agent and Azure settings
├── main.py                # FastAPI entry point
├── requirements.txt
└── README.md
```

> **Note:** Legacy Django files such as `manage.py`, the `kidsbook/` folder, and Django templates have been removed in favor of this modern FastAPI-based implementation.

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/kids-book-webapp.git
    cd kids-book-webapp
    ```

2. **Create a virtual environment:**

    ```bash
    python -m venv venv
    ```
    
    On Windows, activate with:
    
    ```bash
    venv\Scripts\activate
    ```
    
    On Unix or macOS:
    
    ```bash
    source venv/bin/activate
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Configure Azure AI settings:**

    Update the `azure_config.json` file with your Azure endpoint and API key. It should contain the necessary configuration for both the editor and illustrator agents.

5. **(Optional) Configure environment variables:**

    Create a `.env` file in the root directory and add:
    
    ```env
    AZURE_API_KEY=your_azure_api_key
    AZURE_ENDPOINT=https://your-azure-endpoint.openai.azure.com/
    ```

## Usage

1. **Run the FastAPI server:**

    Use Uvicorn to start the development server:

    ```bash
    uvicorn main:app --reload
    ```

    The server will start on [http://127.0.0.1:8000](http://127.0.0.1:8000).

2. **Access the application:**

    Open your web browser and navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000).  
    The homepage will display a form where you can enter a short story.

3. **Generate Your Book:**

    - Enter a short story in the form.
    - Submit the form.
    - The backend will asynchronously process the story:
       - Editing the story using the Editor Agent.
       - Generating an illustration via the Illustrator Agent.
       - Combining the outputs using the Story Processor.
    - Once processing is complete, the composite story, along with the final edited text and illustration URL, will be returned as a JSON response and rendered on the front end.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request to propose enhancements or to report bugs.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.