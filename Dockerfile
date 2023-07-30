# For more information, please refer to https://aka.ms/vscode-docker-python
FROM public.ecr.aws/docker/library/python:3.11


ENV OANDA_TOKEN=865518cb43ca925a7d8ee30ded1d7a3e-31b4a2e1c4bf96de5d31771f15d2a31f
ENV OANDA_ACCOUNT_ID=101-004-26172134-001

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.5.1

RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pip requirements
RUN python -m ensurepip --upgrade \
    && python -m pip install "poetry==$POETRY_VERSION"

WORKDIR /app
COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false \
    && poetry install $(test "production" == production && echo "--no-dev") --no-interaction --no-ansi

COPY . /app


# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "-m", "uvicorn", "src.entry_points.app:create_app", "--host", "0.0.0.0", "--port", "8000"]

