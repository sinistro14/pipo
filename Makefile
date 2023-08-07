-include .env

APP=$(PIPO_APP)
CONFIG_PATH=pyproject.toml
POETRY=poetry
PRINT=python -c "import sys; print(str(sys.argv[1]))"

.PHONY: help
help:
	$(PRINT) "Usage:"
	$(PRINT) "    help          show this message"
	$(PRINT) "    poetry_setup  install poetry to manage python envs and workflows"
	$(PRINT) "    setup         create virtual environment and install dependencies"
	$(PRINT) "    dev_setup     create virtual environment and install dev dependencies"
	$(PRINT) "    lint          run dev utilities for code quality assurance"
	$(PRINT) "    docs          generate code documentation"
	$(PRINT) "    test          run test suite"
	$(PRINT) "    coverage      run coverage analysis"
	$(PRINT) "    dist          package application for distribution"
	$(PRINT) "    image         build app docker image"
	$(PRINT) "    run_image     run app docker image in a container"
	$(PRINT) "    run_app       run docker compose"

.PHONY: poetry_setup
poetry_setup:
	curl -sSL https://install.python-poetry.org | python3 -
	poetry config virtualenvs.in-project true

.PHONY: setup
setup:
	$(POETRY) install --without dev

.PHONY: dev_setup
dev_setup:
	$(POETRY) install

.PHONY: black
black:
	-$(POETRY) run black .

.PHONY: ruff
ruff:
	-$(POETRY) run ruff .

.PHONY: ruff_fix
ruff_fix:
	-$(POETRY) run ruff --fix .

.PHONY: vulture
vulture:
	-$(POETRY) run vulture

.PHONY: lint
lint: black ruff vulture

.PHONY: test
test:
	$(POETRY) run pytest --cov

.PHONY: coverage
coverage:
	$(POETRY) run coverage report -m

.PHONY: docs
docs:
	$(POETRY) run make -C docs html

.PHONY: dist
dist:
	$(POETRY) dist

.PHONY: image
image: docs
	docker build . -t $(APP):latest

.PHONY: dev_image
dev_image:
	docker build . --target development -t $(APP)-dev:latest

.PHONY: run_image
run_image: image
	docker run -d --name $(APP) --env-file .env $(APP):latest

.PHONY: run_dev_image
run_dev_image: dev_image
	docker run --name $(APP)-dev --env-file .env $(APP)-dev:latest

.PHONY: run_app
run_app: docs
	docker compose up -d --build --remove-orphans
