# Pipo
[![License](https://img.shields.io/github/license/sinistro14/pipo)](https://opensource.org/licenses/MIT)
[![Build](https://github.com/sinistro14/pipo/actions/workflows/docker.yml/badge.svg)](https://github.com/sinistro14/pipo/actions/workflows/docker.yml)
[![Version](https://img.shields.io/github/v/tag/sinistro14/pipo)](https://github.com/sinistro14/pipo/releases)
[![Docker Image](https://img.shields.io/docker/image-size/sinistro14/pipo/latest)](https://hub.docker.com/r/sinistro14/pipo)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Sphinx](https://img.shields.io/badge/Docs-Sphinx-%230000?style=flat&logo=sphinx&color=%230A507A)](https://www.sphinx-doc.org/)

Bot to interactively play music in a discord channel.

## Installation

### Runtime prerequisites
The application is compatible with Windows and Linux based systems.
Since both constitute runtime dependencies, [Docker](https://docs.docker.com/engine/install/) + [Docker Compose](https://docs.docker.com/compose/install/) are assumed to be installed and configured.

### Development only
In case poetry is not locally installed:
```bash
make poetry_setup
```
For being able to run the test suite do:
```bash
make dev_setup
```

For additional help try:
```bash
make help
```

Considering Docker to be already installed, one is able to create the app docker image with
```bash
make image
```

## How to run

### Test suite
Before running the suite make sure file '/tests/.secrets.yaml' was created in accordance with the available [example](.secrets.example.yaml).

```bash
make test
```

### Containerized application (Docker)
Before running more commands make sure file '.env' was created in accordance with the available [example](.env.example).

Start a single container with
```bash
make run_image
```

Start the complete application with
```bash
make run_app
```

## License
This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.
