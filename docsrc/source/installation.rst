Installation
############

This application is written in Python (API) and Typescript (client):

- API:
    - Flask
    - `gpxpy <https://github.com/tkrajina/gpxpy>`_ to parse gpx files
    - `staticmap <https://github.com/komoot/staticmap>`_ to generate a static map image from gpx coordinates
    - `python-forecast.io <https://github.com/ZeevG/python-forecast.io>`_ to fetch weather data from `Dark Sky <https://darksky.net>`__ (former forecast.io)
    - `dramatiq <https://flask-dramatiq.readthedocs.io/en/latest/>`_ for task queue
- Client:
    - Vue3/Vuex
    - `Leaflet <https://leafletjs.com/>`__ to display map
    - `Chart.js <https://www.chartjs.org/>`__ to display charts with elevation and speed

| Logo, some sports and weather icons are made by `Freepik <https://www.freepik.com/>`__ from `www.flaticon.com <https://www.flaticon.com/>`__.
| FitTrackee also uses icons from `Fork Awesome <https://forkaweso.me>`__.

Prerequisites
~~~~~~~~~~~~~

-  Python 3.7+
-  PostgreSQL database (10+)
-  SMTP provider and Redis for task queue (if email sending is enabled)
-  API key from `Dark Sky <https://darksky.net/dev>`__ (not mandatory)
-  `Poetry <https://poetry.eustace.io>`__ (for installation from sources only)
-  `Yarn <https://yarnpkg.com>`__ (for development only)
-  Docker and Docker Compose (for development or evaluation purposes)

.. note::
    | The following steps describe an installation on Linux systems (tested
      on Debian and Arch).
    | On other OS, some issues can be encountered and adaptations may be
      necessary.


Environment variables
~~~~~~~~~~~~~~~~~~~~~

.. warning::
    | Since FitTrackee 0.4.0, ``Makefile.custom.config`` is replaced by ``.env``

The following environment variables are used by **FitTrackee** web application
or the task processing library. They are not all mandatory depending on
deployment method.

.. envvar:: FLASK_APP

    | Name of the module to import at flask run.
    | ``FLASK_APP`` should contain ``$(PWD)/fittrackee/__main__.py`` with installation from sources, else ``fittrackee``.


.. envvar:: HOST

    **FitTrackee** host.

    :default: 0.0.0.0


.. envvar:: PORT

    **FitTrackee** port.

    :default: 5000


.. envvar:: APP_SETTINGS

    **FitTrackee** configuration.

    :default: fittrackee.config.ProductionConfig


.. envvar:: APP_SECRET_KEY

    **FitTrackee** secret key, must be initialized in production environment.


.. envvar:: APP_WORKERS

    Number of workers spawned by **Gunicorn**.

    :default: 1


.. envvar:: APP_LOG

    .. versionadded:: 0.4.0

    Path to log file


.. envvar:: UPLOAD_FOLDER

    .. versionadded:: 0.4.0

    Directory containing uploaded files.

    :default: `fittrackee/uploads/`

    .. danger::
        | With installation from PyPI, the directory will be located in
          **virtualenv** directory if the variable is not initialized.

.. envvar:: DATABASE_URL

    | Database URL with username and password, must be initialized in production environment.
    | For example in dev environment : ``postgresql://fittrackee:fittrackee@localhost:5432/fittrackee``

    .. warning::
        | Since `SQLAlchemy update (1.4+) <https://docs.sqlalchemy.org/en/14/changelog/changelog_14.html#change-3687655465c25a39b968b4f5f6e9170b>`__,
          engine URL should begin with `postgresql://`.

.. envvar:: DATABASE_DISABLE_POOLING

    .. versionadded:: 0.4.0

    Disable pooling if needed (when starting application with **FitTrackee** entry point and not directly with **Gunicorn**),
    see `SqlAlchemy documentation <https://docs.sqlalchemy.org/en/13/core/pooling.html#using-connection-pools-with-multiprocessing-or-os-fork>`__.

    :default: false

.. envvar:: UI_URL

    **FitTrackee** URL, needed for links in emails.


.. envvar:: EMAIL_URL

    .. versionadded:: 0.3.0

    Email URL with credentials, see `Emails <installation.html#emails>`__.

    .. versionchanged:: 0.6.5

    :default: empty string

    .. danger::
        If the email URL is empty, email sending will be disabled.

    .. warning::
        If the email URL is invalid, the application may not start.

.. envvar:: SENDER_EMAIL

    .. versionadded:: 0.3.0

    **FitTrackee** sender email address.


