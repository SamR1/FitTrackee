Administrator
#############


`FitTrackee fails to start`
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Check the database URL in `environment variables <../installation.html#envvar-DATABASE_URL>`__ if the following error is displayed in **gunicorn** logs:

  .. code::

     sqlalchemy.exc.NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgres

  It must start with `postgresql://` (engine URLs starting with `postgres://` are no longer supported).

- Check the email URL in `environment variables <../installation.html#envvar-EMAIL_URL>`__ if the following error is displayed in **gunicorn** logs:

  .. code::

     fittrackee.emails.exceptions.InvalidEmailUrlScheme

  A valid ``EMAIL_URL`` must be provided (see `emails <../installation.html#emails>`__).