include Makefile.config
-include Makefile.custom.config
.SILENT:

make-p:
	# Launch all P targets in parallel and exit as soon as one exits.
	set -m; (for p in $(P); do ($(MAKE) $$p || kill 0)& done; wait)

clean-install:
	rm -fr $(NODE_MODULES)
	rm -fr $(VENV)

init-db:
	$(FLASK) drop_db
	$(FLASK) db upgrade --directory $(MIGRATIONS)
	$(FLASK) init_data

install: install-client install-python

install-client:
	$(NPM) install

install-python:
	test -d $(VENV) || virtualenv $(VENV) -p $(PYTHON_VERSION)
	$(PIP) install -r $(REQUIREMENTS)

lint-all: lint-python lint-react

lint-python:
	$(PYTEST) --flake8 --isort -m "flake8 or isort" fittrackee_api --ignore=fittrackee_api/migrations

lint-react:
	$(NPM) lint

migrate-db:
	$(FLASK) db migrate --directory $(MIGRATIONS)

serve-python:
	$(FLASK) run --with-threads -h $(HOST) -p $(API_PORT)

serve-react:
	$(NPM) start

serve:
	$(MAKE) P="serve-react serve-python" make-p

test-e2e: init-db
	$(NPM) test

test-python:
	$(PYTEST) fittrackee_api --cov-config .coveragerc --cov=fittrackee_api --cov-report term-missing

test-python-xml:
	$(PYTEST) fittrackee_api --cov-config .coveragerc --cov=fittrackee_api --cov-report xml

update-cov:	test-python-xml
	$(COV) -r coverage.xml

upgrade-db:
	$(FLASK) db upgrade --directory $(MIGRATIONS)
