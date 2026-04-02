# lunch-picker

A Python project.

## Setup

'''bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies (editable mode with dev tools)
pip install -e ".[dev]"

# Or install just the base package (no tools)
pip install -e .
'''

## About pyproject.toml

This project uses \pyproject.toml\ (modern Python standard) for dependency management.

### Installing dependencies

'''bash
# Install base package only
pip install -e .

# Install with development tools
pip install -e ".[tools]"

# Install with production dependencies
pip install -e ".[prod]"

# Install with development environment (includes both prod and tools)
pip install -e ".[dev]"

# Install specific tool groups
pip install -e ".[format]"    # Black + isort
pip install -e ".[lint]"      # Flake8 + MyPy
pip install -e ".[test]"      # Pytest + pytest-cov
pip install -e ".[hooks]"     # pre-commit
'''

### Managing dependencies

The \pyproject.toml\ file contains three dependency environments:

- **prod** - Production dependencies (empty by default, add your app dependencies here)
- **dev** - Development dependencies (empty by default, add dev-specific packages here)
- **tools** - Development tools (Black, Flake8, MyPy, Pytest, pre-commit if selected)

#### Example: Adding FastAPI to your project

1. **Edit \pyproject.toml\** and add FastAPI to the prod section:

'''toml
[project.optional-dependencies]
prod = [
    "fastapi>=0.100.0",
    "uvicorn>=0.23.0",
]
dev = []
tools = [
    # ... your selected tools ...
]
'''

2. **Reinstall your project** to apply the changes:

'''bash
pip install -e ".[dev]"
'''

This installs your package plus all production and development dependencies.

3. **Verify installation**:

'''bash
python3 -c "import fastapi; print(fastapi.__version__)"
'''

#### General workflow

- Add package name to appropriate section in \pyproject.toml\
- Run \pip install -e ".[dev]"\ to reinstall
- Alternatively, use \pip install <package>\ directly, then update \pyproject.toml\ manually

## Development

'''bash
# Format code
black .

# Lint
flake8 .

# Type check
mypy src/

# Run tests
pytest
'''

## License

MIT
