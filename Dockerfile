FROM python:3.13-slim

WORKDIR /app
COPY . /app
RUN python -m pip install --upgrade pip \
	&& pip install uv \
	&& uv sync

EXPOSE ${PORT:-8000}

# Define the command to run the application
# Use 0.0.0.0 to make it accessible from outside the container
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
