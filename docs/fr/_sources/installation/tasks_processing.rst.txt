Tasks processing
################

.. versionadded:: 0.3.0
.. versionchanged:: 0.10.0 Add ``TASKS_TIME_LIMIT`` variable

Tasks processing is done using `Dramatiq <https://dramatiq.io/>`_. It requires Redis and is used for email sending, user data exports and workouts archives uploads.

.. note::
    If no workers are running, `CLI <../cli.html>`__ commands allow to process queued tasks.

The following environment variables must be set:

- `REDIS_URL <environments_variables.html#envvar-REDIS_URL>`__: Redis instance used by **Dramatiq** and **Flask-Limiter**.
- `WORKERS_PROCESSES <environments_variables.html#envvar-WORKERS_PROCESSES>`__: Number of processes used by **Dramatiq**.
- `DRAMATIQ_LOG <environments_variables.html#envvar-DRAMATIQ_LOG>`__: Path to **Dramatiq** log file.

To avoid long-running tasks for user data exports and workouts archives uploads, a time limit is set:

- `TASKS_TIME_LIMIT <environments_variables.html#envvar-TASKS_TIME_LIMIT>`__: Timeout in seconds for **Dramatiq** task execution. The default value is 1800 seconds (30 minutes).

To start task queue workers, run the following command after virtual environment activation:

.. code-block:: bash

    $ dramatiq fittrackee.tasks:broker --processes=$WORKERS_PROCESSES --log-file=$DRAMATIQ_LOG

.. note::
    | It is also possible to start task queue workers with **Flask-Dramatiq** CLI, but it is recommended to use **Dramatiq** CLI instead for now.

It is possible to run queues independently, for instance for workouts archive uploads:

.. code-block:: bash

    $ dramatiq fittrackee.tasks:broker --processes=2 -Q fittrackee_workouts

The following queues are available:

- ``fittrackee_emails``: for emails sending (priority: high)
- ``fittrackee_users_exports``: for user data exports (priority: medium)
- ``fittrackee_workouts``: for workouts archive uploads (priority: medium)

Run ``dramatiq -h`` to see a list of the available commands.