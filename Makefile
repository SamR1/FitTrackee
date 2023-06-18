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
docker-bandit:
	docker-compose -f docker-compose-dev.yml exec fittrackee $(DOCKER_BANDIT) -r fittrackee -c pyproject.toml

docker-build:
	docker-compose -f docker-compose-dev.yml build fittrackee

docker-build-all: docker-build docker-build-client

docker-build-client:
	docker-compose -f docker-compose-dev.yml build fittrackee_client

docker-check-all: docker-bandit docker-lint-all docker-type-check docker-test-client docker-test-python

docker-downgrade-db:
	docker-compose -f docker-compose-dev.yml exec fittrackee $(DOCKER_FLASK) db downgrade --directory $(DOCKER_MIGRATIONS)

docker-init: docker-run docker-init-db docker-restart docker-run-workers

docker-init-db:
	docker-compose -f docker-compose-dev.yml exec fittrackee docker/init-database.sh

docker-lint-all: docker-lint-client docker-lint-python

docker-lint-client:
	docker-compose -f docker-compose-dev.yml up -d fittrackee_client
	docker-compose -f docker-compose-dev.yml exec fittrackee_client yarn lint

docker-lint-python: docker-run
	docker-compose -f docker-compose-dev.yml exec fittrackee docker/lint-python.sh

docker-logs:
	docker-compose -f docker-compose-dev.yml logs --follow

docker-migrate-db:
	docker-compose -f docker-compose-dev.yml exec fittrackee $(DOCKER_FLASK) db migrate --directory $(DOCKER_MIGRATIONS)

docker-rebuild:
	docker-compose -f docker-compose-dev.yml build --no-cache

docker-restart:
	docker-compose -f docker-compose-dev.yml restart fittrackee
	docker-compose -f docker-compose-dev.yml exec -d fittrackee docker/run-workers.sh

docker-revision:
	docker-compose -f docker-compose-dev.yml exec fittrackee $(DOCKER_FLASK) db revision --directory $(DOCKER_MIGRATIONS) --message $(MIGRATION_MESSAGE)

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

docker-type-check:
	echo 'Running mypy in docker...'
	docker-compose -f docker-compose-dev.yml exec fittrackee $(DOCKER_MYPY) fittrackee

docker-up:
	docker-compose -f docker-compose-dev.yml up fittrackee

docker-upgrade-db:
	docker-compose -f docker-compose-dev.yml exec fittrackee $(DOCKER_FTCLI) db upgrade

downgrade-db:
	$(FLASK) db downgrade --directory $(MIGRATIONS)

gettext:
	$(SPHINXBUILD) -M gettext "$(SOURCEDIR)" "$(DOCSRC)"

LANGUAGE := en
html:
	rm -rf $(BUILDDIR)/$(LANGUAGE)
	rm -rf docs/$(LANGUAGE)/*
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)/$(LANGUAGE)" -D language=$(LANGUAGE)
	cp -a $(BUILDDIR)/$(LANGUAGE)/html/. docs/$(LANGUAGE)

html-all:
	for language in en fr ; do \
		echo -e "\r\nGenerating documentation for '$$language'...\r\n" ; \
		$(MAKE) html LANGUAGE=$$language ; \
	done

html-update:
	$(SPHINXINTL) update -p "$(GETTEXT)" -d "$(LOCALES_DIRS)" -l $(LANGUAGE)

html-update-all:
	for language in en fr ; do \
		echo -e "\r\nUpdating .po files for '$$language'...\r\n" ; \
		$(MAKE) html-update LANGUAGE=$$language ; \
	done

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
	$(PYTEST) --isort --black -m "isort or black" fittrackee e2e --ignore=fittrackee/migrations
	echo 'Running flake8...'
	$(FLAKE8) fittrackee e2e

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
    # for dev environments
	$(MAKE) P="serve-client serve-python" make-p

serve-dev:
    # for dev environments
	$(MAKE) P="serve-client serve-python-dev" make-p

serve-client:
    # for dev environments
	cd fittrackee_client && PORT=3000 $(NPM) serve

serve-python:
    # for dev environments
	echo 'Running on http://$(HOST):$(PORT)'
	$(FLASK) run --with-threads -h $(HOST) -p $(PORT)

serve-python-dev:
    # for dev environments (
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
	# for tests parallelization: 4 workers max.
	# make test-python PYTEST_ARGS="-p no:warnings -n auto --maxprocesses=4"
	$(PYTEST) fittrackee --cov-config .coveragerc --cov=fittrackee --cov-report term-missing $(PYTEST_ARGS)

test-client:
	cd fittrackee_client && $(NPM) test:unit $(MOCHA_ARGS)

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
