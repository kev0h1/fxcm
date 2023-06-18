# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11.1

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.3.1

# Install pip requirements
RUN python -m pip install "poetry==$POETRY_VERSION"

WORKDIR /app
COPY . /app
COPY poetry.lock pyproject.toml /code/
RUN poetry config virtualenvs.create false \
    && poetry install $(test "$YOUR_ENV" == production && echo "--no-dev")--no-interaction --no-ansi




# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["uvicorn", "src.api.app:create_app", "--host", "0.0.0.0", "--port", "8000"]