.. envvar:: REDIS_URL

    .. versionadded:: 0.3.0

    Redis instance used by **Dramatiq**.

    :default: local Redis instance (``redis://``)


.. envvar:: WORKERS_PROCESSES

    .. versionadded:: 0.3.0

    Number of processes used by **Dramatiq**.


.. envvar:: TILE_SERVER_URL

    .. versionadded:: 0.4.0

    | Tile server URL (with api key if needed), see `Map tile server <installation.html#map-tile-server>`__.
    | Since **0.4.9**, it's also used to generate static maps (to keep default server, see `DEFAULT_STATICMAP <installation.html#envvar-DEFAULT_STATICMAP>`__)

    :default: `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`


.. envvar:: MAP_ATTRIBUTION

    .. versionadded:: 0.4.0

    Map attribution (if using another tile server), see `Map tile server <installation.html#map-tile-server>`__.

    :default: `&copy; <a href="http://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors`


.. envvar:: DEFAULT_STATICMAP 🆕

    .. versionadded:: 0.4.9

    If `True`, it keeps using default tile server to generate static maps.

    :default: False


.. envvar:: WEATHER_API_KEY

    .. versionchanged:: 0.4.0 ⚠️ replaces ``WEATHER_API``

    **Dark Sky** API key for weather data (not mandatory).


.. envvar:: VUE_APP_API_URL

    **FitTrackee** API URL, only needed in dev environment.



Emails
^^^^^^
.. versionadded:: 0.3.0

To send emails, a valid ``EMAIL_URL`` must be provided:

- with an unencrypted SMTP server: ``smtp://username:password@smtp.example.com:25``
- with SSL: ``smtp://username:password@smtp.example.com:465/?ssl=True``
- with STARTTLS: ``smtp://username:password@smtp.example.com:587/?tls=True``

.. warning::
    | - If the email URL is invalid, the application may not start.
    | - Sending emails with Office365 may not work if SMTP auth is disabled.

.. versionchanged:: 0.5.3

| Credentials can be omitted: ``smtp://smtp.example.com:25``.
| If ``:<port>`` is omitted, the port defaults to 25.

.. warning::
     | Since 0.6.0, newly created accounts must be confirmed (an email with confirmation instructions is sent after registration).

Emails sent by FitTrackee are:

- account confirmation instructions
- password reset request
- email change (to old and new email adresses)
- password change

.. versionchanged:: 0.6.5

| For single-user instance, it is possible to disable email sending with an empty ``EMAIL_URL`` (in this case, no need to start dramatiq workers).
| A `CLI <cli.html#ftcli-users-update>`__ is available to activate account and modify email and password.


Map tile server
^^^^^^^^^^^^^^^
.. versionadded:: 0.4.0

Default tile server is now **OpenStreetMap**'s standard tile layer (if environment variables are not initialized).
The tile server can be changed by updating ``TILE_SERVER_URL`` and ``MAP_ATTRIBUTION`` variables (`list of tile servers <https://wiki.openstreetmap.org/wiki/Tile_servers>`__).

To keep using **ThunderForest Outdoors**, the configuration is:

- ``TILE_SERVER_URL=https://{s}.tile.thunderforest.com/outdoors/{z}/{x}/{y}.png?apikey=XXXX`` where **XXXX** is **ThunderForest** API key
- ``MAP_ATTRIBUTION=&copy; <a href="http://www.thunderforest.com/">Thunderforest</a>, &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors``

.. note::
    | Check the terms of service of tile provider for map attribution

Installation
~~~~~~~~~~~~

.. warning::
    | Note that FitTrackee is under heavy development, some features may be unstable.

From PyPI
^^^^^^^^^

.. note::
    | Recommended way on production.

- Create and activate a virtualenv

- Install **FitTrackee** with pip

.. code-block:: bash

    $ pip install fittrackee

- Create ``fittrackee`` database

Example :

.. code-block:: sql

    CREATE DATABASE fittrackee;
    CREATE USER fittrackee WITH PASSWORD '<PASSWORD>';
    GRANT ALL PRIVILEGES ON DATABASE fittrackee TO fittrackee;

- Initialize environment variables, see `Environment variables <installation.html#environment-variables>`__

For instance, copy and update ``.env`` file from ``.env.example`` and source the file.

.. code-block:: bash

    $ nano .env
    $ source .env

- Initialize database schema

.. code-block:: bash

    $ ftcli db upgrade

- Start the application

.. code-block:: bash

    $ fittrackee

- Start task queue workers if email sending is enabled.

.. code-block:: bash

    $ fittrackee_worker --processes 2

.. note::
    | To start application and workers with **systemd** service, see `Deployment <installation.html#deployment>`__

- Open http://localhost:3000 and register

- To set admin rights to the newly created account, use the following command line:

.. code:: bash

   $ ftcli users update <username> --set-admin true

.. note::
    If the user account is inactive, it activates it.

From sources
^^^^^^^^^^^^

.. warning::
    | Since FitTrackee 0.2.1, Python packages installation needs Poetry.
    | To install it on ArchLinux:

    .. code-block:: bash

        $ yay poetry
        $ poetry --version
        Poetry 1.0.17

        # optional
        $ poetry config virtualenvs.in-project true

    For other OS, see `Poetry Documentation <https://python-poetry.org/docs/#installation>`__

Dev environment
"""""""""""""""

-  Clone this repo:

.. code:: bash

   $ git clone https://github.com/SamR1/FitTrackee.git
   $ cd FitTrackee

-  Create **.env** from example and update it
   (see `Environment variables <installation.html#environment-variables>`__).

-  Install Python virtualenv, Vue and all related packages and
   initialize the database:

.. code:: bash

   $ make install-dev
   $ make install-db

-  Start the server and the client:

.. code:: bash

   $ make serve

-  Run dramatiq workers:

.. code:: bash

   $ make run-workers

- Open http://localhost:3000 and register

- To set admin rights to the newly created account, use the following command line:

.. code:: bash

   $ make user-set-admin USERNAME=<username>

.. note::
    If the user account is inactive, it activates it.

Production environment
""""""""""""""""""""""

.. warning::
    | Note that FitTrackee is under heavy development, some features may be unstable.

-  Download the last release (for now, it is the release v0.6.8):

.. code:: bash

   $ wget https://github.com/SamR1/FitTrackee/archive/v0.6.8.tar.gz
   $ tar -xzf v0.6.8.tar.gz
   $ mv FitTrackee-0.6.8 FitTrackee
   $ cd FitTrackee

-  Create **.env** from example and update it
   (see `Environment variables <installation.html#environment-variables>`__).

-  Install Python virtualenv and all related packages:

.. code:: bash

   $ make install-python

-  Initialize the database (**after updating** ``db/create.sql`` **to change
   database credentials**):

.. code:: bash

   $ make install-db

-  Start the server and dramatiq workers:

.. code:: bash

   $ make run

.. note::
    If email sending is disabled: ``$ make run-server``

- Open http://localhost:5000 and register

- To set admin rights to the newly created account, use the following command line:

.. code:: bash

   $ make user-set-admin USERNAME=<username>

.. note::
    If the user account is inactive, it activates it.

Upgrade
~~~~~~~

.. warning::
    | Before upgrading, make a backup of all data:
    | - database (with `pg_dump <https://www.postgresql.org/docs/11/app-pgdump.html>`__ for instance)
    | - upload directory (see `Environment variables <installation.html#environment-variables>`__)


From PyPI
^^^^^^^^^

- Stop the application and activate the virtualenv

- Upgrade with pip

.. code-block:: bash

    $ pip install -U fittrackee

- Update environment variables if needed and source environment variables file

.. code-block:: bash

    $ nano .env
    $ source .env

- Upgrade database if needed (see changelog for migrations):

.. code-block:: bash

    $ ftcli db upgrade

- Restart the application and task queue workers (if email sending is enabled).


From sources
^^^^^^^^^^^^

Dev environment
"""""""""""""""

- Stop the application and pull the repository:

.. code:: bash

   $ git pull

- Update **.env** if needed (see `Environment variables <installation.html#environment-variables>`__).

- Upgrade packages:

.. code:: bash

   $ make install-dev

- Upgrade database if needed (see changelog for migrations):

.. code:: bash

   $ make upgrade-db

- Restart the server:

.. code:: bash

   $ make serve

-  Run dramatiq workers:

.. code:: bash

   $ make run-workers

Prod environment
""""""""""""""""

- Stop the application

- Change to the directory where FitTrackee directory is located

- Download the last release (for now, it is the release v0.6.8) and overwrite existing files:

.. code:: bash

   $ wget https://github.com/SamR1/FitTrackee/archive/v0.6.8.tar.gz
   $ tar -xzf v0.6.8.tar.gz
   $ cp -R FitTrackee-0.6.8/* FitTrackee/
   $ cd FitTrackee

- Update **.env** if needed (see `Environment variables <installation.html#environment-variables>`__).

- Upgrade packages:

.. code:: bash

   $ make install-dev

- Upgrade database if needed (see changelog for migrations):

.. code:: bash

   $ make upgrade-db

- Restart the server and dramatiq workers:

.. code:: bash

   $ make run

.. note::
    If email sending is disabled: ``$ make run-server``

Deployment
~~~~~~~~~~

There are several ways to start **FitTrackee** web application and task queue
library.
One way is to use a **systemd** services and **Nginx** to proxy pass to **Gunicorn**.

Examples (to update depending on your application configuration and given distribution):

- for application: ``fittrackee.service``

.. code-block::

    [Unit]
    Description=FitTrackee service
    After=network.target
    After=postgresql.service
    After=redis.service
    StartLimitIntervalSec=0

    [Service]
    Type=simple
    Restart=always
    RestartSec=1
    User=<USER>
    StandardOutput=syslog
    StandardError=syslog
    SyslogIdentifier=fittrackee
    Environment="APP_SECRET_KEY="
    Environment="APP_LOG="
    Environment="UPLOAD_FOLDER="
    Environment="DATABASE_URL="
    Environment="UI_URL="
    Environment="EMAIL_URL="
    Environment="SENDER_EMAIL="
    Environment="REDIS_URL="
    Environment="TILE_SERVER_URL="
    Environment="MAP_ATTRIBUTION="
    Environment="WEATHER_API_KEY="
    WorkingDirectory=/home/<USER>/<FITTRACKEE DIRECTORY>
    ExecStart=/home/<USER>/<FITTRACKEE DIRECTORY>/.venv/bin/gunicorn -b 127.0.0.1:5000 "fittrackee:create_app()" --error-logfile /home/<USER>/<FITTRACKEE DIRECTORY>/gunicorn.log
    Restart=always

    [Install]
    WantedBy=multi-user.target

.. note::
    More information on `Gunicorn documentation <https://docs.gunicorn.org/en/stable/deploy.html>`__

- for task queue workers: ``fittrackee_workers.service``

.. code-block::

    [Unit]
    Description=FitTrackee task queue service
    After=network.target
    After=postgresql.service
    After=redis.service
    StartLimitIntervalSec=0

    [Service]
    Type=simple
    Restart=always
    RestartSec=1
    User=<USER>
    StandardOutput=syslog
    StandardError=syslog
    SyslogIdentifier=fittrackee_workers
    Environment="FLASK_APP=fittrackee"
    Environment="APP_SECRET_KEY="
    Environment="APP_LOG="
    Environment="UPLOAD_FOLDER="
    Environment="DATABASE_URL="
    Environment="UI_URL="
    Environment="EMAIL_URL="
    Environment="SENDER_EMAIL="
    Environment="REDIS_URL="
    WorkingDirectory=/home/<USER>/<FITTRACKEE DIRECTORY>
    ExecStart=/home/<USER>/<FITTRACKEE DIRECTORY>/.venv/bin/flask worker --processes <NUMBER OF PROCESSES>
    Restart=always

    [Install]
    WantedBy=multi-user.target

- **Nginx** configuration:

.. code-block::

    server {
        listen 443 ssl http2;
        server_name example.com;
        ssl_certificate fullchain.pem;
        ssl_certificate_key privkey.pem;

        location / {
            proxy_pass http://127.0.0.1:5000;
            proxy_redirect    default;
            proxy_set_header  Host $host;
            proxy_set_header  X-Real-IP $remote_addr;
            proxy_set_header  X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header  X-Forwarded-Host $server_name;
        }
    }

    server {
        listen 80;
        server_name example.com;
        location / {
            return 301 https://example.com$request_uri;
        }
    }

.. note::
    If needed, update configuration to handle larger files (see `client_max_body_size <https://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size>`_).


Docker
~~~~~~

Installation
^^^^^^^^^^^^

.. versionadded:: 0.4.4

For evaluation purposes, docker files are available, installing **FitTrackee** from **sources**.

- To install **FitTrackee** with database initialisation and run the application and dramatiq workers:

.. code-block:: bash

    $ git clone https://github.com/SamR1/FitTrackee.git
    $ cd FitTrackee
    $ cp .env.docker .env
    $ make docker-build docker-run docker-init

Open http://localhost:5000 and register.

Open http://localhost:8025 to access `MailHog interface <https://github.com/mailhog/MailHog>`_ (email testing tool)

- To set admin rights to the newly created account, use the following command line:

.. code:: bash

   $ make docker-set-admin USERNAME=<username>

.. note::
    If the user account is inactive, it activates it.

- To stop **Fittrackee**:

.. code-block:: bash

    $ make docker-stop

- To start **Fittrackee** (application and dramatiq workers):

.. code-block:: bash

    $ make docker-run-all


- To run shell inside **Fittrackee** container:

.. code-block:: bash

    $ make docker-shell


Development
^^^^^^^^^^^

.. versionadded:: 0.5.0

- an additional step is needed to install `fittrackee_client`

.. code-block:: bash

    $ make docker-build-client

- to start **FitTrackee** with client dev tools:

.. code-block:: bash

    $ make docker-serve-client

Open http://localhost:3000

.. note::
    Some environment variables need to be updated like `UI_URL`