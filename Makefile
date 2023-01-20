PROJECT_NAME=zpl_image_extractor

.PHONY: clean-pyc

clean-eggs:
	@find . -name '*.egg' -print0|xargs -0 rm -rf --
	@rm -rf .eggs/

clean-pyc:
	@find . -iname '*.py[co]' -delete
	@find . -iname '__pycache__' -delete
	@find . -iname '.coverage' -delete
	@rm -rf htmlcov/

pre-clean: clean-eggs clean-pyc
	@find . -iname '*~' -delete
	@find . -iname '*.swp' -delete
	@find . -iname '__pycache__' -delete

post-clean:
	@rm -rf build/
	@rm $(PROJECT_NAME).spec
	@rm dist/$(PROJECT_NAME)

test:
	poetry run pytest -vv tests

test-cov:
	poetry run pytest -vv --cov=loafer tests

cov:
	poetry run coverage report -m

cov-report:
	poetry run pytest -vv --cov=loafer --cov-report=html tests

check-fixtures:
	poetry run pytest --dead-fixtures

changelog-preview:
	@echo "\nmain ("$$(date '+%Y-%m-%d')")"
	@echo "-------------------\n"
	@git log $$(poetry version -s)...main --oneline --reverse


version = `cat CHANGES.rst | awk '/^[0-9]+\.[0-9]+(\.[0-9]+)?/' | head -n1`
bump_version:
	poetry version $(version)

bump_binary: bump_version pre-clean
	pyinstaller --onefile --name $(PROJECT_NAME) $(PROJECT_NAME)/cli.py
	@tar -C dist/ -czf dist/$(PROJECT_NAME).$(version).tar.gz $(PROJECT_NAME)
	@make post-clean
