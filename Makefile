.PHONY: test test-md lint cli web

PYTHON ?= python3

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests/unit -p 'test_*.py' -v

test-md:
	PYTHONPATH=src $(PYTHON) -m unittest tests.unit.test_markdown_cases -v

lint:
	$(PYTHON) -m compileall -q src tests

cli:
	PYTHONPATH=src $(PYTHON) -m hustref.cli --source bibtex --input tests/fixtures/sample.bib

web:
	PYTHONPATH=src $(PYTHON) -m hustref.webapp --host 127.0.0.1 --port 8765
