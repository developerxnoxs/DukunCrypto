# Contributing to AI Technical Analysis Bots

First off, thank you for considering contributing to this project! It's people like you that make this project better.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Set up the development environment (see [Development Setup](#development-setup))
4. Create a new branch for your feature or bugfix

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title** describing the issue
- **Steps to reproduce** the behavior
- **Expected behavior** vs **actual behavior**
- **Screenshots** if applicable
- **Environment details** (Python version, OS, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title** describing the enhancement
- **Detailed description** of the proposed functionality
- **Use case** explaining why this would be useful
- **Possible implementation** if you have ideas

### Adding New Features

Great features to contribute:

- **New technical indicators** (e.g., Stochastic, Williams %R, ATR)
- **Additional cryptocurrency/forex pairs**
- **New data sources** for improved reliability
- **Chart customization options**
- **Multi-language support**
- **Performance optimizations**

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Google Gemini API Key (from [Google AI Studio](https://aistudio.google.com/app/apikey))

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ai-trading-analysis-bots.git
cd ai-trading-analysis-bots

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/
```

## Pull Request Process

1. **Update documentation** if you're changing functionality
2. **Add tests** for new features
3. **Follow the style guidelines** below
4. **Update CHANGELOG.md** with your changes
5. **Ensure all tests pass** before submitting
6. **Request review** from maintainers

### PR Title Format

Use conventional commit format:
- `feat: add new indicator X`
- `fix: resolve data fetching issue`
- `docs: update README installation`
- `refactor: improve chart generation`
- `test: add tests for forex analyzer`

## Style Guidelines

### Python Code Style

- Follow [PEP 8](https://pep8.org/) conventions
- Use type hints for function parameters and returns
- Write docstrings for all public functions/classes
- Maximum line length: 100 characters
- Use meaningful variable names

### Example Code Style

```python
def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate the Relative Strength Index (RSI).

    Args:
        df: DataFrame with 'close' column
        period: RSI calculation period (default: 14)

    Returns:
        Series containing RSI values

    Raises:
        ValueError: If 'close' column is missing
    """
    if 'close' not in df.columns:
        raise ValueError("DataFrame must contain 'close' column")

    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    return 100 - (100 / (1 + rs))
```

### Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests when relevant

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

Thank you for contributing!
