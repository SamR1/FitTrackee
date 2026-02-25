Administrator
#############


FitTrackee fails to start
~~~~~~~~~~~~~~~~~~~~~~~~~

- Check the database URL in `environment variables <../installation.html#envvar-DATABASE_URL>`__ if the following error is displayed in **gunicorn** logs:

  .. code::

     sqlalchemy.exc.NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgres

  The variable ``DATABASE_URL`` must start with ``postgresql://` (engine URLs starting with ``postgres://`` are no longer supported).

- Check the email URL in `environment variables <../installation.html#envvar-EMAIL_URL>`__ if the following error is displayed in **gunicorn** logs:

  .. code::

     fittrackee.emails.exceptions.InvalidEmailUrlScheme

  A valid ``EMAIL_URL`` must be provided (see `emails <../installation.html#emails>`__).


Map images are not displayed but map is shown in Workout detail
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Check the path in `environment variables <../installation.html#envvar-UPLOAD_FOLDER>`__. ``UPLOAD_FOLDER`` must be set with an absolute path.


Failed to upload or download files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Check ``client_max_body_size`` in **nginx** config. Increase the value to handle larger files (see **nginx** `documentation <https://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size>`_).

- Increase **gunicorn** `timeout <https://docs.gunicorn.org/en/stable/settings.html#timeout>`__ value if the following error is displayed in gunicorn log: ``[CRITICAL] WORKER TIMEOUT``.


``RuntimeError: thread already started``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- | This error appears in task queue workers logs with `Flask-dramatiq <https://flask-dramatiq.readthedocs.io>`__ CLI on Python 3.13+.
  | The workaround is to use `Dramatiq <https://dramatiq.io>`__ CLI directly, for instance:

  .. code:: bash

    $ dramatiq fittrackee.tasks:broker --processes=2 --log-file=dramatiq.log


``staticmap3.staticmap - ERROR - request failed [None]`` or "error when generating map image"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- | FitTrackee v0.10+ introduces a new environment variable ``STATICMAP_CACHE_DIR``, for **Static Map 3** cache directory.
  | For docker installation, the directory must be writable for ``fittrackee`` user, see in ``docker-compose.yml`` example in the `repository <https://github.com/SamR1/FitTrackee/blob/main/docker-compose.yml>`__:

  .. code:: yaml

    volumes:
      - ${UPLOAD_DIR:-./data/uploads}:/usr/src/app/uploads
      - ${LOG_DIR:-./data/logs}:/usr/src/app/logs
      - ${STATICMAP_CACHE_DIR:-./data/staticmap_cache}:/usr/src/app/.staticmap_cache
    post_start:
      - command: chown -R fittrackee:fittrackee /usr/src/app/uploads /usr/src/app/logs /usr/src/app/.staticmap_cache
        user: root


``PermissionError: [Errno 13] Permission denied: '/usr/src/app/fittrackee/uploads'``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- This error occurs when `UPLOAD_FOLDER <../installation/environments_variables.html#envvar-UPLOAD_FOLDER>`__ is not set in ``.env`` used by the docker container, see `.env.docker.example <https://github.com/SamR1/FitTrackee/blob/main/.env.docker.example>`__:

  .. code:: yaml

    export UPLOAD_FOLDER=/usr/src/app/uploads


``psycopg2.errors.UndefinedObject: ERROR:  type "geometry" does not exist``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- | This error occurs when **PostGIS** extension is not installed, required with **FitTrackee** v1+.
  | To install it, see `installation instructions <../installation.html#upgrade>`__ or `Upgrading to 1.x <../upgrading-to-1.0.0.html>`__


Workouts created with a file are not displayed on the workouts map
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- | If a workout has be created before **FitTrackee** 1.0.0, it needs to be refreshed to generate the geometry used to display the map.
  | See `Upgrading to 1.x <../upgrading-to-1.0.0.html>`__ for instructions to recalculate all workouts with a CLI command.


``OSError: [Errno 98] Address already in use``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- | Since **gunicorn** 25.1.0, a `control interface <https://gunicorn.org/guides/gunicornc/>`__ is started by default and that may interfere with **prometheus** middleware (used by **dramatiq**).
  | A workaround for now is to disable this interface by adding ``--no-control-socket`` option to **gunicorn** command.
