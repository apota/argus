# Argus Test Suite

This directory contains test files for the Argus AWS Resource Explorer library.

## Test Files

### `test_runner.py`
Comprehensive test runner that performs:
- Import tests for all modules
- Instantiation tests for core classes
- Module structure validation

**Usage:**
```bash
cd c:\work\argus\src\test
python test_runner.py
```

### `test_imports.py`
Simple import test script that verifies all modules can be imported correctly.

**Usage:**
```bash
cd c:\work\argus\src\test
python test_imports.py
```

### `test_quick.py`
Quick test script for basic functionality verification.

**Usage:**
```bash
cd c:\work\argus\src\test
python test_quick.py
```

### `test_common.py`
Unit tests for the common module functionality using unittest framework.

**Usage:**
```bash
cd c:\work\argus\src\test
python test_common.py
```

## Running Tests

### From the test directory:
```bash
cd c:\work\argus\src\test

# Run comprehensive test suite
python test_runner.py

# Run individual test files
python test_imports.py
python test_quick.py
python test_common.py
```

### From the project root:
```bash
cd c:\work\argus

# Run tests using Python module syntax
python -m src.test.test_runner
python -m src.test.test_imports
python -m src.test.test_quick
python -m src.test.test_common
```

## Test Requirements

- Python 3.7+
- All dependencies from `requirements.txt`
- AWS credentials configured (for integration tests)

## Adding New Tests

When adding new modules to Argus:

1. Add import tests to `test_runner.py`
2. Create module-specific unit test files following the pattern `test_<module_name>.py`
3. Update this README with new test information

## Notes

- Import tests verify that all modules can be loaded without errors
- Instantiation tests may show credential-related warnings (this is expected)
- Unit tests use mocking to avoid requiring actual AWS credentials
- Integration tests (if any) require valid AWS credentials
