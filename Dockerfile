FROM python:3.13-slim

WORKDIR /app

# Copy only dependency files first for better layer caching
COPY pyproject.toml requirements.txt uv.lock* ./

# Copy the rest of the application
COPY . /app

# Upgrade pip and install runtime dependencies. Use requirements.txt (exists in repo)
# --no-cache-dir keeps the image smaller
RUN python -m pip install --upgrade pip \
	&& pip install uv \
	&& uv sync

EXPOSE ${PORT:-8000}

# Use python -m uvicorn so we don't rely on a shell entrypoint being present in PATH
# Use sh -c to allow ${PORT} expansion at runtime
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
