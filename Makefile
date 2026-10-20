VERSION ?= 0.0.11
PYTHON ?= python3

.PHONY: test daml-test-legacy daml-test-example daml-test-all dev dev-deps lint clean clean-pyc clean-build clean-test build release

init:
	$(PYTHON) setup.py install

dev-init:
	$(PYTHON) -m pip install . --group dev

test:
	pytest

daml-test-legacy:
	cd examples/legacy/splice-util-batched-markers-test && daml test --all

daml-test-example:
	cd examples/splice-util-batched-markers-test && daml test --all

daml-test-all: daml-test-legacy daml-test-example

lint: mypy black flake8 isort

mypy:
	mypy -p forge

black:
	black forge/ tests/ setup.py

flake8: black
	flake8 forge/ tests/

isort: black
	isort forge/ tests/ setup.py

build: clean
	$(PYTHON) -m build
	ls -la dist/

dev:
	SETUPTOOLS_SCM_PRETEND_VERSION=$(VERSION) $(MAKE) build

dev-release:
	SETUPTOOLS_SCM_PRETEND_VERSION=$(VERSION) \
	$(PYTHON) -m pip install --no-deps --force-reinstall -e .

release: build
	twine check dist/*
	#twine upload --repository-url <your-private-index> dist/*

clean: clean-build clean-pyc clean-test

clean-build:
	@echo Cleaning python build files...
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info
	@rm -f forge/version.py forge/damlforge_git_commithash.txt
	@rm -f *.spec

clean-pyc:
	@echo Cleaning python files...
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rmdir {} +

clean-test:
	@echo Cleaning test files...
	@find . -name 'htmlcov' -exec rm -rf {} +
	@rm -fr coverage.xml
	@rm -fr .coverage
	@rm -fr .eggs/
	@rm -fr .hypothesis/
	@rm -fr .pytest_cache/
	@rm -rf .tox/
	@rm -fr .mypy_cache/
