# Career Coach

A Python application for career coaching and guidance.

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- A virtual environment tool (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/career-coach.git
cd career-coach
```

2. Create and activate a virtual environment (recommended):
```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

## Running the Application

To start the application, run:
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501` in your web browser.

## Dependencies

The project uses the following main dependencies:
- google-generativeai
- openai
- pdfplumber
- psycopg2-binary
- sqlalchemy
- streamlit

## Environment Variables

Make sure to set up any required environment variables for API keys and database connections before running the application.

