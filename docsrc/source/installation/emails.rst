Emails
######

.. versionadded:: 0.3.0
.. versionchanged:: 0.5.3  Credentials and port can be omitted
.. versionchanged:: 0.6.5  Disable email sending
.. versionchanged:: 0.7.13  An email is sent when a data export archive is ready to download
.. versionchanged:: 0.7.24  Handle special characters in password
.. versionchanged:: 0.9.0  An email is sent after moderation action
.. versionchanged:: 1.3.1  Add check on ``SENDER_EMAIL`` at startup

To send emails, a valid ``EMAIL_URL`` and ``EMAIL_SENDER`` must be provided. For ``EMAIL_URL`` some example formats are:

- with an unencrypted SMTP server: ``smtp://username:password@smtp.example.com:25``
- with SSL: ``smtp://username:password@smtp.example.com:465/?ssl=True``
- with STARTTLS: ``smtp://username:password@smtp.example.com:587/?tls=True``

Credentials can be omitted: ``smtp://smtp.example.com:25``.
If ``:<port>`` is omitted, the port defaults to 25.

Password can be encoded if it contains special characters.
For instance with password ``passwordwith@and&and?``, the encoded password will be: ``passwordwith%40and%26and%3F``.

.. warning::
    | If the email URL is invalid or if the sender email is not set, the application may not start.
    | Sending emails with Office365 may not work if SMTP auth is disabled.

.. note::
    | Some SMTP providers (like GMail) may ignore the sender email and use the email address associated with the SMTP account instead. For Gmail, the workaround is to create an alias.

.. warning::
     | Since 0.6.0, newly created accounts must be confirmed (an email with confirmation instructions is sent after registration).

Emails sent by FitTrackee are:

- account confirmation instructions
- password reset request
- email change (to old and new email addresses)
- password change
- notification when a data export archive is ready to download
- suspension and warning
- suspension and warning lifting
- rejected appeal

.. note::
   On single-user instance, it is possible to disable email sending with an empty `EMAIL_URL <environments_variables.html#envvar-EMAIL_URL>`__ (in this case, no need to start **Dramatiq** workers).

A `CLI <../cli.html#ftcli-users-update>`__ is available to activate account, modify email and password and handle data export requests.
