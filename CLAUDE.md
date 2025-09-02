# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Setup

This is a Python project using uv for dependency management. The project requires Python >=3.13.

### Common Commands

```bash
# Install dependencies and sync environment
uv sync

# Run the main application
uv run python main.py

# Run Python scripts with project dependencies
uv run python <script_name>.py

# Add new dependencies
uv add <package_name>

# Format Python code
uv format

# Check and update lockfile
uv lock
```

## Project Structure

This is a minimal Python project using pydantic-ai for AI agent functionality. The project structure is:

- `main.py` - Entry point with a simple pydantic-ai Agent setup using OpenAI GPT-5 model
- `pyproject.toml` - Project configuration with pydantic-ai dependency
- `uv.lock` - Dependency lockfile managed by uv

## Architecture

The project uses pydantic-ai as the main framework for building AI agents. The current implementation in `main.py` creates a basic agent with OpenAI's GPT-5 model and runs a simple synchronous interaction.

Key components:
- **Agent**: Created using pydantic-ai's Agent class with OpenAI model configuration
- **Synchronous execution**: Uses `run_sync()` for immediate response processing

## Development Notes

- Use `uv run` to execute Python scripts with proper environment isolation
- The project uses pydantic-ai with logfire integration for observability
- OpenAI API key needs to be configured in environment for the agent to work