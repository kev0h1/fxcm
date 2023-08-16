# Use an official Python runtime as a parent image
FROM python:3.11.1

# Install Nginx
RUN apt-get update && apt-get install -y nginx

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.5.1 

# Install build dependencies and Poetry
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/* \
    && python -m ensurepip --upgrade \
    && python -m pip install "poetry==$POETRY_VERSION"

# Set the working directory to /app
WORKDIR /app

RUN wget https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem


# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in pyproject.toml
RUN poetry config virtualenvs.create false \
    && poetry install $(test "production" == production && echo "--no-dev") --no-interaction --no-ansi

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
# RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
# USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
# 

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World

CMD ["python", "-m", "uvicorn", "src.entry_points.app:create_app", "--host", "0.0.0.0", "--port", "8000"]