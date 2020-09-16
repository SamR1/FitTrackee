Installation
############

This application is written in Python (API) and Javascript (client):

- API:
    - Flask
    - `gpxpy <https://github.com/tkrajina/gpxpy>`_ to parse gpx files
    - `staticmap <https://github.com/komoot/staticmap>`_ to generate a static map image from gpx coordinates
    - `python-forecast.io <https://github.com/ZeevG/python-forecast.io>`_ to fetch weather data from `Dark Sky <https://darksky.net>`__ (former forecast.io)
    - `dramatiq <https://flask-dramatiq.readthedocs.io/en/latest/>`_ for task queue
- Client:
    - React/Redux
    - `Leaflet <https://leafletjs.com/>`__ to display map
    - `Recharts <https://github.com/recharts/recharts>`__ to display charts with elevation and speed

Sports and weather icons are made by `Freepik <https://www.freepik.com/>`__ from `www.flaticon.com <https://www.flaticon.com/>`__.

Prerequisites
~~~~~~~~~~~~~

-  PostgreSQL database (10+)
-  Redis for task queue
-  Python 3.7+
-  `Poetry <https://poetry.eustace.io>`__
-  `Yarn <https://yarnpkg.com>`__ and
   `serve <https://github.com/zeit/serve>`__
-  API key from `Dark Sky <https://darksky.net/dev>`__ [not mandatory]
-  SMTP provider


Installation
~~~~~~~~~~~~

| The following steps describe an installation on Linux systems (tested
  on Debian and Arch).
| On other OS, some issues can be encountered and adaptations may be
  necessary.

.. warning::
    Since FitTrackee 0.2.1, Python packages installation needs Poetry. To install it on ArchLinux:

    .. code-block:: bash

        $ yay poetry
        $ poetry --version
        Poetry 1.0.5

        # optional
        $ poetry config virtualenvs.in-project true

    For other OS, see `Poetry Documentation <https://python-poetry.org/docs/#installation>`__


Dev environment
^^^^^^^^^^^^^^^

-  Clone this repo:

.. code:: bash

   $ git clone https://github.com/SamR1/FitTrackee.git
   $ cd FitTrackee

-  Update **Makefile.config** file if needed and copy/paste the
   **ThunderForest** and **Dark Sky** API keys value in
   **Makefile.custom.config** file (see `Environment variables <installation.html#environment-variables>`__).

-  Install Python virtualenv, React and all related packages and
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

Open http://localhost:3000 and login (the email is ``admin@example.com``
and the password ``mpwoadmin``) or register

Prod environment
^^^^^^^^^^^^^^^^

.. warning::
    Note that FitTrackee is not production-ready yet

-  Download the last release (for now, it is the beta release v0.3.0):

.. code:: bash

   $ wget https://github.com/SamR1/FitTrackee/archive/v0.3.0-beta.tar.gz
   $ tar -xzf v0.3.0-beta.tar.gz
   $ mv FitTrackee-0.3.0-beta FitTrackee
   $ cd FitTrackee

-  Update **Makefile.config** file if needed and copy/paste the
   **ThunderForest** and **Dark Sky** API keys value in
   **Makefile.custom.config** file (see `Environment variables <installation.html#environment-variables>`__).

-  Install Python virtualenv, React and all related packages and
   initialize the database:

.. code:: bash

   $ make install
   $ make install-db

-  Build the client:

.. code:: bash

   $ make build-client

-  Start the server and the client:

.. code:: bash

   $ make run

-  Run dramatiq workers:

.. code:: bash

   $ make run-workers

Open http://localhost:3000, log in as admin (the email is
``admin@example.com`` and the password ``mpwoadmin``) and change the
password

Upgrade
~~~~~~~

.. warning::
    | Before upgrading, make a backup of all data:
    | - database (with `pg_dump <https://www.postgresql.org/docs/11/app-pgdump.html>`__ for instance)
    | - upload directory: **FitTrackee/fittrackee_api/fittrackee_api/uploads/**


Dev environment
^^^^^^^^^^^^^^^

- Stop the application and pull the repository:

.. code:: bash

   $ git pull

- Update **Makefile.config** and **Makefile.custom.config** file if needed

- Upgrade packages and database:

.. code:: bash

   $ make install-dev
   $ make upgrade-db

- Restart the server and the client:

.. code:: bash

   $ make serve


Prod environment
^^^^^^^^^^^^^^^^

``TODO``


Environment variables
~~~~~~~~~~~~~~~~~~~~~

The following environment variables must be defined in **Makefile.custom.config**:

.. cssclass:: table-bordered table-striped

===================================== ============================================== ====================================
variable                              description                                    app default value
===================================== ============================================== ====================================
``REACT_APP_API_URL``                 Fittrackee API URL                             no default value, must be initialized
``REACT_APP_GPX_LIMIT_IMPORT``        max. number of gpx file in zip archive         10 (*deprecated in 0.3.0*)
``REACT_APP_MAX_SINGLE_FILE_SIZE``    max. size of a gpx or picture file             1MB (*deprecated in 0.3.0*)
``REACT_APP_MAX_ZIP_FILE_SIZE``       max. size of a zip archive                     10MB (*deprecated in 0.3.0*)
``REACT_APP_ALLOW_REGISTRATION``      allows users to register                       true (*deprecated in 0.3.0*)
``REACT_APP_THUNDERFOREST_API_KEY``   ThunderForest API key                          (*deprecated in 0.x.x*, use ``TILE_SERVER_URL`` **and** ``MAP_ATTRIBUTION`` instead)
``TILE_SERVER_URL``                   Tile server URL (with api key if needed)       ``https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png``
``MAP_ATTRIBUTION``                   Map attribution (if using another tile server) ``&copy; <a href="http://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors``
``UI_URL``                            application URL                                no default value, must be initialized
``EMAIL_URL``                         email URL with credentials                     no default value, must be initialized (see below)
``SENDER_EMAIL``                      application sender email address               no default value, must be initialized
``REDIS_URL``                         Redis instance used by Dramatiq                local Redis instance
``WORKERS_PROCESSES``                 number of process used by Dramatiq             no default value, must be initialized
===================================== ============================================== ====================================

.. warning::
    Since FitTrackee 0.3.0, some applications parameters are now stored in database.
    Related environment variables are needed to initialize database.

Emails
^^^^^^
*new in 0.3.0*

To send emails, a valid ``EMAIL_URL`` must be provided:

- with an unencrypted SMTP server: ``smtp://username:password@smtp.example.com:25``
- with SSL: ``smtp://username:password@smtp.example.com:465/?ssl=True``
- with STARTTLS: ``smtp://username:password@smtp.example.com:587/?tls=True``


Map tile server
^^^^^^^^^^^^^^^
*new in 0.x.x*

Default tile server is now **OpenStreetMap**'s standard tile layer (if environment variables are not initialized).
The tile server can be changed by updating ``TILE_SERVER_URL`` and ``MAP_ATTRIBUTION`` variables (`list of tile servers <https://wiki.openstreetmap.org/wiki/Tile_servers>`__).

To keep using ThunderForest Outdoors, the configuration is:

- ``TILE_SERVER_URL=https://{s}.tile.thunderforest.com/outdoors/{z}/{x}/{y}.png?apikey=XXXX`` where **XXXX** is ThunderForest API key
- ``MAP_ATTRIBUTION=&copy; <a href="http://www.thunderforest.com/">Thunderforest</a>, &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors``

.. note::
    Check the terms of service of tile provider for map attribution