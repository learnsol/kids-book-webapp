# Kids Book Web App

## Overview

The Kids Book Web App is a Python-based application that uses multiple AI agents to create children's books. The application accepts a short story as input and uses:
- An **Editor Agent** to review and enhance the story using Azure OpenAI
- An **Illustrator Agent** to generate kid-appropriate illustrations using DALL-E 3
- A **Story Processor** to combine the edited story with generated illustrations into a composite HTML output
- **Azure SQL Database** for storing story data and model interactions

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
├── models/
│   └── database.py        # SQLAlchemy models and database configuration
├── webapp/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
│       └── index.html
├── azure_config.json      # Contains agent and Azure settings
├── main.py               # FastAPI entry point
├── web.config            # Azure App Service configuration
├── startup.py            # ASGI server startup configuration
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.9 or higher
- Azure OpenAI Service access with GPT-4 and DALL-E 3 deployments
- Azure SQL Database
- ODBC Driver 18 for SQL Server

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/kids-book-webapp.git
    cd kids-book-webapp
    ```

2. **Create a virtual environment:**

    ```bash
    python -m venv venv
    venv\Scripts\activate  # Windows
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Configure environment variables:**

    Create a `.env` file in the root directory:
    
    ```env
    AZURE_API_KEY=your_azure_api_key
    AZURE_ENDPOINT=https://your-azure-endpoint.openai.azure.com/
    AZURE_SQL_CONNECTION_STRING=mssql+pyodbc://username:password@server.database.windows.net:1433/database?driver=ODBC+Driver+18+for+SQL+Server
    ```

## Local Development

1. **Run database migrations:**

    The application will automatically create necessary tables on startup.

2. **Start the FastAPI server:**

    ```bash
    uvicorn main:app --reload
    ```

3. **Access the application:**

    Open [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Azure Deployment

1. **Prerequisites:**
   - Existing Azure App Service Plan
   - Azure SQL Database
   - Azure OpenAI Service

2. **Deploy to Azure App Service:**

    ```powershell
    # Install Azure CLI if not already installed
    winget install Microsoft.AzureCLI

    # Login to Azure
    az login

    # Deploy the app
    az webapp deployment source config-zip `
        --resource-group your-resource-group `
        --name your-webapp-name `
        --src deploy.zip
    ```

3. **Configure App Settings:**

    ```powershell
    az webapp config appsettings set `
        --resource-group your-resource-group `
        --name your-webapp-name `
        --settings `
            AZURE_API_KEY="your-api-key" `
            AZURE_ENDPOINT="your-endpoint" `
            AZURE_SQL_CONNECTION_STRING="your-connection-string"
    ```

## Features

- Asynchronous story processing
- Content filtering for child-appropriate material
- DALL-E 3 illustration generation
- HTML story output with downloadable option
- Data persistence in Azure SQL
- Production-ready Azure deployment configuration

## Contributing

Contributions are welcome! Please open an issue or submit a pull request to propose enhancements or to report bugs.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.