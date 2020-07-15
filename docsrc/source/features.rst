Features
########

List
~~~~

Account
^^^^^^^
- A user can create, update and deleted his account
- Password reset is now available

Administration
^^^^^^^^^^^^^^
- Application

  - active users limit (if 0, registration is enabled (no limit defined))
  - maximum size of uploaded files
  - maximum size of zip archive
  - maximum number of files in the zip archive

- Users

  - display users list and details
  - edit a user to add/remove administration rights
  - delete a user

- Sports

  - enable or disable a sport (a sport can be disabled even if activity with this sport exists)

Activities/Workouts
^^^^^^^^^^^^^^^^^^^
- 6 sports supported:
     - Cycling (Sport)
     - Cycling (Transport)
     - Hiking
     - Montain Biking
     - Running
     - Walking
- Dashboard with month calendar displaying activities and record. The week can start on Sunday or Monday (which can be changed in the user settings)
- Activity creation by uploading a gpx file. An activity can even be created without gpx (the user must enter date, time, duration and distance)
- An activity with a gpx file can be displayed with map, weather (if the DarkSky API key is provided) and charts (speed and elevation). Segments can be displayed
- Activity edition and deletion. User can add a note
- User statistics
- User records by sports:
    - average speed
    - farest distance
    - longest duration
    - maximum speed
- Activities list and filter

**Notes:**

- for now, only activity owner can see his activities

Translations
^^^^^^^^^^^^
FitTrackee is available in English and French (which can be saved in the user settings).


Dashboard
~~~~~~~~~

.. figure:: _images/fittrackee_screenshot-01.png
   :alt: FitTrackee Dashboard


Activity/workout detail
~~~~~~~~~~~~~~~~~~~~~~~
.. figure:: _images/fittrackee_screenshot-02.png
   :alt: FitTrackee Activity


Activities/workouts list
~~~~~~~~~~~~~~~~~~~~~~~~
.. figure:: _images/fittrackee_screenshot-03.png
   :alt: FitTrackee Activities


Statistics
~~~~~~~~~~
.. figure:: _images/fittrackee_screenshot-04.png
   :alt: FitTrackee Statistics

Administration
~~~~~~~~~~~~~~
.. figure:: _images/fittrackee_screenshot-05.png
   :alt: FitTrackee Administration
