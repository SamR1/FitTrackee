Installation
############

**FitTrackee** can be installed:

- via a single Python package from `PyPI <https://pypi.org/project/fittrackee/>`__,
- from sources,
- with a `Docker <installation.html#docker>`__ image.

Thanks to contributors, packages are also available on `Yunohost <https://apps.yunohost.org/app/fittrackee>`__ and `NixOS <https://search.nixos.org/packages?query=fittrackee>`__.


Main dependencies
*****************

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
    - `Chart.js <https://www.chartjs.org/>`__ to display charts
    - `heatmap.js <https://www.patrick-wied.at/static/heatmapjs/>`__ (`fork <https://github.com/SamR1/heatmap.js>`__) and `leaflet-heatmap <https://github.com/Leaflet/Leaflet.heat>`__ to display heatmap for rackets sports
    - `zxcvbn-ts <https://zxcvbn-ts.github.io/zxcvbn/>`_ for password strength estimation

| Logo, most of sports icons and weather icons are made by `Freepik <https://www.freepik.com/>`__ from `Flaticon <https://www.flaticon.com/>`__.
| FitTrackee also uses icons from `Fork Awesome <https://forkaweso.me>`__.
| Sports icons for Canoeing, Kayaking and Rowing are made by `@Von-Birne <https://github.com/Von-Birne>`__.
| Sport icon for Halfbike is made by `@astridx <https://github.com/astridx>`__.

Instance types
**************

Single-user instance
====================

| For a single-user instance, `registration <../features/administration.html#configuration>`__ can be disabled.
| So all you need is Python and PostgreSQL/PostGIS database if you want to keep the setup simple. A `CLI <../cli.html#users>`__ is available to manage user account.

Multiple-users instance
=======================

| Registration can en enabled and maximum number of accounts can be set in the `Administration <../features/administration.html#configuration>`__.
| It is recommended to set Redis and a SMTP provider for email sending and tasks processing. Alternatively, a `CLI <../cli.html#users>`__ is available to manage users account.

Prerequisites
*************

- mandatory

  - installation from sources or package:

    - `Python <https://www.python.org/>`__ 3.10+
    - `PostgreSQL <https://www.postgresql.org/>`__ 14+
    - `PostGIS <https://postgis.net/>`__ 3.4+
    - `GDAL <https://gdal.org/en/stable/>`__ on the server running the application, if different from the server running the database (GDAL is installed with PostGIS)

  - installation with Docker:

    - `Docker <https://docs.docker.com/get-started/>`__ and `Docker Compose <https://docs.docker.com/compose/>`__ v2.30+

- optional

  - `Redis <https://redis.io/>`__ for `task queue <tasks_processing.html>`__ (for `email <emails.html>`__ sending if enable, for data export requests, and asynchronous archive uploads if enabled) and `API rate limits <api_rate_limits.html>`__ (for installation from sources or package)
  - SMTP provider (if `email <emails.html>`__ sending is enabled)
  - API key from a `weather data provider <weather.html>`__
  - `elevation data provider <elevation.html>`__
  - `Poetry <https://python-poetry.org>`__ 1.2+ (for installation from sources only)
  - `Node <https://nodejs.org>`__ 20+ and `Yarn <https://yarnpkg.com>`__ (for development only)

.. note::
    | If registration is enabled, it is recommended to set Redis and a SMTP provider for email sending and data export requests.

.. note::
    Depending on the operating system and the version of Python installed, additional dependencies may be required, such as **gcc** or **libgdal-dev**.

.. important::

    This documentation does not detail how to secure a server. Please refer to the documentation and best practices corresponding to your installation and operating system.


.. toctree::
   :maxdepth: 2

   environments_variables.rst
   installation
   upgrade
   deployment
   map_tile_server
   weather
   elevation
   emails
   api_rate_limits
   tasks_processing
