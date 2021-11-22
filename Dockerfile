FROM python:3.9-slim

# == Update system ==
RUN apt-get update
RUN apt-get install --no-install-recommends -y curl build-essential 

# Timezone
ENV TZ="Europe/Moscow"
# Python, Pip and Poetry configuration
ENV PYTHONUNBUFFERED=1 
ENV PYTHONDONTWRITEBYTECODE=1 
ENV PIP_NO_CACHE_DIR=off 
ENV PIP_DISABLE_PIP_VERSION_CHECK=on 
ENV PIP_DEFAULT_TIMEOUT=100 
ENV POETRY_VERSION=1.1.8 
ENV POETRY_HOME="/opt/poetry" 
ENV POETRY_VIRTUALENVS_IN_PROJECT=true 
ENV POETRY_NO_INTERACTION=1 
ENV PYSETUP_PATH="/opt/pysetup" 
ENV VENV_PATH="/opt/pysetup/.venv"
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
# Download poetry
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
# Setup directory
WORKDIR $PYSETUP_PATH
# Do not create virtual machines
RUN poetry config virtualenvs.create false
# Copy files representing dependencies
COPY poetry.lock pyproject.toml ./
# Install dependencies
RUN poetry install --no-dev
# Create App folder 
RUN mkdir /skedule
WORKDIR /skedule
# copy all files
COPY . /skedule/
# Run app
CMD ["python3", "main.py"]