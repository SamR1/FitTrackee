include Makefile.config
-include Makefile.custom.config
.SILENT:

make-p:
	# Launch all P targets in parallel and exit as soon as one exits.
	set -m; (for p in $(P); do ($(MAKE) $$p || kill 0)& done; wait)

build-client:
	$(NPM) build

clean-install:
	rm -fr $(NODE_MODULES)
	rm -fr $(VENV)

install-db:
	psql -U postgres -f fittrackee_api/db/create.sql
	$(FLASK) db upgrade --directory $(MIGRATIONS)
	$(FLASK) initdata

init-db:
	$(FLASK) drop-db
	$(FLASK) db upgrade --directory $(MIGRATIONS)
	$(FLASK) initdata

install: install-client install-python

install-client:
	$(NPM) install --prod

install-client-dev:
	$(NPM) install

install-dev: install-client-dev install-python-dev

install-python: venv
	$(PIPENV) install --deploy

install-python-dev: venv
	$(PIPENV) install --dev

lint-all: lint-python lint-react

lint-python:
	$(PYTEST) --flake8 --isort -m "flake8 or isort" fittrackee_api --ignore=fittrackee_api/migrations

lint-react:
	$(NPM) lint

migrate-db:
	$(FLASK) db migrate --directory $(MIGRATIONS)

recalculate:
	$(FLASK) recalculate

run:
	$(MAKE) P="run-server run-client" make-p

run-client:
	serve -s fittrackee_client/build -l 3000 >> serve.log  2>&1

run-server:
	cd fittrackee_api && $(GUNICORN) -b 127.0.0.1:5000 "fittrackee_api:create_app()" --error-logfile ../gunicorn-error.log

serve-python:
	$(FLASK) run --with-threads -h $(HOST) -p $(API_PORT)

serve-react:
	$(NPM) start

serve:
	$(MAKE) P="serve-react serve-python" make-p

test-e2e: init-db
	$(NPM) test

test-python:
	$(PYTEST) fittrackee_api --cov-config .coveragerc --cov=fittrackee_api --cov-report term-missing $(PYTEST_ARGS)

test-python-xml:
	$(PYTEST) fittrackee_api --cov-config .coveragerc --cov=fittrackee_api --cov-report xml

update-cov:	test-python-xml
	$(COV) -r coverage.xml

upgrade-db:
	$(FLASK) db upgrade --directory $(MIGRATIONS)

venv:
	test -d $(VENV) || pipenv --python $(PYTHON_VERSION)
