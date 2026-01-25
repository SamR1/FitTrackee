Upgrade
#######

.. danger::
    If you are upgrading to version 1.0, additional steps are required, see `Upgrading to 1.0.x <upgrade.html#upgrading-to-1-0-x>`__.

.. warning::
    Before upgrading, make a backup of all data:

    - database (with `pg_dump <https://www.postgresql.org/docs/current/app-pgdump.html>`__ for instance)
    - upload directory (see `Environment variables <environments_variables.html#envvar-UPLOAD_FOLDER>`__)

.. warning::

    For now, releases do not follow `semantic versioning <https://semver.org>`__. Any version may contain backward-incompatible changes.

.. note::
    Depending on the operating system and the version of Python installed, additional dependencies may be required, such as **gcc** or **libgdal-dev**.


From PyPI
*********

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
************

.. warning::
    | Only if **FitTrackee** was initially installed from sources.



Prod environment
================

- Stop the application

- Change to the directory where FitTrackee directory is located

- Download the last release (for now, it is the release v1.1.0) and overwrite existing files:

.. code:: bash

   $ wget https://github.com/SamR1/FitTrackee/archive/v1.1.0.tar.gz
   $ tar -xzf v1.1.0.tar.gz
   $ cp -R FitTrackee-1.1.0/* FitTrackee/
   $ cd FitTrackee

- Update **.env** if needed (see `Environment variables <environments_variables.html>`__).

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


Dev environment
===============

- Stop the application and pull the repository:

.. code:: bash

   $ git pull

- Update **.env** if needed (see `Environment variables <environments_variables.html>`__).

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

Upgrading to 1.0.x
******************

.. note::
    This paragraph describes the upgrade from a version prior to 1.0.0 to version 1.0.x.

The version 1.0.0 introduces major changes on workout file processing to improve performances and ease the implementation of the next features:

- data displayed in the workout chart are stored in the database,
- and segments geometry is also stored.

This last change requires `PostGIS <https://postgis.net/>`__ extension, which adds geospatial capabilities to the `PostgreSQL <https://www.postgresql.org/>`__ database.


Instructions for upgrade
========================

.. warning::
    These actions must be performed before upgrading to version 1.1.0.

.. warning::
    Before upgrading, make a backup of all data:

    - database (with `pg_dump <https://www.postgresql.org/docs/current/app-pgdump.html>`__ for instance)
    - upload directory (see `Environment variables <environments_variables.html#envvar-UPLOAD_FOLDER>`__)

.. note::
    Depending on the operating system and the version of Python installed, additional dependencies may be required, such as **gcc** or **libgdal-dev**.

From PyPI or sources
--------------------

**PostGIS** must be installed on your operating system.
You can find instructions for your OS on `PostGIS documentation <https://postgis.net/documentation/getting_started/>`_.

Here are the instructions for installation on ArchLinux with `yay <https://github.com/Jguer/yay>`__ (to adapt depending on your operating system):

- stop the application and workers
- install **PostGIS** on the server running the database

  .. code-block:: bash

      $ yay postgis

- add **PostGIS** extension to the database

  .. code-block:: bash

      $ psql -U <SUPER_USER> -d <FITTRACKEE_DATABASE_NAME> -c 'CREATE EXTENSION IF NOT EXISTS postgis;'

- if the server running the application is different from the server running the database, install `gdal <https://gdal.org/en/stable/download.html#binaries>`__ library on the server running the application (**GDAL** is installed with **PostGIS**)

  .. code-block:: bash

      $ yay gdal

- update **fittrackee** (see `instructions for upgrade <upgrade.html>`__)
- run database migrations
- start application and workers

With Docker
-----------

- stop the application, workers and database

  .. code-block:: bash

      $ docker compose stop

- change the database ``postgres`` image in ``docker-compose.yml`` to ``postgis/postgis`` (keep the same **PostgreSQL** version), for instance:

  .. code-block:: diff

      -   image: postgres:17-alpine
      +   image: postgis/postgis:17-3.5-alpine

.. warning::

    | There is no official image for PostGIS on ARM platforms yet, see `issue on GitHub <https://github.com/postgis/docker-postgis/issues/216>`__.
    | The workaround is to build PostGIS image locally.

- start only the database

  .. code-block:: bash

      $ docker compose up fittrackee-db -d

- add **PostGIS** extension to the database

  .. code-block:: bash

      $ docker compose exec fittrackee-db psql -U <SUPER_USER> -d <FITTRACKEE_DATABASE_NAME> -c 'CREATE EXTENSION IF NOT EXISTS postgis;'
      CREATE EXTENSION

- update **fittrackee** version in ``docker-compose.yml``
- start the application, migrations should run without error


Workouts data update
====================

An new CLI option (``--add-missing-geometry``) allows to refresh workouts without geometry and chart data.

After upgrading **fittrackee**, run this command with other options depending on the number of workouts to update and the server capability, before enabling geospatial features on UI.

For instance to update the first 1,000 workouts created with a file:

.. code-block:: bash

    $ ftcli workouts refresh --add-missing-geometry --per-page 1000 -v

| This command can be re-executed until there are no more workouts to update.
| Once all workouts have been updated, enable geospatial features on the interface by setting the environment variable `ENABLE_GEOSPATIAL_FEATURES <environments_variables.html#envvar-ENABLE_GEOSPATIAL_FEATURES>`_  to ``True`` in ``.env``.

.. important::
    The version 1.1.0 requires all workouts to be updated (``--add-missing-geometry`` option is removed in v1.1.0).