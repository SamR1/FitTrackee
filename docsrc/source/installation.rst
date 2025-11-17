Installation
############

**FitTrackee** can be installed:

- via a single Python package from `PyPI <https://pypi.org/project/fittrackee/>`__,
- from sources,
- with a `Docker <installation.html#docker>`__ image.

Thanks to contributors, packages are also available on `Yunohost <installation.html#yunohost>`__ and `NixOS <installation.html#nixos>`__.

For a single-user instance, registration can be disabled. So all you need is Python and PostgreSQL/PostGIS. A `CLI <cli.html#users>`__ is available to manage user account.

| The following steps describe an installation on Linux systems (tested with ArchLinux-based OS and Ubuntu on CI).
| On other operating systems, some issues can be encountered and adaptations may be necessary.

.. note::
  Other installation guides are available thanks to contributors:

  - `Installation on Uberspace Web hosting <https://lab.uberspace.de/guide_fittrackee/>`__ (Fittrackee 0.7.25)
  - `Installation on Debian 12 net install (guide in German) <https://speefak.spdns.de/oss_lifestyle/fittrackee-installation-unter-debian-12/>`__ (Fittrackee 0.7.31)


Main dependencies
~~~~~~~~~~~~~~~~~
This application is written in Python (API) and Typescript (client):

- API:
    - Flask
    - `SQLAlchemy <https://www.sqlalchemy.org/>`_ and `geoalchemy2 <https://geoalchemy-2.readthedocs.io>`_ to interact with the database
    - `gpxpy <https://github.com/tkrajina/gpxpy>`_ to parse gpx files
    - `fitdecode <https://github.com/polyvertex/fitdecode>`_ to parse fit files
    - `GeoPandas <https://geopandas.org>`_ to work with geospatial data
    - `Static Map 3 <https://github.com/SamR1/staticmap>`_, a fork of `Static Map <https://github.com/komoot/staticmap>`_ to generate a static map image from file coordinates
    - `Dramatiq <https://dramatiq.io/>`_ and `Flask-Dramatiq <https://flask-dramatiq.readthedocs.io>`_ for task queue
    - `Authlib <https://docs.authlib.org/en/latest/>`_ for OAuth 2.0 Authorization support
    - `Flask-Limiter <https://flask-limiter.readthedocs.io/en/stable>`_ for API rate limits
    - `gunicorn <https://gunicorn.org/>`_ to serve application
- Client:
    - Vue3/Vuex
    - `Leaflet <https://leafletjs.com/>`__ to display map
    - `Chart.js <https://www.chartjs.org/>`__ to display charts with elevation and speed
    - `heatmap.js <https://www.patrick-wied.at/static/heatmapjs/>`__ (`fork <https://github.com/SamR1/heatmap.js>`__) and `leaflet-heatmap <https://github.com/Leaflet/Leaflet.heat>`__ to display heatmap on Outdoor Tennis map

| Logo, some sports and weather icons are made by `Freepik <https://www.freepik.com/>`__ from `www.flaticon.com <https://www.flaticon.com/>`__.
| Sports icons for Canoeing, Kayaking and Rowing are made by `@Von-Birne <https://github.com/Von-Birne>`__.
| Sports icon for Halfbike is made by `@astridx <https://github.com/astridx>`__.
| FitTrackee also uses icons from `Fork Awesome <https://forkaweso.me>`__.


Prerequisites
~~~~~~~~~~~~~

- mandatory

  - installation from sources or package:

    - `Python <https://www.python.org/>`__ 3.10+
    - `PostgreSQL <https://www.postgresql.org/>`__ 13+
    - `PostGIS <https://postgis.net/>`__ 3.4+
    - `GDAL <https://gdal.org/en/stable/>`__ on the server running the application, if different from the server running the database (GDAL is installed with PostGIS)

  - installation with Docker:

    - `Docker <https://docs.docker.com/get-started/>`__ and `Docker Compose <https://docs.docker.com/compose/>`__ v2.30+

- optional

  - `Redis <https://redis.io/>`__ for `task queue <installation.html#tasks-processing>`__ (if email sending is enabled and for data export requests, asynchronous archive uploads) and API rate limits (for installation from sources or package)
  - SMTP provider (if email sending is enabled)
  - API key from a `weather data provider <installation.html#weather-data>`__
  - `Poetry <https://python-poetry.org>`__ 1.2+ (for installation from sources only)
  - `Node <https://nodejs.org>`__ 20+ and `Yarn <https://yarnpkg.com>`__ (for development only)

