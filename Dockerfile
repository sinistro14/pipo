FROM python:3.8-slim-bullseye as base

    # python
ENV PYTHONUNBUFFERED=1 \
    # prevents python from creating .pyc files
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
    VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# install required system dependencies
RUN apt-get update && \
    apt-get -y --no-install-recommends install \
        gcc \
        ffmpeg && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip setuptools wheel


# used to build dependencies + create virtual environment
FROM base as builder-base

RUN pip install --ignore-installed distlib --disable-pip-version-check poetry==${POETRY_VERSION}

# copy project requirements file to ensure they will be cached
WORKDIR $PYSETUP_PATH
COPY pyproject.toml ./

# install runtime dependencies, internally uses $POETRY_VIRTUALENVS_IN_PROJECT
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
# app configuration  
ENV ENV=production \
    APP_NAME="pipo"
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY ./${APP_NAME} /${APP_NAME}/

RUN groupadd -r appuser && useradd -r -g appuser appuser && chown -R appuser /${APP_NAME}
USER appuser
ENTRYPOINT python -m ${APP_NAME}
