Features
########

List
~~~~

Administration
^^^^^^^^^^^^^^
(*new in 0.3.0*)

- **Application**

  The following parameters can be set:

  - active users limit (if 0, registration is enabled (no limit defined))
  - maximum size of uploaded files
  - maximum size of zip archive
  - maximum number of files in the zip archive

- **Users**

  - display users list and details
  - edit a user to add/remove administration rights
  - delete a user

- **Sports**

  - enable or disable a sport (a sport can be disabled even if workout with this sport exists)

Account
^^^^^^^
- A user can create, update and deleted his account
- A user can reset his password (*new in 0.3.0*)


Workouts
^^^^^^^^
- 6 sports are supported:
     - Cycling (Sport)
     - Cycling (Transport)
     - Hiking
     - Montain Biking
     - Running
     - Walking
- Dashboard with month calendar displaying workouts and record. The week can start on Sunday or Monday (which can be changed in the user settings). The calendar displays up to 100 workouts.
- Workout creation by uploading a gpx file. A workout can even be created without gpx (the user must enter date, time, duration and distance)
- A workout with a gpx file can be displayed with map, weather (if the DarkSky API key is provided) and charts (speed and elevation). Segments can be displayed
- Workout edition and deletion. User can add a note
- User statistics
- User records by sports:
    - average speed
    - farest distance
    - longest duration
    - maximum speed
- Workouts list and filter

.. note::
    for now, only the owner of the workout can see it.

Translations
^^^^^^^^^^^^
FitTrackee is available in English and French (which can be saved in the user settings).


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
