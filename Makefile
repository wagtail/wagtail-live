.PHONY: docs

default: clean

clean:
	find . -name '*.pyc' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.egg-info' -exec rm -rf {} +

format:
	isort wagtail_live wagtail_live_interface tests setup.py
	black wagtail_live wagtail_live_interface tests setup.py
	flake8 wagtail_live wagtail_live_interface tests setup.py

lint:
	isort --check-only --diff wagtail_live wagtail_live_interface tests setup.py
	black --check --diff wagtail_live wagtail_live_interface tests setup.py
	flake8 wagtail_live wagtail_live_interface tests setup.py

test:
	pytest

docs:
	mkdocs serve -a 127.0.0.1:8080
