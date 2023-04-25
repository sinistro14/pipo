include .env

APP=$(PIPO_APP)
CONFIG_PATH=pyproject.toml
POETRY=poetry
PRINT=python -c "import sys; print(str(sys.argv[1]))"

help:
	$(PRINT) "Usage:"
	$(PRINT) "    help          show this message"
	$(PRINT) "    poetry_setup  install poetry to manage python envs and workflows"
	$(PRINT) "    setup         create virtual environment and install dependencies"
	$(PRINT) "    dev_setup     create virtual environment and install dev dependencies"
	$(PRINT) "    lint          run some dev utilities for code quality assurance"
	$(PRINT) "    test          run test suite"
	$(PRINT) "    dist          package application for distribution"
	$(PRINT) "    image         build app docker image"
	$(PRINT) "    run_image     run app docker image in a container"
	$(PRINT) "    run_app       run docker compose"

poetry_setup:
	curl -sSL https://install.python-poetry.org | python3 -
	poetry config virtualenvs.in-project true

setup:
	$(POETRY) install --without dev

dev_setup:
	$(POETRY) install

isort:
	-$(POETRY) run isort .

black:
	-$(POETRY) run black .

mypy:
	-$(POETRY) run mypy .

pylint:
	-$(POETRY) run pylint $(APP)

bandit:
	-$(POETRY) run bandit -c $(CONFIG_PATH) -r . 

vulture:
	-$(POETRY) run vulture

lint: isort black mypy pylint bandit vulture

test:
	$(POETRY) run pytest

dist:
	$(POETRY) dist

image:
	docker build . -t $(APP):latest

run_image: image
	docker run -d --name $(APP) --env-file .env $(APP):latest

run_app:
	docker compose up -d --build

.PHONY: help poetry_setup setup dev_setup lint isort black mypy pylint bandit test dist image run_image run_app
