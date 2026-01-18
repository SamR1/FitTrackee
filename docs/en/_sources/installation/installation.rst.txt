Installation
############

| The following steps describe an installation on Linux systems (tested with ArchLinux-based OS and Ubuntu on CI).
| On other operating systems, some issues can be encountered and adaptations may be necessary.

.. note::
  Other installation guides are available thanks to contributors:

  - `Installation on Uberspace Web hosting <https://lab.uberspace.de/guide_fittrackee/>`__ (Fittrackee 0.7.25)
  - `Installation on Debian 12 net install (guide in German) <https://speefak.spdns.de/oss_lifestyle/fittrackee-installation-unter-debian-12/>`__ (Fittrackee 0.7.31)


.. warning::
    | Note that **FitTrackee** is under heavy development, some features may be unstable.

.. note::
    Depending on the operating system and the version of Python installed, additional dependencies may be required, such as **gcc** or **libgdal-dev**.

From PyPI
*********

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

- Initialize environment variables, see `Environment variables <environments_variables.html>`__

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
    | To start application and workers with **systemd** service, see `Deployment <deployment.html>`__.

- Open http://localhost:5000 and register

- To set owner role to the newly created account, use the following command line:

.. code:: bash

   $ ftcli users update <username> --set-role owner

.. note::
    If the user account is inactive, it activates it.

From sources
************

.. warning::
    | Since **FitTrackee** 0.2.1, Python packages installation needs Poetry.
    | For more information, see `Poetry Documentation <https://python-poetry.org/docs/#installation>`__

.. note::
    | To keep virtualenv in project directory, update Poetry `configuration <https://python-poetry.org/docs/configuration/#virtualenvsin-project>`__.

    .. code-block:: bash

        $ poetry config virtualenvs.in-project true

Production environment
======================

.. warning::
    | Note that FitTrackee is under heavy development, some features may be unstable.

-  Download the last release (for now, it is the release v1.1.0b2):

.. code:: bash

   $ wget https://github.com/SamR1/FitTrackee/archive/1.1.0b2.tar.gz
   $ tar -xzf v1.1.0b2.tar.gz
   $ mv FitTrackee-1.1.0b2 FitTrackee
   $ cd FitTrackee

-  Create **.env** from example and update it
   (see `Environment variables <environments_variables.html>`__).

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


Dev environment
===============

-  Clone this repo:

.. code:: bash

   $ git clone https://github.com/SamR1/FitTrackee.git
   $ cd FitTrackee

-  Create **.env** from example and update it
   (see `Environment variables <environments_variables.html>`__).

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


Docker
******

.. versionadded:: 0.4.4
.. versionchanged:: 0.5.0 add client application for development
.. versionchanged:: 0.8.13 add docker image for production


Production
==========

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

- create ``.env`` from example (``.env.docker.example``) and update it (see `Environment variables <environments_variables.html>`__).

- to start the application:

.. code:: bash

   $ docker compose up -d

.. warning::

    Migrations are executed at startup. Please backup data before updating FitTrackee image version.

- to run a CLI command, for instance to give admin rights:

.. code:: bash

   $ docker compose exec fittrackee ftcli users update <username> --set-role admin


Development
===========

- To install and run **FitTrackee**:

.. code-block:: bash

    $ git clone https://github.com/SamR1/FitTrackee.git
    $ cd FitTrackee
    $ make docker-run

- Open http://localhost:5000 and register.

.. note::

  | To change ``fittrackee`` container port when running containers with Makefile commands, create a ``.env`` file with `HOST_APP_PORT <environments_variables.html#envvar-HOST_APP_PORT>`__.
  | For example:

  .. code-block::

    export HOST_APP_PORT=5001


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
******

.. versionadded:: 1.0.4

Development
===========

You can use the **Dev Container** without the **debug configuration** and vice versa.
Dev Container is strongly recommended on Windows because of path handling issues.


Dev Container
-------------
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
---------------------------
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
