Administration
##############

.. versionadded:: 0.3.0

.. figure:: ../_images/administration-menu.png
   :alt: FitTrackee Administration

Application
***********

Only users if administration rights can access application administration.

Configuration
=============

.. versionchanged:: 0.6.0 added administrator email for contact
.. versionchanged:: 0.7.4 maximum size of workout file and maximum number of files in the zip archive updated
.. versionchanged:: 0.8.5 added maximum number of workouts for sport statistics
.. versionchanged:: 0.10.0 added maximum number of files for synchronous processing and maximum number of workouts displayed on global map

The following parameters can be set:

- active users limit (default: 0). If 0, registration is enabled (no limit defined).
- maximum size of workout file (individually uploaded or in a zip archive, default: 1Mb)
- maximum size of zip archive (default: 10Mb)
- maximum number of files in the zip archive (default: 10)
- maximum number of files for synchronous processing (default: 10). If the maximum number of files in the zip archive equals the maximum number of files for synchronous processing, asynchronous upload is disabled.

.. note::
  When upgrading to v0.10.0, asynchronous download is disabled, since both values are equal.

- maximum number of workouts for sport statistics (default: 10,000). If 0, all workouts are fetched to calculate statistics
- maximum number of workouts displayed on global map (default: 10,000), this value can not exceed 50,000 workouts

.. note::
  | The maximum number of workouts for statistics or the global map must be defined according to the server capabilities.
  | In the case of the global map, this value also has an impact on the rendering performance on the client side (depending on the browser and the capabilities of the device displaying the map).

- administrator email for contact

.. warning::
  | If several application workers are running (see `environment variable <../installation/environments_variables.html#envvar-APP_WORKERS>`__), it may be necessary to restart all the workers so that the changes are taken into account.
  | Updating timeout (see `environment variable <../installation/environments_variables.html#envvar-APP_TIMEOUT>`__) or server configuration may be necessary to handle large files (like `nginx <https://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size>`_ for instance).
  | Setting values that are too high for file size or number may cause errors.
  | If a weather data provider is configured, errors related to API limitations may occur.

.. note::
  If email sending is disabled, a warning is displayed.

About
=====

.. versionadded:: 0.7.13

| It is possible displayed additional information that may be useful to users in **About** page (like instance rules).
| Markdown syntax can be used.

Privacy policy
==============

.. versionadded:: 0.7.13

| A default privacy policy is available (originally adapted from the `Discourse <https://github.com/discourse/discourse>`__ privacy policy).
| A custom privacy policy can set if needed (Markdown syntax can be used). A policy update will display a message on users dashboard to review it.

.. note::
  Only the default privacy policy is translated (if the translation is available).


Moderation
**********

.. versionadded:: 0.9.0

Only users with administration or moderation rights can access moderation.

This page displays the list of reports, which can be filtered.

Administrators and moderators can manage a report:

- add a comment
- send a warning
- suspend or reactive workout or comment
- suspend or reactive user account
- mark report as resolved or unresolved

.. figure:: ../_images/report-in-administration.png
  :alt: Report on FitTrackee

.. note::
  Report content is visible regardless the visibility level.

| Users can appeal suspension or warning.
| Suspended user can only access his account, appeal the account suspension, request and data export or delete his account. His sessions and comments are no longer visible.


Equipment Types
***************

.. versionadded:: 0.8.0

Only users with administration rights can access equipment types administration.

.. figure:: ../_images/equipment-types-in-administration.png
  :alt: Equipment types administration on FitTrackee

It allows to enable or disable an equipment type in order to match disabled sports (a equipment type can be disabled even if equipment with this type exists)

Queued tasks
************

.. versionadded:: 0.10.0

Only users with administration rights can view queued tasks for user data export or workouts archive upload.

.. note::
  If no workers are running, `CLI <../cli.html>`__ commands allow to process queued tasks.


Sports
******

| Only users with administration rights can access sports administration.

.. figure:: ../_images/sports-administration.png
  :alt: Sports administration on FitTrackee

| It allows to enable or disable a sport (a sport can be disabled even if workout with this sport exists).


Users
*****

.. versionchanged:: 0.6.0  added user account activation, email and password update
.. versionchanged:: 0.9.0  added moderator and owner roles, updated administrator role

Only users with administration rights can access users administration.

Following roles are available:

- user

  - no moderation or administration rights

- moderator

  - can only access moderation entry in administration
  - can see reports
  - perform report actions

- administrator

  - has moderator rights
  - can access all entries in administration:

    - application
    - moderation
    - equipment types
    - sports
    - users

- owner

  - has admin rights
  - role can not be modified by other administrator/owner on application

.. note::

  Roles defined prior to version 0.9.0 remain unchanged.

Users administration displays the list of users, which can be filtered.

It is possible to edit a user in order to:

- update role. A user with owner role can not be modified by other users. Owner role can only be assigned or removed with **FitTrackee** CLI.
- activate his account
- update his email (in case his account is locked)
- reset his password (in case his account is locked). If email sending is disabled, it is only possible via `CLI <../cli.html>`__.

It is also possible to delete a user account.