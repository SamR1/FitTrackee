API rate limits
###############

.. versionadded:: 0.7.0
.. versionchanged:: 1.0.4 Remove ``API_RATE_LIMITS`` default value in order to disable only rate limits when Redis is set

| If `API_RATE_LIMITS <environments_variables.html#envvar-API_RATE_LIMITS>`__ environment variable is not empty and **Redis** available, API rate limits are managed by `Flask-Limiter <https://flask-limiter.readthedocs.io/en/stable>`_, based on IP with fixed window strategy.

.. note::
    | If no Redis instance is available for rate limits, FitTrackee can still start.

| All endpoints are subject to rate limits, except endpoints serving assets.
| Limits are configured by setting the environment variable ``API_RATE_LIMITS``, for example ``300 per 5 minutes`` (see `Flask-Limiter documentation for notation <https://flask-limiter.readthedocs.io/en/stable/configuration.html#rate-limit-string-notation>`_).
| Multiple rate limits must be separated by a comma, for instance:

.. code-block::

    export API_RATE_LIMITS="200 per day,50 per hour"

**Flask-Limiter** provides a `Command Line Interface <https://flask-limiter.readthedocs.io/en/stable/cli.html>`_ for maintenance and diagnostic purposes.

.. code-block:: bash

    $ flask limiter
    Usage: flask limiter [OPTIONS] COMMAND [ARGS]...

      Flask-Limiter maintenance & utility commands

    Options:
      --help  Show this message and exit.

    Commands:
      clear   Clear limits for a specific key
      config  View the extension configuration
      limits  Enumerate details about all routes with rate limits

.. note::
    | Rate limits can be managed by other applications, like `nginx <https://nginx.org/en/docs/http/ngx_http_limit_req_module.html>`__.

