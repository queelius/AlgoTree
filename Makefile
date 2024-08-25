# Makefile at the root of your project

# Variables
PYTHON=python3
PIP=pip
SOURCES=$(shell find AlgoTree -name "*.py")
TESTS=$(shell find test -name "*.py")

# Phony targets
.PHONY: all install test lint clean docs coverage

# Default targetq

# Install dependencies
install:
	$(PIP) install -r requirements.txt

# Run tests
test:
	$(PYTHON) -m unittest discover -s test

# Lint the code
lint:
	$(PYTHON) -m flake8 $(SOURCES) $(TESTS)

# Clean build artifacts
clean:
	rm -rf build dist *.egg-info
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -type f -delete
	find . -name "*.pyo" -type f -delete

# Generate documentation
docs:
	sphinx-apidoc -o source AlgoTree
	sphinx-build -b html source docs

# Run test coverage
coverage:
	coverage run -m unittest discover -s test
	coverage report
	coverage json

pypi:
	$(PYTHON) setup.py sdist bdist_wheel
	$(PYTHON) -m twine upload dist/*
