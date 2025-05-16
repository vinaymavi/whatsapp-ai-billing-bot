# WhatsApp AI Billing Bot

A FastAPI-based application that integrates with WhatsApp to provide AI-powered billing and invoice management.

## Features

- WhatsApp integration for communication
- AI-powered billing and invoice processing
- Integration with Google Cloud services (Firestore, Storage)
- Vector database for semantic search (Pinecone)

## Technology Stack

- **Backend**: FastAPI, Python 3.13
- **AI/ML**: LangChain, OpenAI
- **Database**: Google Firestore, Pinecone (vector database)
- **Storage**: Google Cloud Storage
- **Deployment**: Docker, Google Cloud Run, GitHub Actions

## Local Development

### Prerequisites

- Python 3.13
- Virtual environment (venv)
- Google Cloud SDK (optional for local GCP integration)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/whatsapp-ai-billing-bot.git
cd whatsapp-ai-billing-bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp example.env .env
# Edit .env with your actual configuration values
```

### Running the Application

```bash
# Run the application using uvicorn
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the VS Code task
# Press Ctrl+Shift+B or run the "Run Server" task
```

### Running Tests

```bash
# Run tests using pytest
python -m pytest tests -v

# Or use the VS Code task
# Run the "Run Tests" task
```

## Docker Setup

The application can be containerized using Docker:

```bash
# Build the Docker image
docker build -t whatsapp-ai-billing-bot .

# Run the container
docker run -p 8000:8000 --env-file .env whatsapp-ai-billing-bot
```

## Deployment

This project includes CI/CD setup for automatic deployment to Google Cloud Run.
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on setting up the deployment pipeline.

## API Documentation

When the application is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc