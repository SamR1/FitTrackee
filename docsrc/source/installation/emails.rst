Emails
######

.. versionadded:: 0.3.0
.. versionchanged:: 0.5.3  Credentials and port can be omitted
.. versionchanged:: 0.6.5  Disable email sending
.. versionchanged:: 0.7.13  An email is sent when a data export archive is ready to download
.. versionchanged:: 0.7.24  Handle special characters in password
.. versionchanged:: 0.9.0  An email is sent after moderation action

To send emails, a valid ``EMAIL_URL`` must be provided:

- with an unencrypted SMTP server: ``smtp://username:password@smtp.example.com:25``
- with SSL: ``smtp://username:password@smtp.example.com:465/?ssl=True``
- with STARTTLS: ``smtp://username:password@smtp.example.com:587/?tls=True``

Credentials can be omitted: ``smtp://smtp.example.com:25``.
If ``:<port>`` is omitted, the port defaults to 25.

Password can be encoded if it contains special characters.
For instance with password ``passwordwith@and&and?``, the encoded password will be: ``passwordwith%40and%26and%3F``.

.. warning::
    | If the email URL is invalid, the application may not start.
    | Sending emails with Office365 may not work if SMTP auth is disabled.

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
