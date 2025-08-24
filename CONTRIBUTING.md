# Contributing to the Health Scoring Agent

First off, thank you for considering contributing to the Health Scoring Agent! We welcome contributions from everyone. This document provides guidelines for contributing to the project.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior.

## How Can I Contribute?

There are many ways to contribute, from writing tutorials or blog posts, improving the documentation, submitting bug reports and feature requests or writing code which can be incorporated into the main project.

### Reporting Bugs

If you find a bug, please [create an issue](https://github.com/joeshirey/HealthScoringAgent/issues/new) and provide the following information:

- A clear and descriptive title.
- A detailed description of the problem, including steps to reproduce it.
- The expected behavior and what actually happened.
- Your system information (OS, Python version, etc.).

### Suggesting Enhancements

If you have an idea for a new feature or an enhancement to an existing one, please [create an issue](https://github.com/joeshirey/HealthScoringAgent/issues/new) to discuss it first. This allows us to coordinate our efforts and avoid duplicated work.

### Pull Requests

We welcome pull requests! Please follow these steps to submit your contribution:

1. **Fork the repository** and create a new branch from `main`.
    - A good branch name would be `feature/33-add-new-agent` or `bugfix/42-fix-api-error`.
2. **Set up your development environment.**
3. **Make your changes.** Ensure your code follows the project's style guidelines.
4. **Add or update tests** for your changes.
5. **Update the documentation** if your changes affect it.
6. **Submit a pull request** to the `main` branch of the original repository.

## Development Setup

To get started with development, you'll need to set up your local environment.

1. **Clone your fork:**

    ```sh
    git clone https://github.com/YOUR_USERNAME/HealthScoringAgent.git
    cd HealthScoringAgent
    ```

2. **Create and activate a virtual environment:**

    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. **Install dependencies:**

    The project uses `uv` for dependency management.

    ```sh
    pip install uv
    uv pip install -e .[dev]
    ```

    The `[dev]` extra includes all the dependencies needed for development, such as `ruff` for linting and `pytest` for testing.

## Code Style and Linting

This project follows the **PEP 8** style guide and uses `ruff` for linting and formatting. Before submitting a pull request, please ensure your code is clean.

- **Check for linting errors:**

    ```sh
    uv run ruff check .
    ```

- **Automatically fix errors:**

    ```sh
    uv run ruff check . --fix
    ```

- **Format your code:**

    ```sh
    uv run ruff format .
    ```

## Testing

All new features and bug fixes should be accompanied by tests. This project uses `pytest` for testing.

- **Run all tests:**

    ```sh
    uv run pytest
    ```

- **Run tests for a specific file:**

    ```sh
    uv run pytest tests/test_my_feature.py
    ```

## Documentation

If you add a new feature or change an existing one, please update the documentation accordingly. The documentation is written in Markdown and is located in the `docs/` directory and in the `README.md`.

## Submitting a Pull Request

When you're ready to submit your pull request, please make sure it meets the following criteria:

- The pull request has a clear and descriptive title.
- The pull request description explains the changes and references the relevant issue(s).
- The code is well-commented and follows the project's style guidelines.
- Tests have been added or updated for the changes.
- The documentation has been updated.

Thank you for your contribution!
