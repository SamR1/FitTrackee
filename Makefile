include Makefile.config
-include Makefile.custom.config
.SILENT:

make-p:
	# Launch all P targets in parallel and exit as soon as one exits.
	set -m; (for p in $(P); do ($(MAKE) $$p || kill 0)& done; wait)

init-db:
	$(FLASK) init_db

install: install-client install-python

install-client:
	$(NPM) install

install-python:
	test -d $(VENV) || virtualenv $(VENV) -p $(PYTHON_VERSION)
	$(PIP) install -r $(REQUIREMENTS)

lint-all: lint-python lint-react

lint-python:
	$(PYTEST) --flake8 --isort -m "flake8 or isort" mpwo_api

lint-react:
	$(NPM) lint

serve-python:
	$(FLASK) run --with-threads -h $(HOST) -p $(API_PORT)

serve-react:
	$(NPM) start

serve:
	$(MAKE) P="serve-react serve-python" make-p

test-e2e:
	$(NPM) test

test-python:
	$(FLASK) test_local
