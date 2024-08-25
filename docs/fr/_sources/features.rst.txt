Features
########

| **FitTrackee** allows you to store and display **gpx** files and some statistics from your **outdoor** activities.
| Equipments can be associated with workouts.
| For now, this app is kind of a single-user application. Even if several users can register, a user can only view his own workouts.

Gpx files are stored in an upload directory (**without encryption**).

With the default configuration, `Open Street Map <https://www.openstreetmap.org>`__ is used as tile server in Workout detail and for static map generation.


Workouts
^^^^^^^^
- 18 sports are supported:
     - Cycling (Sport)
     - Cycling (Transport)
     - Cycling (Trekking)  (*new in 0.7.27*)
     - Cycling (Virtual)  (*new in 0.7.3*)
     - Hiking
     - Mountain Biking
     - Mountain Biking (Electric)  (*new in 0.5.0*)
     - Mountaineering  (*new in 0.7.9*)
     - Open Water Swimming  (*new in 0.7.20*)
     - Paragliding  (*new in 0.7.19*)
     - Rowing  (*new in 0.5.0*)
     - Running
     - Skiing (Alpine) (*new in 0.5.0*)
     - Skiing (Cross Country)  (*new in 0.5.0*)
     - Snowshoes (*new in 0.5.2*)
     - Swimrun (*new in 0.8.7*)
     - Trail (*new in 0.5.0*)
     - Walking

- (*new in 0.5.0*) Stopped speed threshold used by `gpxpy <https://github.com/tkrajina/gpxpy>`_ is not the default one for the following sports (0.1 km/h instead of 1 km/h):
     - Hiking
     - Mountaineering
     - Open Water Swimming
     - Paragliding
     - Skiing (Cross Country)
     - Snowshoes
     - Swimrun
     - Trail
     - Walking

.. note::
  It can be overridden in user preferences.

.. note::
  | Except the stopped speed threshold, all sports are analyzed in the same way (no specificity taken into account for the moment).
  | Swimrun is displayed as a single activity with no difference between segments for now.

- Dashboard with month calendar displaying workouts and record. The week can start on Sunday or Monday (which can be changed in the user preferences). The calendar displays up to 100 workouts.
- Workout creation by uploading manually a gpx file or a zip archive containing a limited number of gpx files (related data are stored in database in metric system).

.. warning::
  | Only **gpx** files with time and elevation are supported (otherwise, errors may occur on upload).

.. note::
  | Calculated values may differ from values calculated by the application that originally generated the gpx files, in particular the maximum speed.

.. note::
  | For now, **FitTrackee** has no importer, but some `third-party tools <third_party_tools.html#importers>`__ allow you to import workouts.

- | A workout can even be created without gpx (the user must enter date, time, duration and distance).
  | Ascent and descent can also be provided (*new in 0.7.10*).
- | A workout with a gpx file can be displayed with map and charts (speed and elevation (if the gpx file contains elevation data, *updated in 0.7.20*)).
  | Controls allow full screen view and position reset (*new in 0.5.5*).
- | If **Visual Crossing** (*new in 0.7.11*) API key is provided, weather is displayed in workout detail. Data source is displayed in **About** page.
  | Wind is displayed, with an arrow indicating the direction (a tooltip can be displayed with the direction that the wind is coming **from**) (*new in 0.5.5*).
- An `equipment <features.html#equipments>`__ can be associated with a workout (*new in 0.8.0*). For now, only one equipment can be associated.
- Segments can be displayed.
- Workout gpx file can be downloaded (*new in 0.5.1*)
- Workout edition and deletion. User can add a note.
- User statistics, by time period (week, month, year) and sport:
    - totals:
        - total distance
        - total duration
        - total workouts
        - total ascent  (*new in 0.5.0*)
        - total descent  (*new in 0.5.0*)
    - averages:
        - average speed  (*new in 0.5.1*)
        - average distance  (*new in 0.8.5*)
        - average duration  (*new in 0.8.5*)
        - average workouts  (*new in 0.8.5*)
        - average ascent  (*new in 0.8.5*)
        - average descent  (*new in 0.8.5*)
- User statistics by sport (*new in 0.8.5*):
   - total workouts
   - distance (total and average)
   - duration (total and average)
   - average speed
   - ascent (total and average)
   - descent (total and average)
   - records

