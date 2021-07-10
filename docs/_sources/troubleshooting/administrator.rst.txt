Administrator
#############


`FitTrackee fails to start`
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Check the database URL in `Environment variables <../installation.html#envvar-DATABASE_URL>`__ if the following error is displayed in **gunicorn** logs:

.. code::

   sqlalchemy.exc.NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgres

It must start with `postgresql://` (engine URLs starting with `postgres://` are no longer supported).