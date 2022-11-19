FROM python:3.8-slim-bullseye as base

    # python
ENV PYTHON_VERSION=3.8.15 \
    PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.2.2 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask interactive questions
    POETRY_NO_INTERACTION=1 \
    \
    # paths
    # where requirements + virtual environment will be
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv" \
    \
    # prepend poetry and venv to path
    PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# install required system dependencies
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
        ffmpeg \
    && apt-get clean \
    && pip install --upgrade pip setuptools wheel


# `builder-base` stage is used to build deps + create virtual environment
#FROM base as builder-base
FROM rust:1.65-slim-bullseye as builder-base

    # python
ENV PYTHON_VERSION=3.8.15 \
    PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.2.2 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask interactive questions
    POETRY_NO_INTERACTION=1 \
    \
    # paths
    # where requirements + virtual environment will be
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv" \
    \
    # prepend poetry and venv to path
    PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# gcc and python3-dev will be used for proj dependencies install, not being removed here
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
        gcc \
        python3 \
        python3-pip \
        python3-dev \
        libffi-dev \
        libssl-dev \
        libc-dev \
    && apt-get clean \
    && pip install --ignore-installed distlib --disable-pip-version-check poetry==${POETRY_VERSION}

# copy project requirement files to ensure they will be cached
WORKDIR $PYSETUP_PATH
COPY pyproject.toml ./

# install runtime deps, internally uses $POETRY_VIRTUALENVS_IN_PROJECT
RUN poetry install --without dev


# `development` image used during development / testing
FROM base as development
ENV ENV=development \
    APP_NAME="pipo"
WORKDIR $PYSETUP_PATH

# copy built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# quicker install as runtime deps are already installed
RUN poetry install

ENTRYPOINT python -m ${APP_NAME}


# `production` image used for runtime
FROM base as production

ARG USERNAME=appuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID
# app configuration
ENV ENV=production \
    APP_NAME="pipo"
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY ./${APP_NAME} /${APP_NAME}/

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && chown -R $USERNAME /${APP_NAME}
USER $USERNAME
ENTRYPOINT python -m ${APP_NAME}