.. note::
    | If registration is enabled, it is recommended to set Redis and a SMTP provider for email sending and data export requests.

.. note::
    Depending on the operating system and the version of Python installed, additional dependencies may be required, such as **gcc** or **libgdal-dev**.


Environment variables
~~~~~~~~~~~~~~~~~~~~~

.. warning::
    | Since FitTrackee 0.4.0, ``Makefile.custom.config`` is replaced by ``.env``

The following environment variables are used by **FitTrackee** web application
or the task processing library. They are not all mandatory depending on
deployment method.

.. envvar:: API_RATE_LIMITS

    .. versionadded:: 0.7.0

    API rate limits, see `API rate limits <installation.html#api-rate-limits>`__.

    :default: ``300 per 5 minutes``


.. envvar:: APP_LOG

    .. versionadded:: 0.4.0

    Path to log file


.. envvar:: APP_SECRET_KEY

    **FitTrackee** secret key, must be initialized in production environment.

    .. warning::
        Use a strong secret key. This key is used in JWT generation.

.. envvar:: APP_SETTINGS

    **FitTrackee** configuration.

    :default: ``fittrackee.config.ProductionConfig``


.. envvar:: APP_TIMEOUT

    .. versionadded:: 0.9.3

    Timeout (in seconds) for workers spawned by **Gunicorn** (when starting application with **FitTrackee** entry point or with Docker image), see `Gunicorn documentation <https://docs.gunicorn.org/en/stable/settings.html#timeout>`__).

    :default: 30

.. envvar:: APP_WORKERS

    .. versionchanged:: 0.9.3 used by the Docker image entry point script

    Number of workers spawned by **Gunicorn** (when starting application with **FitTrackee** entry point or with Docker image), see `Gunicorn documentation <https://docs.gunicorn.org/en/stable/settings.html#workers>`__.

    :default: 1

.. envvar:: DATABASE_DISABLE_POOLING

    .. versionadded:: 0.4.0
    .. versionremoved:: 0.9.3

    Disable pooling if needed (when starting application with **FitTrackee** entry point and not directly with **Gunicorn**),
    see `SqlAlchemy documentation <https://docs.sqlalchemy.org/en/13/core/pooling.html#using-connection-pools-with-multiprocessing-or-os-fork>`__.

    :default: ``false``

.. envvar:: DATABASE_URL

    | Database URL with username and password, must be initialized in production environment.
    | For example in dev environment : ``postgresql://fittrackee:fittrackee@localhost:5432/fittrackee``

    .. warning::
        | Since `SQLAlchemy update (1.4+) <https://docs.sqlalchemy.org/en/14/changelog/changelog_14.html#change-3687655465c25a39b968b4f5f6e9170b>`__,
          engine URL should begin with ``postgresql://``.

.. envvar:: DEFAULT_STATICMAP

    .. versionadded:: 0.4.9

    | If ``True``, it keeps using **Static Map 3** default tile server to generate static maps (OSM tile server).
    | Otherwise, it uses the tile server set in `TILE_SERVER_URL <installation.html#envvar-TILE_SERVER_URL>`__.

    .. versionchanged:: 0.6.10

    | This variable is now case-insensitive.
    | If ``False``, depending on tile server, `subdomains <installation.html#envvar-STATICMAP_SUBDOMAINS>`__ may be mandatory.

    :default: ``False``


.. envvar:: DRAMATIQ_LOG

    .. versionadded:: 0.9.5

    Path to **Dramatiq** log file.


.. envvar:: EMAIL_URL

    .. versionadded:: 0.3.0

    Email URL with credentials, see `Emails <installation.html#emails>`__.

    .. versionchanged:: 0.6.5

    :default: empty string

    .. danger::
        If the email URL is empty, email sending will be disabled.

    .. warning::
        If the email URL is invalid, the application may not start.

.. envvar:: ENABLE_GEOSPATIAL_FEATURES

    .. versionadded:: 1.0.0

    | Enables geospatial features on User Interface.
    | **Keep the value set to** ``False`` **until all workouts have been updated to add geometries** (see `Workouts CLI command <cli.html#ftcli-workouts-refresh>`__).
    | This variable is case-insensitive.

    :default: ``False``

    .. warning::
        This is a temporary flag. It will be removed in the next version, which will require all workouts to be updated.


.. envvar:: FLASK_APP

    | Name of the module to import at flask run.
    | ``FLASK_APP`` should contain ``$(PWD)/fittrackee/__main__.py`` with installation from sources, else ``fittrackee``.


