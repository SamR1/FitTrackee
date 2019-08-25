Installation
############

This application is written in Python (API) and Javascript (client):

- API:
    - Flask
    - `gpxpy <https://github.com/tkrajina/gpxpy>`__ to parse gpx files
    - `staticmap <https://github.com/komoot/staticmap>`__ to generate a static map image from gpx coordinates
    - `python-forecast.io <https://github.com/ZeevG/python-forecast.io>`__ to fetch weather data from `Dark Sky <https://darksky.net>`__ (former forecast.io)
- Client:
    - React/Redux
    - `Leaflet <https://leafletjs.com/>`__ to display map
    - `Recharts <https://github.com/recharts/recharts>`__ to display charts with elevation and speed

Sports and weather icons are made by `Freepik <https://www.freepik.com/>`__ from `www.flaticon.com <https://www.flaticon.com/>`__.

Prerequisites
~~~~~~~~~~~~~

-  PostgreSQL database (10+)
-  Python 3.7+
-  `Yarn <https://yarnpkg.com>`__ and
   `serve <https://github.com/zeit/serve>`__
-  API key from `ThunderForest <http://thunderforest.com>`__
-  API key from `Dark Sky <https://darksky.net/dev>`__ [not mandatory]


Installation
~~~~~~~~~~~~

| The following steps describe an installation on Linux systems (tested
  on Debian and Arch).
| On other OS, some issues can be encountered and adaptations may be
  necessary.

Dev environment
^^^^^^^^^^^^^^^

-  Clone this repo:

.. code:: bash

   $ git clone https://github.com/SamR1/FitTrackee.git
   $ cd FitTrackee

-  Update **Makefile.config** file if needed and copy/paste the
   **ThunderForest** and **Dark Sky** API keys value in
   **Makefile.custom.config** file (see example). User registration can
   also be disabled in **Makefile.custom.config**.

-  Install Python virtualenv, React and all related packages and
   initialize the database:

.. code:: bash

   $ make install-dev
   $ make install-db

-  Start the server and the client:

.. code:: bash

   $ make serve

Open http://localhost:3000 and login (the email is ``admin@example.com``
and the password ``mpwoadmin``) or register

Prod environment
^^^^^^^^^^^^^^^^

.. warning::
    Note that FitTrackee is not production-ready yet

-  Download the last release (for now it is the beta release v0.2.0):

.. code:: bash

   $ wget https://github.com/SamR1/FitTrackee/archive/v0.2.0-beta.tar.gz
   $ tar -xzf v0.2.0-beta.tar.gz
   $ mv FitTrackee-0.2.0-beta FitTrackee
   $ cd FitTrackee

-  Update **Makefile.config** file if needed and copy/paste the
   **ThunderForest** and **Dark Sky** API keys value in
   **Makefile.custom.config** file (see example). User registration can
   also be disabled in **Makefile.custom.config**.

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

- Reinstall packages if needed:

.. code:: bash

   $ make install-dev

- Restart the server and the client:

.. code:: bash

   $ make serve


Prod environment
^^^^^^^^^^^^^^^^

``TODO``

