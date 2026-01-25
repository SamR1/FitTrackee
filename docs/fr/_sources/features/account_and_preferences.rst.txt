Account & preferences
#####################

Account
*******

.. versionchanged:: 0.3.0 password reset
.. versionchanged:: 0.6.0 email change
.. versionchanged:: 0.7.13 data export
.. versionchanged:: 0.10.0 notification when data export is completed

Users can create, update and deleted their account.

.. figure:: ../_images/user-account-edition.png
   :alt: User account edition on FitTrackee

They can reset his password, can change their email address and update their profile image.

| They can also request the export of their data.
| It generates a zip archive containing 2 ``json`` files (user info and workouts data) and all uploaded files.
| A notification is displayed after export completion.

.. note::
  For now, it's not possible to import these files into another **FitTrackee** instance.


Preferences
***********

.. versionchanged:: 0.5.0 added interface theme and imperial system
.. versionchanged:: 0.6.11 added ascent preference
.. versionchanged:: 0.7.3 added date/time format
.. versionchanged:: 0.7.15 added elevation chart display
.. versionchanged:: 0.7.16 added max speed calculation strategy
.. versionchanged:: 0.7.27 added interface theme
.. versionchanged:: 0.9.0 added follow requests approval, profile visibility in users directory, workout visibilities
.. versionchanged:: 0.10.0 added heart rate visibility
.. versionchanged:: 0.10.3 event for segments creation
.. versionchanged:: 0.11.0 preferred displayed for charts
.. versionchanged:: 1.1.0 missing elevation processing

.. figure:: ../_images/user-preferences.png
   :alt: User Preferences on FitTrackee

It is possible to set interface preference:

- language, timezone, date format and first day of week
- interface theme (light, dark or according to browser preferences)

For account, it is possible to set:

- follow requests approval: manually (default) or automatically
- profile visibility in users directory: hidden (default) or displayed

For workouts, it is possible to choose:

- between metric system and imperial system for distance, elevation and speed display
- to display or hide ascent records and total on Dashboard
- the preferred display for workout chart:

  - all data on a single chart
  - each data displayed on a different chart

- elevation chart axis start: zero or minimum altitude
- to exclude extreme values (which may be GPS errors) when calculating the maximum speed (by default, extreme values are excluded)

  .. note::
    Changing this preference will only affect next file uploads.

- missing elevation processing if an elevation service is set:

  - none
  - OpenElevation (raw data)
  - OpenElevation (smoothed data)
  - Valhalla

- default visibility for workout data, analysis, map and heart rate.

The type of events that generate segment when uploading .fit files can also be set:

- all pause events,
- only manual pause,
- none.


Sports preferences
******************

.. versionadded:: 0.5.0
.. versionchanged:: 0.8.0 added default equipment
.. versionchanged:: 1.1.0 added pace/speed display

.. figure:: ../_images/sport-preference.png
   :alt: Sport Preferences on FitTrackee

The following sport preferences can be set:

- change sport color (used for sport image and charts)
- can override stopped speed threshold (for next uploaded gpx files)
- disable/enable a sport
- define default `equipment <equipment.html>`__.
- set pace/speed display for Hiking, Running, Trail and Walking:

  - pace
  - speed
  - pace and speed

  .. note::
    | If a sport is disabled by an administrator, it can not be enabled by a user. In this case, it will only appear in preferences if the user has workouts and only sport color can be changed.
    | A disabled sport (by admin or user) will not appear in dropdown when **adding a workout**.
    | A workout with a disabled sport will still be displayed in the application.

Quick edit is also available in order to change color, activate sport, update stopped speed threshold, or reset preferences.

.. figure:: ../_images/sports-quick-edition.png
   :alt: Sports edition on FitTrackee

Follow requests
***************

.. versionadded:: 0.9.0

Users can view follow requests to approve or reject.

.. figure:: ../_images/follow-requests.png
   :alt: Follow requests on FitTrackee


They can display blocked users.

.. figure:: ../_images/blocked-users.png
   :alt: Blocked users on FitTrackee

Moderation
**********

Users can view received warnings, sanctions, and appeal.

.. figure:: ../_images/sanctions.png
   :alt: Moderation on FitTrackee

.. figure:: ../_images/sanction-detail.png
   :alt: Sanction detail on FitTrackee

Notifications
*************

.. versionadded:: 0.9.0

Users can update notification preferences.

.. figure:: ../_images/notifications-preferences.png
   :alt: Notifications preferences on FitTrackee

Messages
********

.. versionadded:: 1.0.0

Users can update messages preferences.

.. figure:: ../_images/messages-preferences.png
   :alt: Messages preferences on FitTrackee


Archive uploads
***************

.. versionadded:: 0.10.0

Users can view, interrupt and delete tasks for asynchronous uploads.

.. figure:: ../_images/async-uploads-list.png
   :alt: Archive uploads list on FitTrackee

.. figure:: ../_images/async-upload-detail.png
   :alt: Archive uploads detail on FitTrackee