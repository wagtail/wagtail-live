.PHONY: docs

default: clean

clean:
	find . -name '*.pyc' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.egg-info' -exec rm -rf {} +
	rm -rf dist/ build/

format:
	isort src/wagtail_live wagtail_live_interface tests setup.py
	black src/wagtail_live wagtail_live_interface tests setup.py
	flake8 src/wagtail_live wagtail_live_interface tests setup.py

lint:
	isort --check-only --diff src/wagtail_live wagtail_live_interface tests setup.py
	black --check --diff src/wagtail_live wagtail_live_interface tests setup.py
	flake8 src/wagtail_live wagtail_live_interface tests setup.py

test:
	pytest

docs:
	mkdocs serve -a 127.0.0.1:8080
