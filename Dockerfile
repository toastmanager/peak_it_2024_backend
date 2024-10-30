FROM python:3.12-alpine

# Set environment variables for Poetry installation
ENV POETRY_HOME="/root/.poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install dependencies for installing Poetry
RUN apk add --no-cache curl

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set the working directory in the container
WORKDIR /backend

# Copy the pyproject.toml and poetry.lock files into the container
COPY pyproject.toml poetry.lock* /backend/

# Configure Poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies using Poetry
RUN poetry install --no-dev

# Copy the rest of application code and the entrypoint script
COPY . /backend
COPY entrypoint.sh /backend/entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /backend/entrypoint.sh

# Command to run application
CMD ["/backend/entrypoint.sh"]