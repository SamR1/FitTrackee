include Makefile.config
-include .env
.SILENT:

make-p:
	# Launch all P targets in parallel and exit as soon as one exits.
	set -m; (for p in $(P); do ($(MAKE) $$p || kill 0)& done; wait)

babel-extract:
	$(PYBABEL) extract -F babel.cfg -k lazy_gettext -o messages.pot .

babel-init:
	$(PYBABEL) init -i messages.pot -d fittrackee/emails/translations -l $(LANG)

babel-compile:
	$(PYBABEL) compile -d fittrackee/emails/translations

babel-update:
	$(PYBABEL) update -i messages.pot -d fittrackee/emails/translations

bandit:
	$(BANDIT) -r fittrackee -c pyproject.toml

build-client: lint-client
	cd fittrackee_client && $(NPM) build

check-all: bandit lint-all type-check test-all

check-client: lint-client test-client

check-python: bandit lint-python type-check test-python

clean:
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf e2e/.pytest_cache

clean-install: clean
	rm -fr $(NODE_MODULES)
	rm -fr $(VENV)
	rm -rf *.egg-info
	rm -rf dist/

## Docker commands for evaluation purposes
docker-build:
	docker-compose -f docker-compose-dev.yml build fittrackee

docker-build-all: docker-build docker-build-client

docker-build-client:
	docker-compose -f docker-compose-dev.yml build fittrackee_client

docker-init: docker-run docker-init-db docker-restart docker-run-workers

docker-init-db:
	docker-compose -f docker-compose-dev.yml exec fittrackee docker/init-database.sh

docker-lint-client:
	docker-compose -f docker-compose-dev.yml up -d fittrackee_client
	docker-compose -f docker-compose-dev.yml exec fittrackee_client yarn lint

docker-lint-python: docker-run
	docker-compose -f docker-compose-dev.yml exec fittrackee docker/lint-python.sh

docker-logs:
	docker-compose -f docker-compose-dev.yml logs --follow

docker-rebuild:
	docker-compose -f docker-compose-dev.yml build --no-cache

docker-restart:
	docker-compose -f docker-compose-dev.yml restart fittrackee

docker-run-all: docker-run docker-run-workers

docker-run:
	docker-compose -f docker-compose-dev.yml up -d fittrackee

docker-run-workers:
	docker-compose -f docker-compose-dev.yml exec -d fittrackee docker/run-workers.sh

docker-serve-client:
	docker-compose -f docker-compose-dev.yml up -d fittrackee_client
	docker-compose -f docker-compose-dev.yml exec fittrackee_client yarn serve

docker-set-admin:
	docker-compose -f docker-compose-dev.yml exec fittrackee docker/set-admin.sh $(USERNAME)

docker-shell:
	docker-compose -f docker-compose-dev.yml exec fittrackee docker/shell.sh

docker-stop:
	docker-compose -f docker-compose-dev.yml stop

docker-test-client:
	docker-compose -f docker-compose-dev.yml up -d fittrackee_client
	docker-compose -f docker-compose-dev.yml exec fittrackee_client yarn test:unit

# needs a running application
docker-test-e2e: docker-run
	docker-compose -f docker-compose-dev.yml up -d selenium
	docker-compose -f docker-compose-dev.yml exec fittrackee docker/test-e2e.sh $(PYTEST_ARGS)

docker-test-python: docker-run
	docker-compose -f docker-compose-dev.yml exec fittrackee docker/test-python.sh $(PYTEST_ARGS)

docker-up:
	docker-compose -f docker-compose-dev.yml up fittrackee

downgrade-db:
	$(FLASK) db downgrade --directory $(MIGRATIONS)

