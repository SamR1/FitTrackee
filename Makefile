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
	psql -U postgres -f fittrackee_api/db/create.sql
	$(FLASK) db upgrade --directory $(MIGRATIONS)
	$(FLASK) initdata

init-app-config:
	$(FLASK) init-app-config

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

install-python:
	$(POETRY) install --no-dev

install-python-dev:
	$(POETRY) install

lint-all: lint-python lint-react

lint-all-fix: lint-python-fix lint-react-fix

lint-python:
	$(PYTEST) --flake8 --isort --black -m "flake8 or isort or black" fittrackee_api --ignore=fittrackee_api/migrations

lint-python-fix:
	$(BLACK) fittrackee_api

lint-react:
	$(NPM) lint

lint-react-fix:
	$(NPM) lint-fix

mail:
	docker run -d -e "MH_STORAGE=maildir" -v /tmp/maildir:/maildir -p 1025:1025 -p 8025:8025 mailhog/mailhog

migrate-db:
	$(FLASK) db migrate --directory $(MIGRATIONS)

recalculate:
	$(FLASK) recalculate

run:
	$(MAKE) P="run-server run-workers run-client" make-p

run-client:
	serve -s fittrackee_client/build -l 3000 >> serve.log  2>&1

run-server:
	cd fittrackee_api && $(GUNICORN) -b 127.0.0.1:5000 "fittrackee_api:create_app()" --error-logfile ../gunicorn.log

run-workers:
	$(FLASK) worker --processes=$(WORKERS_PROCESSES) >> dramatiq.log  2>&1

serve-python:
	$(FLASK) run --with-threads -h $(HOST) -p $(API_PORT)

serve-python-dev:
	$(FLASK) run --with-threads -h $(HOST) -p $(API_PORT) --cert=adhoc

serve-react:
	$(NPM) start

serve:
	$(MAKE) P="serve-react serve-python" make-p

serve-dev:
	$(MAKE) P="serve-react serve-python-dev" make-p

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
