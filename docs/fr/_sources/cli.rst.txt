Command line interface
######################

A command line interface (CLI) is available to manage database, OAuth2 tokens and users.

.. code-block:: bash

    $ ftcli
    Usage: ftcli [OPTIONS] COMMAND [ARGS]...

      FitTrackee Command Line Interface

    Options:
      --help  Show this message and exit.

    Commands:
      db      Manage database.
      oauth2  Manage OAuth2 tokens.
      users   Manage users.


Database
~~~~~~~~

``ftcli db drop``
"""""""""""""""""
.. versionadded:: 0.6.5

Empty database and delete uploaded files, only on development environments.


``ftcli db upgrade``
""""""""""""""""""""
.. versionadded:: 0.6.5

Apply migrations.


OAuth2
~~~~~~

``ftcli oauth2 clean``
""""""""""""""""""""""
.. versionadded:: 0.7.0

Remove tokens expired for more than provided number of days

.. cssclass:: table-bordered
.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Options
     - Description
   * - ``--days``
     - Number of days.



Users
~~~~~

``ftcli users clean_archives``
""""""""""""""""""""""""""""""
.. versionadded:: 0.7.13

Delete export requests and related archives created more than provided number of days.

.. cssclass:: table-bordered
.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Options
     - Description
   * - ``--days``
     - Number of days.


``ftcli users clean_tokens``
""""""""""""""""""""""""""""
.. versionadded:: 0.7.0

Remove blacklisted tokens expired for more than provided number of days.

.. cssclass:: table-bordered
.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Options
     - Description
   * - ``--days``
     - Number of days.


``ftcli users create``
""""""""""""""""""""""
.. versionadded:: 0.7.15

Create a user account.

.. note::
  - the newly created account is already active.
  - the CLI allows to create users when registration is disabled.


.. cssclass:: table-bordered
.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Arguments/options
     - Description
   * - ``USERNAME``
     - Username.
   * - ``--email EMAIL``
     - User email (mandatory).
   * - ``--password PASSWORD``
     - User password (if not provided, a random password is generated).



``ftcli users export_archives``
"""""""""""""""""""""""""""""""
.. versionadded:: 0.7.13

Process incomplete user export requests.
Can be used if redis is not set (no dramatiq workers running).

.. cssclass:: table-bordered
.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Options
     - Description
   * - ``--max``
     - Maximum number of export requests to process.


``ftcli users update``
""""""""""""""""""""""
.. versionadded:: 0.6.5

Modify a user account (admin rights, active status, email and password).

.. cssclass:: table-bordered
.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Arguments/options
     - Description
   * - ``USERNAME``
     - Username.
   * - ``--set-admin BOOLEAN``
     - Add/remove admin rights (when adding admin rights, it also activates user account if not active).
   * - ``--activate``
     - Activate user account.
   * - ``--reset-password``
     - Reset user password (a new password will be displayed).
   * - ``--update-email EMAIL``
     - Update user email.
