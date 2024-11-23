# Flask Application

A simple Flask web application with Docker support.

## Requirements
- Docker
- Python 3.9 (if running locally)

## Running with Docker

1. Build the Docker image:
```bash
docker build -t flask-app .
```

2. Run the container:
```bash
docker run -p 5000:5000 flask-app
```

The application will be available at http://localhost:5000

## Running Locally

1. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

The application will be available at http://localhost:5000