.. note::
  | There is a limit on the number of workouts used to calculate statistics to avoid performance issues. The value can be set in administration.
  | If the limit is reached, the number of workouts used is displayed.
  | The total number of workouts for a given sport is not affected by this limit.

- User records by sports:
    - average speed
    - farthest distance
    - highest ascent (*new in 0.6.11*, can be hidden, see user preferences)
    - longest duration
    - maximum speed

.. note::
  Records may differ from records displayed by the application that originally generated the gpx files.

- Workouts list.
    - The user can filter workouts on:
        - date
        - sports (only sports with workouts are displayed in sport dropdown)
        - equipment (only equipments with workouts are displayed in equipment dropdown) (*new in 0.8.0*)
        - title (*new in 0.7.15*)
        - notes (*new in 0.8.0*)
        - distance
        - duration
        - average speed
        - maximum speed
    - Workouts can be sorted by:
        - date
        - distance
        - duration
        - average speed

.. note::
    For now, only the owner of the workout can see it.


Account & preferences
^^^^^^^^^^^^^^^^^^^^^
- A user can create, update and deleted his account.
- The user must agree to the privacy policy to register. If a more recent policy is available, a message is displayed on the dashboard to review the new version (*new in 0.7.13*).
- On registration, the user account is created with selected language in dropdown as user preference (*new in 0.6.9*).
- After registration, the user account is inactive and an email with confirmation instructions is sent to activate it.
  A user with an inactive account cannot log in. (*new in 0.6.0*).

.. note::
  In case email sending is not configured, a `command line <cli.html#ftcli-users-update>`__ allows to activate users account.

- A user can reset his password (*new in 0.3.0*)
- A user can change his email address (*new in 0.6.0*)
- A user can set language, timezone and first day of week.
- A user can set the interface theme (light, dark or according to browser preferences) (*new in 0.7.27*).
- A user can choose between metric system and imperial system for distance, elevation and speed display (*new in 0.5.0*)
- A user can choose to display or hide ascent records and total on Dashboard (*new in 0.6.11*)
- A user can choose format used to display dates (*new in 0.7.3*)
- A user can choose elevation chart axis start: zero or minimum altitude (*new in 0.7.15*)
- A user can choose to exclude extreme values (which may be GPS errors) when calculating the maximum speed (by default, extreme values are excluded) (*new in 0.7.16*)

.. note::
  Changing this preference will only affect next file uploads.

- A user can set sport preferences (*new in 0.5.0*):
     - change sport color (used for sport image and charts)
     - can override stopped speed threshold (for next uploaded gpx files)
     - disable/enable a sport
     - define default `equipments <features.html#equipments>`__ (*new in 0.8.0*).

.. note::
  | If a sport is disabled by an administrator, it can not be enabled by a user. In this case, it will only appear in preferences if the user has workouts and only sport color can be changed.
  | A disabled sport (by admin or user) will not appear in dropdown when **adding a workout**.
  | A workout with a disabled sport will still be displayed in the application.

- | A user can request a data export (*new in 0.7.13*).
  | It generates a zip archive containing 2 ``json`` files (user info and workouts data) and all uploaded gpx files.

.. note::
  For now, it's not possible to import these files into another **FitTrackee** instance.

Equipments
^^^^^^^^^^
(*new in 0.8.0*)

- A user can create equipments that can be associated with workouts.
- The following equipment types are available, depending on the sport:
    - Shoes: Hiking, Mountaineering, Running, Trail and Walking,
    - Bike: Cycling (Sport, Transport, Trekking), Mountain Biking and Mountain Biking (Electric),
    - Bike Trainer: Cycling (Virtual),
    - Kayak/Boat: Rowing,
    - Skis: Skiing (Alpine and Cross Country),
    - Snowshoes: Snowshoes.
- Equipment is visible only to its owner.
- For now only, only one piece of equipment can be associated with a workout.
- Following totals are displayed for each piece of equipment:
    - total distance
    - total duration
    - total workouts

.. note::
  | In case of an incorrect total (although this should not happen), it is possible to recalculate totals.

- It is possible to define default equipments for sports: when adding a workout, the equipment will automatically be displayed in the dropdown list depending on selected sport.
- An equipment can be edited (label, equipment type, description, active status and default sports).

.. warning::
  | Changing equipment type will remove all existing workouts associations for that piece of equipment and default sports.