.. envvar:: HOST

    **FitTrackee** host.

    :default: ``127.0.0.1``


.. envvar:: MAP_ATTRIBUTION

    .. versionadded:: 0.4.0

    Map attribution (if using another tile server), see `Map tile server <installation.html#map-tile-server>`__.

    :default: ``&copy; <a href="http://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors``


.. envvar:: NOMINATIM_URL

    .. versionadded:: 1.0.0

    URL of `Nominatim <https://nominatim.org>`__ server, used to get location coordinates from user input

    :default: ``https://nominatim.openstreetmap.org``


.. envvar:: PORT

    **FitTrackee** port.

    :default: 5000


.. envvar:: REDIS_URL

    .. versionadded:: 0.3.0

    Redis instance used by **Dramatiq** and **Flask-Limiter**.

    :default: local Redis instance (``redis://``)


.. envvar:: SENDER_EMAIL

    .. versionadded:: 0.3.0

    **FitTrackee** sender email address.


.. envvar:: STATICMAP_CACHE_DIR

    .. versionadded:: 0.10.0

    Directory for **Static Map 3** cache

    :default: ``.staticmap_cache``

    .. warning::
        This is the library's default variable, to be modified to set another directory.


.. envvar:: STATICMAP_SUBDOMAINS

    .. versionadded:: 0.6.10

    | Some tile servers require a subdomain, see `Map tile server <installation.html#map-tile-server>`__.
    | For instance: "a,b,c" for OSM France.

    :default: empty string


.. envvar:: TASKS_TIME_LIMIT

    .. versionadded:: 0.10.0

    Timeout in seconds for **Dramatiq** task execution to avoid long-running tasks.

    :default: 1800


.. envvar:: TILE_SERVER_URL

    .. versionadded:: 0.4.0

    | Tile server URL (with api key if needed), see `Map tile server <installation.html#map-tile-server>`__.
    | Since **0.4.9**, it's also used to generate static maps (to keep default server, see `DEFAULT_STATICMAP <installation.html#envvar-DEFAULT_STATICMAP>`__)

    .. versionchanged:: 0.7.23

    | The default URL is updated: **OpenStreetMap**'s tile server no longer requires subdomains.

    :default: ``https://tile.openstreetmap.org/{z}/{x}/{y}.png``


.. envvar:: UI_URL

    **FitTrackee** URL, needed for links in emails and mentions on interface.

    .. warning::
        UI_URL must contains url scheme (``https://``).


.. envvar:: UPLOAD_FOLDER

    .. versionadded:: 0.4.0

    **Absolute path** to the directory where ``uploads`` folder will be created.

    :default: ``<application_directory>/fittrackee``

    .. danger::
        | With installation from PyPI, the directory will be located in
          **virtualenv** directory if the variable is not initialized.

.. envvar:: VITE_APP_API_URL

    .. versionchanged:: 0.7.26 ⚠️ replaces ``VUE_APP_API_URL``

    **FitTrackee** API URL, only needed in dev environment.

.. envvar:: WEATHER_API_KEY

    .. versionchanged:: 0.4.0 ⚠️ replaces ``WEATHER_API``

    Weather API key (not mandatory), see ``WEATHER_API_PROVIDER``.


.. envvar:: WEATHER_API_PROVIDER

    .. versionadded:: 0.7.11

    Provider for weather data (not mandatory), see `Weather data <installation.html#weather-data>`__.

.. envvar:: WORKERS_PROCESSES

    .. versionadded:: 0.3.0

    Number of processes used by **Dramatiq**.


Docker Compose
^^^^^^^^^^^^^^

.. versionadded:: 0.8.13
.. versionchanged:: 0.11.2 Rename variables and add ``HOST_STATICMAP_CACHE_DIR``

.. envvar:: HOST_APP_PORT

    Application container port


.. envvar:: HOST_DATABASE_DIR

    Host directory for PostgreSQL data volume


.. envvar:: POSTGRES_USER

    User for PostgreSQL database


.. envvar:: POSTGRES_PASSWORD

    Password for PostgreSQL user


.. envvar:: POSTGRES_DB

    Database name for FitTrackee application


.. envvar:: HOST_REDIS_DIR

    Host directory for redis data volume


.. envvar:: HOST_LOG_DIR

    Host directory for logs volume


.. envvar:: HOST_UPLOAD_DIR

    Host directory for uploaded files volume


.. envvar:: HOST_STATICMAP_CACHE_DIR

    Host directory for Static Map 3 cache volume


Emails
~~~~~~
.. versionadded:: 0.3.0
.. versionchanged:: 0.5.3  Credentials and port can be omitted
.. versionchanged:: 0.6.5  Disable email sending
.. versionchanged:: 0.7.24  Handle special characters in password

To send emails, a valid ``EMAIL_URL`` must be provided:

- with an unencrypted SMTP server: ``smtp://username:password@smtp.example.com:25``
- with SSL: ``smtp://username:password@smtp.example.com:465/?ssl=True``
- with STARTTLS: ``smtp://username:password@smtp.example.com:587/?tls=True``

Credentials can be omitted: ``smtp://smtp.example.com:25``.
If ``:<port>`` is omitted, the port defaults to 25.

Password can be encoded if it contains special characters.
For instance with password ``passwordwith@and&and?``, the encoded password will be: ``passwordwith%40and%26and%3F``.

.. warning::
    | If the email URL is invalid, the application may not start.
    | Sending emails with Office365 may not work if SMTP auth is disabled.

.. warning::
     | Since 0.6.0, newly created accounts must be confirmed (an email with confirmation instructions is sent after registration).

Emails sent by FitTrackee are:

- account confirmation instructions
- password reset request
- email change (to old and new email addresses)
- password change
- notification when a data export archive is ready to download (*new in 0.7.13*)
- suspension and warning (*new in 0.9.0*)
- suspension and warning lifting (*new in 0.9.0*)
- rejected appeal (*new in 0.9.0*)


On single-user instance, it is possible to disable email sending with an empty ``EMAIL_URL`` (in this case, no need to start **Dramatiq** workers).

A `CLI <cli.html#ftcli-users-update>`__ is available to activate account, modify email and password and handle data export requests.


Map tile server
~~~~~~~~~~~~~~~
.. versionadded:: 0.4.0
.. versionchanged:: 0.6.10 Handle tile server subdomains
.. versionchanged:: 0.7.23 Default tile server (**OpenStreetMap**) no longer requires subdomains

Default tile server is now **OpenStreetMap**'s standard tile layer (if environment variables are not initialized).
The tile server can be changed by updating ``TILE_SERVER_URL`` and ``MAP_ATTRIBUTION`` variables (`list of tile servers <https://wiki.openstreetmap.org/wiki/Raster_tile_providers>`__).

To keep using **ThunderForest Outdoors**, the configuration is:

- ``TILE_SERVER_URL=https://{s}.tile.thunderforest.com/outdoors/{z}/{x}/{y}.png?apikey=XXXX`` where **XXXX** is **ThunderForest** API key
- ``MAP_ATTRIBUTION=&copy; <a href="http://www.thunderforest.com/">Thunderforest</a>, &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors``

.. note::
    | Check the terms of service of tile provider for map attribution.

Since the tile server can be used for static map generation, some servers require a subdomain.

For instance, to set OSM France tile server, the expected values are:

- ``TILE_SERVER_URL=https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png``
- ``MAP_ATTRIBUTION='fond de carte par <a href="http://www.openstreetmap.fr/mentions-legales/" target="_blank" rel="nofollow noopener">OpenStreetMap France</a>, sous&nbsp;<a href="http://creativecommons.org/licenses/by-sa/2.0/fr/" target="_blank" rel="nofollow noopener">licence CC BY-SA</a>'``
- ``STATICMAP_SUBDOMAINS=a,b,c``

The subdomain will be chosen randomly.

The default tile server (**OpenStreetMap**) no longer requires subdomains.


API rate limits
~~~~~~~~~~~~~~~
.. versionadded:: 0.7.0

| API rate limits are managed by `Flask-Limiter <https://flask-limiter.readthedocs.io/en/stable>`_, based on IP with fixed window strategy.
| To enable rate limits, **Redis** must be available.

.. note::
    | If no Redis instance is available for rate limits, FitTrackee can still start.

| All endpoints are subject to rate limits, except endpoints serving assets.
| Limits can be modified by setting the environment variable ``API_RATE_LIMITS`` (see `Flask-Limiter documentation for notation <https://flask-limiter.readthedocs.io/en/stable/configuration.html#rate-limit-string-notation>`_).
| Rate limits must be separated by a comma, for instance:

.. code-block::

    export API_RATE_LIMITS="200 per day, 50 per hour"

**Flask-Limiter** provides a `Command Line Interface <https://flask-limiter.readthedocs.io/en/stable/cli.html>`_ for maintenance and diagnostic purposes.

.. code-block:: bash

    $ flask limiter
    Usage: flask limiter [OPTIONS] COMMAND [ARGS]...

      Flask-Limiter maintenance & utility commands

    Options:
      --help  Show this message and exit.

    Commands:
      clear   Clear limits for a specific key
      config  View the extension configuration
      limits  Enumerate details about all routes with rate limits


Weather data
~~~~~~~~~~~~
.. versionchanged:: 0.7.11 Add Visual Crossing to weather providers
.. versionchanged:: 0.7.15 Remove Darksky from weather providers

The following weather data providers are supported by **FitTrackee**:

- `Visual Crossing <https://www.visualcrossing.com>`__ (**note**: historical data are provided on hourly period)

.. note::

   **DarkSky** support is discontinued, since the service shut down on March 31, 2023.

To configure a weather provider, set the following environment variables:

- ``WEATHER_API_PROVIDER``: the name of the provider (currently ``visualcrossing`` is the only choice)
- ``WEATHER_API_KEY``: the key to the corresponding weather provider


Tasks processing
~~~~~~~~~~~~~~~~

.. versionadded:: 0.3.0
.. versionchanged:: 0.10.0 Add ``TASKS_TIME_LIMIT`` variable

Tasks processing is done using `Dramatiq <https://dramatiq.io/>`_. It requires Redis and is used for email sending, user data exports and workouts archives uploads.

.. note::
    If no workers are running, a `command line <cli.html>`__ allows to process queued tasks.

The following environment variables must be set:

- ``REDIS_URL``: Redis instance used by **Dramatiq** and **Flask-Limiter**.
- ``WORKERS_PROCESSES``: Number of processes used by **Dramatiq**.
- ``DRAMATIQ_LOG``: Path to **Dramatiq** log file.

To avoid long-running tasks for user data exports and workouts archives uploads, a time limit is set:

- ``TASKS_TIME_LIMIT``: Timeout in seconds for **Dramatiq** task execution. The default value is 1800 seconds (30 minutes).

To start task queue workers, run the following command:

.. code-block:: bash

    $ dramatiq fittrackee.tasks:broker --processes=$WORKERS_PROCESSES --log-file=$DRAMATIQ_LOG

.. note::
    | It is also possible to start task queue workers with **Flask-Dramatiq** CLI, but it is recommended to use **Dramatiq** CLI instead for now.

It is possible to run queues independently, for instance for workouts archive uploads:

.. code-block:: bash

    $ dramatiq fittrackee.tasks:broker --processes=2 -Q fittrackee_workouts

The following queues are available:

- ``fittrackee_emails``: for emails sending (priority: high)
- ``fittrackee_users_exports``: for user data exports (priority: medium)
- ``fittrackee_workouts``: for workouts archive uploads (priority: medium)

Run ``dramatiq -h`` to see a list of the available commands.

Installation
~~~~~~~~~~~~

.. warning::
    | Note that **FitTrackee** is under heavy development, some features may be unstable.

.. note::
    Depending on the operating system and the version of Python installed, additional dependencies may be required, such as **gcc** or **libgdal-dev**.

From PyPI
^^^^^^^^^

.. note::
    | Simplest way to install FitTrackee.

- Create and activate a `virtualenv <https://docs.python.org/3/library/venv.html>`__

- Install **FitTrackee** with pip

.. code-block:: bash

    $ pip install fittrackee

- Create ``fittrackee`` database

Example:

.. code-block:: sql

    CREATE USER fittrackee WITH PASSWORD '<PASSWORD>';
    CREATE SCHEMA fittrackee AUTHORIZATION fittrackee;
    CREATE DATABASE fittrackee OWNER fittrackee;

.. note::
    | see PostgreSQL `documentation <https://www.postgresql.org/docs/15/ddl-schemas.html>`_ for schema and privileges.

- Install **PostGIS** extension

Example for `fittrackee` database:

.. code-block:: bash

    $ psql -U <SUPER_USER> -d fittrackee -c 'CREATE EXTENSION IF NOT EXISTS postgis;'

.. note::
    | **PostGIS** must be installed on OS, see `installation documentation <https://postgis.net/documentation/getting_started/#installing-postgis>`_.
    | Many OS includes pre-built packages for PostGIS, see `wiki <https://trac.osgeo.org/postgis/wiki/UsersWikiPackages>`_.

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

- Start task queue workers **if email sending is enabled**, with **Dramatiq** CLI (see `documentation <https://dramatiq.io/guide.html#workers>`__) :

.. code-block:: bash

    $ dramatiq fittrackee.tasks:broker --processes=$WORKERS_PROCESSES --log-file=$DRAMATIQ_LOG

.. note::
    | It is also possible to start task queue workers with **Flask-Dramatiq** CLI:

    .. code-block:: bash

        $ flask worker --processes 2

    | But running **Flask-Dramatiq** CLI on Python 3.13+ raises errors. Emails and user data export are sent, but the `middleware <https://dramatiq.io/reference.html#dramatiq.middleware.TimeLimit>`__ preventing actors from running too long is not active. Please use **Dramatiq** CLI instead for now.

.. note::
    | To start application and workers with **systemd** service, see `Deployment <installation.html#deployment>`__

- Open http://localhost:5000 and register

- To set owner role to the newly created account, use the following command line:

.. code:: bash

   $ ftcli users update <username> --set-role owner

.. note::
    If the user account is inactive, it activates it.

From sources
^^^^^^^^^^^^

.. warning::
    | Since **FitTrackee** 0.2.1, Python packages installation needs Poetry.
    | For more information, see `Poetry Documentation <https://python-poetry.org/docs/#installation>`__

.. note::
    | To keep virtualenv in project directory, update Poetry `configuration <https://python-poetry.org/docs/configuration/#virtualenvsin-project>`__.

    .. code-block:: bash

        $ poetry config virtualenvs.in-project true

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
   $ make install-db-dev

-  Start the server and the client:

.. code:: bash

   $ make serve

-  Run **Dramatiq** workers:

.. code:: bash

   $ make run-workers

- Open http://localhost:3000 and register

- To set owner role to the newly created account, use the following command line:

.. code:: bash

   $ make user-set-role USERNAME=<username> ROLE=owner

.. note::
    If the user account is inactive, it activates it.

Production environment
""""""""""""""""""""""

.. warning::
    | Note that FitTrackee is under heavy development, some features may be unstable.

-  Download the last release (for now, it is the release v1.0.3):

.. code:: bash

   $ wget https://github.com/SamR1/FitTrackee/archive/1.0.3.tar.gz
   $ tar -xzf v1.0.3.tar.gz
   $ mv FitTrackee-1.0.3 FitTrackee
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

-  Start the server and **Dramatiq** workers:

.. code:: bash

   $ make run

.. note::
    If email sending is disabled: ``$ make run-server``

- Open http://localhost:5000 and register

- To set owner role to the newly created account, use the following command line:

.. code:: bash

   $ make user-set-role USERNAME=<username> ROLE=owner

.. note::
    If the user account is inactive, it activates it.

Upgrade
~~~~~~~

.. danger::
    If you are upgrading to version 1.0, additional steps are required, see `Upgrading to 1.0.0 <upgrading-to-1.0.0.html>`__.

.. warning::
    Before upgrading, make a backup of all data:

    - database (with `pg_dump <https://www.postgresql.org/docs/current/app-pgdump.html>`__ for instance)
    - upload directory (see `Environment variables <installation.html#envvar-UPLOAD_FOLDER>`__)

.. warning::

    For now, releases do not follow `semantic versioning <https://semver.org>`__. Any version may contain backward-incompatible changes.

.. note::
    Depending on the operating system and the version of Python installed, additional dependencies may be required, such as **gcc** or **libgdal-dev**.


From PyPI
^^^^^^^^^

.. warning::
    | Only if **FitTrackee** was initially installed from **PyPI**

- Stop the application and activate the `virtualenv <https://docs.python.org/3/library/venv.html>`__

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

.. warning::
    | Only if **FitTrackee** was initially installed from sources.


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

-  Run **Dramatiq** workers:

.. code:: bash

   $ make run-workers

Prod environment
""""""""""""""""

- Stop the application

- Change to the directory where FitTrackee directory is located

- Download the last release (for now, it is the release v1.0.3) and overwrite existing files:

.. code:: bash

   $ wget https://github.com/SamR1/FitTrackee/archive/v1.0.3.tar.gz
   $ tar -xzf v1.0.3.tar.gz
   $ cp -R FitTrackee-1.0.3/* FitTrackee/
   $ cd FitTrackee

- Update **.env** if needed (see `Environment variables <installation.html#environment-variables>`__).

- Upgrade packages:

.. code:: bash

   $ make install-python

- Upgrade database if needed (see changelog for migrations):

.. code:: bash

   $ make upgrade-db

- Restart the server and **Dramatiq** workers:

.. code:: bash

   $ make run

.. note::
    If email sending is disabled: ``$ make run-server``

Deployment
~~~~~~~~~~

There are several ways to start **FitTrackee** web application and task queue
library.
One way is to use a **systemd** services and **Nginx** to proxy pass to **Gunicorn**.

Examples:

.. warning::
    To adapt depending on your instance configuration and operating system

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
    Environment="STATICMAP_SUBDOMAINS="
    Environment="MAP_ATTRIBUTION="
    Environment="WEATHER_API_KEY="
    Environment="STATICMAP_CACHE_DIR="
    WorkingDirectory=/home/<USER>/<FITTRACKEE DIRECTORY>
    ExecStart=/home/<USER>/<FITTRACKEE DIRECTORY>/.venv/bin/gunicorn -b 127.0.0.1:5000 "fittrackee:create_app()" --error-logfile /home/<USER>/<FITTRACKEE DIRECTORY>/gunicorn.log
    Restart=always

    [Install]
    WantedBy=multi-user.target


.. seealso::
    To handle large files, a higher value for `timeout <https://docs.gunicorn.org/en/stable/settings.html#timeout>`__ can be set.

.. seealso::
    More information on deployment with Gunicorn in its `documentation <https://docs.gunicorn.org/en/stable/deploy.html>`__.

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
    Environment="TASKS_TIME_LIMIT="
    Environment="STATICMAP_CACHE_DIR="
    WorkingDirectory=/home/<USER>/<FITTRACKEE DIRECTORY>
    ExecStart=/home/<USER>/<FITTRACKEE DIRECTORY>/.venv/bin/dramatiq fittrackee.tasks:broker --processes=<NUMBER OF PROCESSES> --log-file=<DRAMATIQ_LOG_FILE_PATH>
    Restart=always

    [Install]
    WantedBy=multi-user.target

.. note::
    Command to be adapted to run queues separately

.. seealso::
    More information on **Dramatiq** CLI in its `documentation <https://dramatiq.io/guide.html#workers>`__.

- **Nginx** configuration:

.. code-block::

    server {
        listen 443 ssl http2;
        server_name example.com;
        ssl_certificate fullchain.pem;
        ssl_certificate_key privkey.pem;

        ## this parameter controls how large of a file can be 
        ## uploaded, and defaults to 1MB. If you change the FitTrackee
        ## settings to allow larger uploads, you'll need to change this
        ## setting by uncommenting the line below and setting the size limit
        ## you want. Set to "0" to prevent nginx from checking the 
        ## request body size at all
        # client_max_body_size 1m; 

        location / {
            proxy_pass http://127.0.0.1:5000;
            proxy_redirect    default;
            proxy_set_header  Host $host;
            proxy_set_header  X-Real-IP $remote_addr;
            proxy_set_header  X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header  X-Forwarded-Host $server_name;
            proxy_set_header  X-Forwarded-Proto $scheme;
        }
    }

    server {
        listen 80;
        server_name example.com;
        location / {
            return 301 https://example.com$request_uri;
        }
    }

.. seealso::
    If needed, update configuration to handle larger files (see `client_max_body_size <https://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size>`_).


Docker
~~~~~~

.. versionadded:: 0.4.4
.. versionchanged:: 0.5.0 add client application for development
.. versionchanged:: 0.8.13 add docker image for production


Production
^^^^^^^^^^

Images are available on `DockerHub <https://hub.docker.com/r/fittrackee/fittrackee>`_ or `Github registry <https://github.com/SamR1/FitTrackee/packages>`_.

.. note::

    Images are available for ``linux/amd64`` and ``linux/arm64`` platforms. Only ``linux/amd64`` image has been tested.

.. warning::

    | There is no official image for PostGIS on ARM platforms yet, see `issue on GitHub <https://github.com/postgis/docker-postgis/issues/216>`__.
    | The workaround is to build PostGIS image locally.

- create a ``docker-compose.yml`` file as needed (see the `example <https://github.com/SamR1/FitTrackee/blob/main/docker-compose.yml>`__ in the repository):

  - the minimal set up requires at least the database and the web application
  - to activate the rate limit, redis is required
  - to send e-mails, redis and workers are required and a valid ``EMAIL_URL`` variable must be set in ``.env``

.. note::
    The same image is used by the web application and workers.

.. warning::
    Following directory must be writable for ``fittrackee`` user (see `docker-compose.yml example <https://github.com/SamR1/FitTrackee/blob/main/docker-compose.yml>`__):

    - ``/usr/src/app/uploads``
    - ``/usr/src/app/logs``
    - ``/usr/src/app/.staticmap_cache``

- create ``.env`` from example (``.env.docker.example``) and update it (see `Environment variables <installation.html#environment-variables>`__).

- to start the application:

.. code:: bash

   $ docker compose up -d

.. warning::

    Migrations are executed at startup. Please backup data before updating FitTrackee image version.

- to run a CLI command, for instance to give admin rights:

.. code:: bash

   $ docker compose exec fittrackee ftcli users update <username> --set-role admin


Development
^^^^^^^^^^^

- To install and run **FitTrackee**:

.. code-block:: bash

    $ git clone https://github.com/SamR1/FitTrackee.git
    $ cd FitTrackee
    $ make docker-run

- Open http://localhost:5000 and register.

.. note::

  | To change ``fittrackee`` container port when running containers with Makefile commands, create a ``.env`` file with `APP_PORT <installation.html#envvar-APP_PORT>`__.
  | For example:

  .. code-block::

    export APP_PORT=5001


Open http://localhost:8025 to access `MailHog interface <https://github.com/mailhog/MailHog>`_ (email testing tool)

- To set owner role to the newly created account, use the following command line:

.. code:: bash

   $ make docker-set-role USERNAME=<username> ROLE=owner

.. note::
    If the user account is inactive, it activates it.

- To stop **Fittrackee**:

.. code-block:: bash

    $ make docker-stop

- To run shell inside **Fittrackee** container:

.. code-block:: bash

    $ make docker-shell

- an additional step is needed to install ``fittrackee_client``

.. code-block:: bash

    $ make docker-build-client

- to start **FitTrackee** with client dev tools:

.. code-block:: bash

    $ make docker-serve-client

Open http://localhost:3000

.. note::
    Some environment variables need to be updated like ``UI_URL``

- to run lint or tests:

.. code-block:: bash

    $ make docker-lint-client  # run type check and lint on javascript files
    $ make docker-test-client  # run unit tests on Client
    $ make docker-lint-python  # run type check and lint on python files
    $ make docker-test-python  # run unit tests on API


VSCode
~~~~~~

.. versionadded:: 1.0.4

Development
^^^^^^^^^^^

You can use the **Dev Container** without the **debug configuration** and vice versa.
Dev Container is strongly recommended on Windows because of path handling issues.


Dev Container
"""""""""""""
Using a Dev Container gives you a ready-to-use environment (Python, Poetry, Node, etc.) without installing them on your host.

**Prerequisites**

- Docker Engine
- VS Code with `Dev Containers extension <https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers>`__

**How to use**

- Open the FitTrackee folder in VS Code.
- When prompted, choose **Reopen in Container** (or open the Command Palette and run ``Dev Containers: Reopen in Container``).

.. note::

   | For better file-system performance on Windows/macOS, use an **anonymous container volume** so code and packages are stored inside the VM filesystem.
   | Use the Command Palette action ``Dev Containers: Clone Repository in Container Volume`` to clone into a volume.
   | If you rebuild the container frequently, prefer a **named volume** to preserve installed dependencies between rebuilds.
   | See `Improve performance <https://code.visualstudio.com/remote/advancedcontainers/improve-performance>`__.

.. note::

    Port 5000 (fittrackee-ui) is forwarded automatically, if you change APP_PORT you need to manually forward the new port using ``Forward a Port`` command in the Command Palette.


Debug configuration & tasks
"""""""""""""""""""""""""""
This repository includes a VS Code *launch* configuration that:

- starts the full Docker Compose dev stack in the background,
- waits until services are healthy,
- attaches the debugger to the backend so breakpoints work immediately,
- tears the stack down when you stop the debugger.

**How to start debugging**

- Open the Command Palette and run ``Debug: Start Debugging`` **or** press **F5**.

.. note::
   If the debugger fails to attach, use ``Debug: Select Debug Session`` to end the session,
   check container logs, then run ``Tasks: Run Task`` and then **down: devcontainer-compose**
   before retrying.

.. warning::
   On Linux, ``host.docker.internal`` does not resolve automatically from inside containers.
   If the debugger fails to attach and logs show connection issues to ``host.docker.internal:5678``,
   ensure ``.devcontainer\docker-compose-devcontainer.yml`` includes the host gateway mapping:

   .. code-block:: yaml

      services:
        fittrackee:
          extra_hosts:
            - "host.docker.internal:host-gateway"


Yunohost
~~~~~~~~

Thanks to contributors, a package is available, see https://github.com/YunoHost-Apps/fittrackee_ynh.


NixOS
~~~~~

Thanks to contributors, a package is available on NixOS, see https://search.nixos.org/packages?query=fittrackee.
