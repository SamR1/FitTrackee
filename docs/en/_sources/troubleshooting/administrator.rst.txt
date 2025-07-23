Administrator
#############


`FitTrackee fails to start`
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Check the database URL in `environment variables <../installation.html#envvar-DATABASE_URL>`__ if the following error is displayed in **gunicorn** logs:

  .. code::

     sqlalchemy.exc.NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgres

  The variable ``DATABASE_URL`` must start with ``postgresql://` (engine URLs starting with ``postgres://`` are no longer supported).

- Check the email URL in `environment variables <../installation.html#envvar-EMAIL_URL>`__ if the following error is displayed in **gunicorn** logs:

  .. code::

     fittrackee.emails.exceptions.InvalidEmailUrlScheme

  A valid ``EMAIL_URL`` must be provided (see `emails <../installation.html#emails>`__).


`Map images are not displayed but map is shown in Workout detail`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Check the path in `environment variables <../installation.html#envvar-UPLOAD_FOLDER>`__. ``UPLOAD_FOLDER`` must be set with an absolute path.


`Failed to upload or download files`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Check ``client_max_body_size`` in **nginx** config. Increase the value to handle larger files (see **nginx** `documentation <https://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size>`_).

- Increase **gunicorn** `timeout <https://docs.gunicorn.org/en/stable/settings.html#timeout>`__ value if the following error is displayed in gunicorn log: ``[CRITICAL] WORKER TIMEOUT``.


``RuntimeError: thread already started``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- | This error appears in task queue workers logs with `Flask-dramatiq <https://flask-dramatiq.readthedocs.io>`__ CLI on Python 3.13+.
  | The workaround is to use `Dramatiq <https://dramatiq.io>`__ CLI directly, for instance:

  .. code:: bash

    $ dramatiq fittrackee.tasks:broker --processes=2 --log-file=dramatiq.log


``staticmap3.staticmap - ERROR - request failed [None]``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- | FitTrackee v0.10+ introduces a new environnement variable ``STATICMAP_CACHE_DIR``, for **Static Map 3** cache directory.
  | For docker installation, the directory must be writable for ``fittrackee`` user, see in ``docker-compose.yml`` example in the `repository <https://github.com/SamR1/FitTrackee/blob/master/docker-compose.yml>`__:

  .. code:: yaml

    volumes:
      - ${UPLOAD_DIR:-./data/uploads}:/usr/src/app/uploads
      - ${LOG_DIR:-./data/logs}:/usr/src/app/logs
      - ${STATICMAP_CACHE_DIR:-./data/staticmap_cache}:/usr/src/app/.staticmap_cache
    post_start:
      - command: chown -R fittrackee:fittrackee /usr/src/app/uploads /usr/src/app/logs /usr/src/app/.staticmap_cache
        user: root