- Deactivated equipment will not appear in dropdown when **a workout is added**. It remains displayed in the details of the workout, to which it was associated before being deactivated.

.. note::
  | An equipment type can be deactivated by an administrator.

OAuth Apps
^^^^^^^^^^
(*new in 0.7.0*)

- A user can create `clients <oauth.html>`__ for third-party applications.

Administration
^^^^^^^^^^^^^^
(*new in 0.3.0*)

Application
"""""""""""

**Configuration**

The following parameters can be set:

- active users limit (default: 0). If 0, registration is enabled (no limit defined).
- maximum size of gpx file (individually uploaded or in a zip archive, default: 1Mb) (*changed in 0.7.4*)
- maximum size of zip archive (default: 10Mb)
- maximum number of files in the zip archive (default: 10) (*changed in 0.7.4*)
- maximum number of workouts for sport statistics (default: 10.000). If 0, all workouts are fetched to calculate statistics (*new in 0.8.5*)
- administrator email for contact (*new in 0.6.0*)

.. warning::
  Updating server configuration may be necessary to handle large files (like `nginx <https://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size>`_ for instance).

.. note::
  If email sending is disabled, a warning is displayed.

**About**

(*new in 0.7.13*)

| It is possible displayed additional information that may be useful to users in **About** page.
| Markdown syntax can be used.


**Privacy policy**

(*new in 0.7.13*)

| A default privacy policy is available (originally adapted from the `Discourse <https://github.com/discourse/discourse>`__ privacy policy).
| A custom privacy policy can set if needed (Markdown syntax can be used). A policy update will display a message on users dashboard to review it.

.. note::
  Only the default privacy policy is translated (if the translation is available).

Users
"""""

- display and filter users list
- edit a user to:

  - add/remove administration rights
  - activate his account (*new in 0.6.0*)
  - update his email (in case his account is locked) (*new in 0.6.0*)
  - reset his password (in case his account is locked) (*new in 0.6.0*). If email sending is disabled, it is only possible via CLI.
- delete a user


Equipment Types
"""""""""""""""
- enable or disable an equipment type in order to match disabled sports (a equipment type can be disabled even if equipment with this type exists)  (*new in 0.8.0*)


Sports
""""""
- enable or disable a sport (a sport can be disabled even if workout with this sport exists)


Translations
^^^^^^^^^^^^
FitTrackee is available in the following languages (which can be saved in the user preferences):

- English
- French (*new in 0.2.3*)
- German (*new in 0.6.9*)
- Dutch (*new in 0.7.8*)
- Italian (*new in 0.7.10*)
- Galician (*new in 0.7.15*)
- Spanish (*new in 0.7.15*)
- Norwegian Bokmål (*new in 0.7.15*)
- Polish (*new in 0.7.18*)
- Basque (*new in 0.7.31*)
- Czech (*new in 0.8.1*)
- Portuguese (*new in 0.8.4*)

Application translations status on `Weblate <https://hosted.weblate.org/engage/fittrackee/>`__ (may differ from the released version):

.. figure:: https://hosted.weblate.org/widgets/fittrackee/-/multi-auto.svg


Screenshots
^^^^^^^^^^^^

Dashboard
"""""""""

.. figure:: _images/fittrackee_screenshot-01.png
   :alt: FitTrackee Dashboard


Workout detail
""""""""""""""
.. figure:: _images/fittrackee_screenshot-02.png
   :alt: FitTrackee Workout


Workouts list
"""""""""""""
.. figure:: _images/fittrackee_screenshot-03.png
   :alt: FitTrackee Workouts


Statistics
""""""""""
.. figure:: _images/fittrackee_screenshot-04.png
   :alt: FitTrackee Statistics

.. figure:: _images/fittrackee_screenshot-11.png
   :alt: FitTrackee Sport Statistics

Equipments
""""""""""
.. figure:: _images/fittrackee_screenshot-09.png
   :alt: FitTrackee Equipments

.. figure:: _images/fittrackee_screenshot-10.png
   :alt: FitTrackee Equipment detail


Administration
""""""""""""""
.. figure:: _images/fittrackee_screenshot-05.png
   :alt: FitTrackee Administration

.. figure:: _images/fittrackee_screenshot-06.png
   :alt: FitTrackee Sports Administration