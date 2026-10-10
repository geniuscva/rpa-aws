# RPA Mock Servers

This directory contains mock servers used for local development and testing of the RPA robot without hitting production endpoints.

## Accuity Mock Server (`accuity_app.py`)

This is a lightweight Flask application that mocks the Accuity portal for testing the RPA robot's search and PDF export functionality (FR6). 
It exposes endpoints for login, search, results, and PDF generation.

### Prerequisites

You need to have `Flask` installed in your Python environment:

```bash
pip install Flask
```

### Running the server

1. Open a terminal.
2. Navigate to the project root directory.
3. Run the Flask application:

```bash
python mock_servers/accuity_app.py
```

The mock server will start on `http://localhost:5000`.

### Endpoints

- `/` or `/login`: The login page.
- `/search`: The search page to query entities.
- `/result`: The results page showing Match Score 100.
- `/record`: The detail page for an entity.
- `/export`: Generates and downloads a dummy PDF.
