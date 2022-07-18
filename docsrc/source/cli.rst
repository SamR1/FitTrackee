Command line interface
######################

A command line interface (CLI) is available to manage database and users.

.. code-block:: bash

    $ ftcli
    Usage: ftcli [OPTIONS] COMMAND [ARGS]...

      FitTrackee Command Line Interface

    Options:
      --help  Show this message and exit.

    Commands:
      db     Manage database.
      users  Manage users.

.. warning::
    | The following commands are now deprecated and will be removed in a next version:
    | - ``fittrackee_set_admin``
    | - ``fittrackee_upgrade_db``


Database
~~~~~~~~

``ftcli db upgrade``
""""""""""""""""""""
.. versionadded:: 0.6.5

Apply migrations.


``ftcli db drop``
"""""""""""""""""
.. versionadded:: 0.6.5

Empty database and delete uploaded files, only on development environments.



Users
~~~~~

``ftcli users update``
""""""""""""""""""""""
.. versionadded:: 0.6.5

Modify a user account (admin rights, active status, email and password).

.. cssclass:: table-bordered
.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Options
     - Description
   * - ``--set-admin BOOLEAN``
     - Add/remove admin rights (when adding admin rights, it also activates user account if not active).
   * - ``--activate``
     - Activate user account.
   * - ``--reset-password``
     - Reset user password (a new password will be displayed).
   * - ``--update-email EMAIL``
     - Update user email.
