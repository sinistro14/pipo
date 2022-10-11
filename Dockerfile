FROM jrottenberg/ffmpeg:5.1.2-alpine313 as base

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
    VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# install required system dependencies
RUN apk --update --no-cache add \
    python3 \
    py3-pip \
    py3-psutil \
    && pip install --upgrade pip setuptools wheel

# `builder-base` stage is used to build deps + create virtual environment
FROM base as builder-base

RUN apk add --no-cache \
        gcc \
        curl \
        musl-dev \
        libffi-dev \
        python3-dev \
        libressl-dev && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile=minimal && \
    source $HOME/.cargo/env && \
    pip install --ignore-installed distlib --disable-pip-version-check poetry==${POETRY_VERSION} && \
    apk del \
        gcc \
        curl \
        musl-dev \
        libffi-dev \
        python3-dev \
        libressl-dev

# copy project requirement files to ensure they will be cached
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# install runtime deps, internally uses $POETRY_VIRTUALENVS_IN_PROJECT
RUN poetry install --without dev

# `development` image is used during development / testing
FROM base as development
ENV ENV=development \
    APP_NAME="pipo"
WORKDIR $PYSETUP_PATH

# copy built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# quicker install as runtime deps are already installed
RUN poetry install

# becomes code mountpoint
WORKDIR /app

CMD uvicorn --reload ${APP_NAME}.app:app


# `production` image used for runtime
FROM base as production
# app configuration  
ENV ENV=production \
    APP_NAME="pipo"
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY ./${APP_NAME} /${APP_NAME}/
ENTRYPOINT gunicorn -k uvicorn.workers.UvicornWorker -b ${APP_HOST}:${APP_PORT} ${APP_NAME}.app:app