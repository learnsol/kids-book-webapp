# Kids Book Web App

## Overview
The Kids Book Web App is a Python-based web application designed to create children's books by leveraging multiple AI agents. The application takes a short story as input and utilizes an editor agent to ensure coherence, consistency, and readability, while an illustrator agent generates illustrations based on the processed story. The project adheres to Azure AI best practices and responsible AI principles, incorporating content filters to ensure appropriate content for children.

## Project Structure
```
kids-book-webapp
├── kidsbook
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── agents
│   ├── __init__.py
│   ├── editor_agent.py
│   ├── illustrator_agent.py
│   └── story_processor.py
├── webapp
│   ├── __init__.py
│   ├── views.py
│   ├── models.py
│   ├── templates
│   │   └── index.html
│   └── static
│       ├── css
│       └── js
├── manage.py
├── requirements.txt
├── azure_config.json
└── README.md
```

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/kids-book-webapp.git
   cd kids-book-webapp
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Configure Azure AI settings in `azure_config.json`.

## Usage
1. Run the development server:
   ```
   python manage.py runserver
   ```

2. Access the application in your web browser at `http://127.0.0.1:8000`.

3. Input a short story and let the agents process it to create a children's book.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.