html:
	rm -rf docsrc/build
	rm -rf docs/*
	touch docs/.nojekyll
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	rm -rf docsrc/build/html/_static/bootstrap-2.3.2
	rm -rf docsrc/build/html/_static/bootswatch-2.3.2
	find docsrc/build/html/_static/bootswatch-3.4.1/. -maxdepth 1 -not -name flatly -not -name fonts -exec rm -rf '{}' \; 2>/tmp/NULL
	sed -i "s/\@import url(\"https:\/\/fonts.googleapis.com\/css?family=Lato:400,700,400italic\");//" docsrc/build/html/_static/bootswatch-3.4.1/flatly/bootstrap.min.css
	cp -a docsrc/build/html/. docs

install-db:
	psql -U postgres -f db/create.sql
	$(FTCLI) db upgrade

init-db:
	$(FTCLI) db drop
	$(FTCLI) db upgrade

install: install-client install-python

install-client:
	# NPM_ARGS="--ignore-engines", if errors with Node latest version
	cd fittrackee_client && $(NPM) install --prod $(NPM_ARGS)

install-client-dev:
	# NPM_ARGS="--ignore-engines", if errors with Node latest version
	cd fittrackee_client && $(NPM) install $(NPM_ARGS)

install-dev: install-client-dev install-python-dev

install-python:
	$(POETRY) install --no-dev

install-python-dev:
	$(POETRY) install

lint-all: lint-python lint-client

lint-all-fix: lint-python-fix lint-client-fix

lint-client:
	cd fittrackee_client && $(NPM) lint

lint-client-fix:
	cd fittrackee_client && $(NPM) lint-fix

lint-python:
	$(PYTEST) --flake8 --isort --black -m "flake8 or isort or black" fittrackee e2e --ignore=fittrackee/migrations

lint-python-fix:
	$(BLACK) fittrackee e2e

mail:
	docker run -d -e "MH_STORAGE=maildir" -v /tmp/maildir:/maildir -p 1025:1025 -p 8025:8025 mailhog/mailhog

migrate-db:
	$(FLASK) db migrate --directory $(MIGRATIONS)

revision:
	$(FLASK) db revision --directory $(MIGRATIONS) --message $(MIGRATION_MESSAGE)

run:
	$(MAKE) P="run-server run-workers" make-p

run-server:
	echo 'Running on http://$(HOST):$(PORT)'
	cd fittrackee && $(GUNICORN) -b $(HOST):$(PORT) "fittrackee:create_app()" --error-logfile ../gunicorn.log

run-workers:
	$(FLASK) worker --processes=$(WORKERS_PROCESSES) >> dramatiq.log  2>&1

serve:
	$(MAKE) P="serve-client serve-python" make-p

serve-dev:
	$(MAKE) P="serve-client serve-python-dev" make-p

serve-client:
	cd fittrackee_client && PORT=3000 $(NPM) serve

serve-python:
	echo 'Running on http://$(HOST):$(PORT)'
	$(FLASK) run --with-threads -h $(HOST) -p $(PORT)

serve-python-dev:
	echo 'Running on https://$(HOST):$(PORT)'
	$(FLASK) run --with-threads -h $(HOST) -p $(PORT) --cert=adhoc

set-admin:
	echo "Deprecated command, will be removed in a next version. Use 'user-set-admin' instead."
	$(FTCLI) users update $(USERNAME) --set-admin true

test-all: test-client test-python

test-e2e:
	$(PYTEST) e2e --driver firefox $(PYTEST_ARGS)

test-e2e-client:
	E2E_ARGS=client $(PYTEST) e2e --driver firefox $(PYTEST_ARGS)

test-python:
	$(PYTEST) fittrackee --cov-config .coveragerc --cov=fittrackee --cov-report term-missing $(PYTEST_ARGS)

test-client:
	cd fittrackee_client && $(NPM) test:unit

type-check:
	echo 'Running mypy...'
	$(MYPY) fittrackee

upgrade-db:
	$(FTCLI) db upgrade

user-activate:
	$(FTCLI) users update $(USERNAME) --activate

user-reset-password:
	$(FTCLI) users update $(USERNAME) --reset-password

ADMIN := true
user-set-admin:
	$(FTCLI) users update $(USERNAME) --set-admin $(ADMIN)

user-update-email:
	$(FTCLI) users update $(USERNAME) --update-email $(EMAIL)
