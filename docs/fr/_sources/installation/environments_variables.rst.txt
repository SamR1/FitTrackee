Environment variables
#####################

.. warning::
    | Since FitTrackee 0.4.0, ``Makefile.custom.config`` is replaced by ``.env``


General variables
*****************


The following environment variables are used by **FitTrackee** web application
or the task processing library. They are not all mandatory depending on
deployment method.

.. envvar:: API_RATE_LIMITS

    .. versionadded:: 0.7.0
    .. versionchanged:: 1.0.4 remove default value

    API rate limits set for **Flask-Limiter** see `API rate limits <api_rate_limits.html>`__.

.. envvar:: APP_LOG

    .. versionadded:: 0.4.0

    Path to log file

    .. versionchanged:: 1.0.4

    If the value is not set, logging output is displayed only on the console.


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
    | Otherwise, it uses the tile server set in `TILE_SERVER_URL <environments_variables.html#envvar-TILE_SERVER_URL>`__.

    .. versionchanged:: 0.6.10

    | This variable is now case-insensitive.
    | If ``False``, depending on tile server, `subdomains <environments_variables.html#envvar-STATICMAP_SUBDOMAINS>`__ may be mandatory.

    :default: ``False``


.. envvar:: DRAMATIQ_LOG

    .. versionadded:: 0.9.5

    Path to **Dramatiq** log file.


.. envvar:: EMAIL_URL

    .. versionadded:: 0.3.0

    Email URL with credentials, see `Email <emails.html>`__.

    .. versionchanged:: 0.6.5

    :default: empty string

    .. danger::
        If the email URL is empty, email sending will be disabled.

    .. warning::
        If the email URL is invalid, the application may not start.

.. envvar:: ENABLE_GEOSPATIAL_FEATURES

    .. versionadded:: 1.0.0
    .. versionremoved:: 1.1.0

    | Enables geospatial features on User Interface.
    | **Keep the value set to** ``False`` **until all workouts have been updated to add geometries** (see `Workouts CLI command <../cli.html#ftcli-workouts-refresh>`__).
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


.. envvar:: LOG_LEVEL

    .. versionadded:: 1.0.4

    Log level for **Gunicorn** (when starting application with **FitTrackee** entry point or with Docker image), see `Gunicorn documentation <https://docs.gunicorn.org/en/stable/settings.html#loglevel>`__).

    :default: ``info``


.. envvar:: MAP_ATTRIBUTION

    .. versionadded:: 0.4.0

    Map attribution (if using another tile server), see `Map tile server <map_tile_server.html>`__.

    :default: ``&copy; <a href="http://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors``


.. envvar:: NOMINATIM_URL

    .. versionadded:: 1.0.0

    URL of `Nominatim <https://nominatim.org>`__ server, used to get location coordinates from user input

    :default: ``https://nominatim.openstreetmap.org``


.. envvar:: OPEN_ELEVATION_API_URL

    .. versionadded:: 1.1.0

    URL of `OpenElevation <https://open-elevation.com/>`__ service (public API or self-hosted instance).


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

    | Some tile servers require a subdomain, see `Map tile server <map_tile_server.html>`__.
    | For instance: "a,b,c" for OSM France.

    :default: empty string


.. envvar:: TASKS_TIME_LIMIT

    .. versionadded:: 0.10.0

    Timeout in seconds for **Dramatiq** task execution to avoid long-running tasks.

    :default: 1800


.. envvar:: TILE_SERVER_URL

    .. versionadded:: 0.4.0

    | Tile server URL (with api key if needed), see `Map tile server <map_tile_server.html>`__.
    | Since **0.4.9**, it's also used to generate static maps (to keep default server, see `DEFAULT_STATICMAP <environments_variables.html#envvar-DEFAULT_STATICMAP>`__)

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

.. envvar:: VALHALLA_API_URL

    .. versionadded:: 1.1.0

    URL of `Valhalla <https://valhalla.github.io/valhalla/>`__ service (public API or self-hosted instance).

.. envvar:: VITE_APP_API_URL

    .. versionchanged:: 0.7.26 ⚠️ replaces ``VUE_APP_API_URL``

    **FitTrackee** API URL, only needed in dev environment.

.. envvar:: WEATHER_API_KEY

    .. versionchanged:: 0.4.0 ⚠️ replaces ``WEATHER_API``

    Weather API key (not mandatory), see ``WEATHER_API_PROVIDER``.


.. envvar:: WEATHER_API_PROVIDER

    .. versionadded:: 0.7.11

    Provider for weather data (not mandatory), see `Weather data <weather.html>`__.

.. envvar:: WORKERS_PROCESSES

    .. versionadded:: 0.3.0

    Number of processes used by **Dramatiq**.


Docker Compose
**************

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

