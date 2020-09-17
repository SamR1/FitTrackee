include Makefile.config
-include Makefile.custom.config
.SILENT:

make-p:
	# Launch all P targets in parallel and exit as soon as one exits.
	set -m; (for p in $(P); do ($(MAKE) $$p || kill 0)& done; wait)

build-client: lint-client
	cd fittrackee_client && $(NPM) build

clean-install:
	rm -fr $(NODE_MODULES)
	rm -fr $(VENV)

html:
	rm -rf docsrc/build
	rm -rf docs/*
	touch docs/.nojekyll
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	rm -rf docsrc/build/html/_static/bootstrap-2.3.2
	rm -rf docsrc/build/html/_static/bootswatch-2.3.2
	find docsrc/build/html/_static/bootswatch-3.3.7/. -maxdepth 1 -not -name flatly -not -name fonts -exec rm -rf '{}' \; 2>/tmp/NULL
	sed -i "s/\@import url(\"https:\/\/fonts.googleapis.com\/css?family=Lato:400,700,400italic\");//" docsrc/build/html/_static/bootswatch-3.3.7/flatly/bootstrap.min.css
	cp -a docsrc/build/html/. docs

install-db:
	psql -U postgres -f db/create.sql
	$(FLASK) db upgrade --directory $(MIGRATIONS)
	$(FLASK) init-data

init-app-config:
	$(FLASK) init-app-config

init-db:
	$(FLASK) drop-db
	$(FLASK) db upgrade --directory $(MIGRATIONS)
	$(FLASK) init-data

install: install-client install-python

install-client:
	cd fittrackee_client && $(NPM) install --prod

install-client-dev:
	cd fittrackee_client && $(NPM) install

install-dev: install-client-dev install-python-dev

install-python:
	$(POETRY) install --no-dev

install-python-dev:
	$(POETRY) install

lint-all: lint-python lint-client

lint-all-fix: lint-python-fix lint-client-fix

lint-python:
	$(PYTEST) --flake8 --isort --black -m "flake8 or isort or black" fittrackee e2e --ignore=fittrackee/migrations

lint-python-fix:
	$(BLACK) fittrackee e2e

lint-client:
	cd fittrackee_client && $(NPM) lint

lint-client-fix:
	cd fittrackee_client && $(NPM) lint-fix

mail:
	docker run -d -e "MH_STORAGE=maildir" -v /tmp/maildir:/maildir -p 1025:1025 -p 8025:8025 mailhog/mailhog

migrate-db:
	$(FLASK) db migrate --directory $(MIGRATIONS)

recalculate:
	$(FLASK) recalculate

run:
	$(MAKE) P="run-server run-workers" make-p

run-server:
	cd fittrackee && $(GUNICORN) -b 127.0.0.1:5000 "fittrackee:create_app()" --error-logfile ../gunicorn.log

run-workers:
	$(FLASK) worker --processes=$(WORKERS_PROCESSES) >> dramatiq.log  2>&1

serve-python:
	$(FLASK) run --with-threads -h $(HOST) -p $(API_PORT)

serve-python-dev:
	$(FLASK) run --with-threads -h $(HOST) -p $(API_PORT) --cert=adhoc

serve-client:
	cd fittrackee_client && $(NPM) start

serve:
	$(MAKE) P="serve-client serve-python" make-p

serve-dev:
	$(MAKE) P="serve-client serve-python-dev" make-p

test-e2e: init-db
	$(PYTEST) e2e --driver firefox $(PYTEST_ARGS)

test-e2e-client: init-db
	E2E_ARGS=client $(PYTEST) e2e --driver firefox $(PYTEST_ARGS)

test-python:
	$(PYTEST) fittrackee --cov-config .coveragerc --cov=fittrackee --cov-report term-missing $(PYTEST_ARGS)

upgrade-db:
	$(FLASK) db upgrade --directory $(MIGRATIONS)
