.PHONY: docs

default: clean

clean:
	find . -name '*.pyc' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.egg-info' -exec rm -rf {} +

format:
	isort wagtail_live tests setup.py
	black wagtail_live tests setup.py
	flake8 wagtail_live tests setup.py

lint:
	isort --check-only --diff wagtail_live tests setup.py
	black --check --diff wagtail_live tests setup.py
	flake8 wagtail_live tests setup.py

test:
	pytest

docs:
	mkdocs serve -a 127.0.0.1:8080

showcov:
	@echo "http://127.0.0.1:9000"
	python -m http.server --directory htmlcov 9000
