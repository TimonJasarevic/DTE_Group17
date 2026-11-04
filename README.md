# DTE_Group17
Group 17's public repo for it's Digital Twin Engineering project using the MetroPT dataset.

## Prerequisites

Install:
- [Git](https://git-scm.com/)
- [Astral uv](https://docs.astral.sh/uv/)
- [Docker](https://docs.docker.com/engine/install/)

## Setup

Clone the repository:

```bash
git clone <repository-url>
cd DTE_Group17
```

Install Python dependencies:

```bash
uv sync
```

## Development

Run Python scripts locally:

```bash
uv run python src/<script>.py
```

Add dependencies:

```bash
uv add <package>
```

## Docker

Build and start all services:

```bash
docker compose up --build
```

Stop all services:

```bash
docker compose down
```

## Collaboration

Get the latest changes and synchronize dependencies:

```bash
git pull
uv sync
```

Commit dependency changes to both `pyproject.toml` and `uv.lock`.