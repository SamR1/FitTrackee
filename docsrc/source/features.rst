Features
########

List
~~~~

Administration
^^^^^^^^^^^^^^
(*new in 0.3.0*)

- **Application**

  The following parameters can be set:

  - active users limit. If 0, registration is enabled (no limit defined)
  - maximum size of uploaded files
  - maximum size of zip archive
  - maximum number of files in the zip archive. If an archive contains more files, only the configured number of files is processed, without raising errors.

  .. warning::
      Updating server configuration may be necessary to handle large files (like `nginx <https://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size>`_ for instance).


- **Users**

  - display users list and details
  - edit a user to add/remove administration rights
  - delete a user

- **Sports**

  - enable or disable a sport (a sport can be disabled even if workout with this sport exists)

Account & preferences
^^^^^^^^^^^^^^^^^^^^^
- A user can create, update and deleted his account
- A user can set language, timezone and first day of week.
- A user can reset his password (*new in 0.3.0*)
- A user can choose between metric system and imperial system for distance, elevation and speed display (*new in 0.5.0*)
- A user can set sport preferences (*new in 0.5.0*):
     - change sport color (used for sport image and charts)
     - can override stopped speed threshold (for next uploaded gpx files)
     - disable/enable a sport.

.. note::
  | If a sport is disabled by an administrator, it can not be enabled by a user. In this case, it will only appear in preferences if it has user's workouts and the user can only change sport color.
  | A disabled sport (by admin or user) will not appear in dropdown when **adding a workout**.
  | A workout with a disabled sport will still be displayed in the application.



Workouts
^^^^^^^^
- 11 sports are supported:
     - Cycling (Sport)
     - Cycling (Transport)
     - Hiking
     - Mountain Biking
     - Mountain Biking (Electric)  (**new in 0.5.0**)
     - Rowing  (**new in 0.5.0**)
     - Running
     - Skiing (Alpine) (**new in 0.5.0**)
     - Skiing (Cross Country)  (**new in 0.5.0**)
     - Snowshoes  (**new in 0.5.2**)
     - Trail  (**new in 0.5.0**)
     - Walking
- (*new in 0.5.0*) Stopped speed threshold used by `gpxpy <https://github.com/tkrajina/gpxpy>`_ is not the default one for the following sports (0.1 km/h instead of 1 km/h):
     - Hiking
     - Skiing (Cross Country)
     - Snowshoes
     - Trail
     - Walking

.. note::
  It can be overridden in user preferences.

- Dashboard with month calendar displaying workouts and record. The week can start on Sunday or Monday (which can be changed in the user preferences). The calendar displays up to 100 workouts.
- Workout creation by uploading a gpx file (related data are stored in database with metric system). A workout can even be created without gpx (the user must enter date, time, duration and distance).
- A workout with a gpx file can be displayed with map, weather (if the DarkSky API key is provided) and charts (speed and elevation). Segments can be displayed.
- Workout gpx file can be downloaded  (**new in 0.5.1**)
- Workout edition and deletion. User can add a note.
- User statistics, by time period (week, month, year) and sport:
    - total distance
    - total duration
    - total workouts
    - total ascent  (**new in 0.5.0**)
    - total descent  (**new in 0.5.0**)
    - average speed  (**new in 0.5.1**)
- User records by sports:
    - average speed
    - farest distance
    - longest duration
    - maximum speed
- Workouts list and filter. Only sports with workouts are displayed in sport dropdown.

.. note::
    For now, only the owner of the workout can see it.

Translations
^^^^^^^^^^^^
FitTrackee is available in English and French (which can be saved in the user preferences).


Dashboard
~~~~~~~~~

.. figure:: _images/fittrackee_screenshot-01.png
   :alt: FitTrackee Dashboard


Workout detail
~~~~~~~~~~~~~~~~~~~~~~~
.. figure:: _images/fittrackee_screenshot-02.png
   :alt: FitTrackee Workout


Workouts list
~~~~~~~~~~~~~
.. figure:: _images/fittrackee_screenshot-03.png
   :alt: FitTrackee Workouts


Statistics
~~~~~~~~~~
.. figure:: _images/fittrackee_screenshot-04.png
   :alt: FitTrackee Statistics

Administration
~~~~~~~~~~~~~~
.. figure:: _images/fittrackee_screenshot-05.png
   :alt: FitTrackee Administration

.. figure:: _images/fittrackee_screenshot-06.png
   :alt: FitTrackee Sports Administration