# Tests directory

This directory contains unit tests for the backtest-py framework.

## Structure

- `test_models/` - Tests for data models
- `test_repositories/` - Tests for data repositories
- `test_core/` - Tests for core functionality
- `test_integration/` - Integration tests

## Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_models/test_market_data.py

# Run with coverage
python -m pytest --cov=backtest
```
