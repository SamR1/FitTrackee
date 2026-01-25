Workout
#######

Creation
********

A workout can be created by:

- uploading manually a file or a zip archive containing a limited number of files,
- or entering workout data (without file).

.. note::
  | For now, **FitTrackee** has no importer, but some `third-party tools <../third_party_tools.html#importers>`__ allow you to import workouts (for instance from Garmin or Strava accounts).

File upload
===========

.. versionchanged:: 0.10.0  support for .fit, .kml/.kmz and .tcx files, asynchronous uploads for larger files
.. versionchanged:: 0.10.3  pause events triggering segment creation (.fit files only)

Supported files extensions are:

- .gpx
- .fit
- .kml and .kmz

  - versions supported: 2.2.0 and 2.3.0
  - only files with ``Placemark``/``MultiTrack``/``Tracks`` are supported.
  - files with folders or multiple ``Placemark`` are not supported for now.

- .tcx
- .zip archive containing files with one of the supported extensions

The maximum file size and number can be modified by administrators.

.. warning::

   Only files containing at least time and coordinates are supported (otherwise, errors may occur on upload).


.. figure:: ../_images/workout-creation-with-file.png
   :alt: Form for file upload

   Form for file upload

.. admonition:: Technical notes

  For extensions other than .gpx, files are converted to .gpx:

  - .fit: generated .gpx file contains one track (``<trk>``). Depending on user preferences, a new segment (``<trkseg>``) can be created after pause events:
     - all pause events,
     - only manual pause event.
  - .kml: generated .gpx file contains one track (``<trk>``) corresponding to ``<MultiTrack>``, containing one segment (``<trkseg>``) per kml track (``<Track>``)
  - .tcx: generated .gpx file contains one track (``<trk>``) containing one segment (``<trkseg>``) per activity (``<Activity>``)

Archive files (.zip) upload can be asynchronous when enabled by the administrators.
Asynchronous uploads can be displayed in user account and can be interrupted by the user.
In case errors are encountered, the list of error files is displayed at the end of the upload.


.. note::
  Weather data are not collected during asynchronous uploads to avoid hitting API rate limit.

.. warning::
  | A timeout is set to prevent long-running uploads.
  | Errored or aborted uploads are not reprocessed.

A notification is displayed after task completion.

Data entry
==========

.. versionchanged:: 0.7.10 add ascent and descent

Users can create a workout without file by entering date, time, duration, distance, ascent and descent.

.. figure:: ../_images/workout-creation-without-file.png
   :alt: Form for workout creation without a file


Sports
======

27 sports are available.

| Most icons for sports are made by `Freepik <https://www.freepik.com/>`__ from `Flaticon <https://www.flaticon.com/>`__.
| Sports icons for Canoeing, Kayaking and Rowing are made by `@Von-Birne <https://github.com/Von-Birne>`__.
| Sport icon for Halfbike is made by `@astridx <https://github.com/astridx>`__.

Sports available
----------------

Cycle sports
~~~~~~~~~~~~
.. versionadded:: 0.7.3 Cycling (Virtual)
.. versionadded:: 0.7.27 Cycling (Trekking)
.. versionadded:: 0.9.3 Halfbike
.. versionadded:: 0.5.0 Mountain Biking (Electric)

.. cssclass:: sports-table
.. list-table::
   :header-rows: 1
   :widths: 15 15 70

   * - Id
     - Icon
     - Name
   * - 1
     - .. image:: ../_images/sports/cycling_sport.png
     - Cycling (Sport)
   * - 2
     - .. image:: ../_images/sports/cycling_transport.png
     - Cycling (Transport)
   * - 17
     - .. image:: ../_images/sports/cycling_trekking.png
     - Cycling (Trekking)
   * - 13
     - .. image:: ../_images/sports/cycling_virtual.png
     - Cycling (Virtual)
   * - 21
     - .. image:: ../_images/sports/halfbike.png
     - Halfbike
   * - 4
     - .. image:: ../_images/sports/mountain_biking.png
     - Mountain Biking
   * - 7
     - .. image:: ../_images/sports/mountain_biking_electric.png
     - Mountain Biking (Electric)


Foot sports
~~~~~~~~~~~
.. versionadded:: 0.5.0 Trail

.. cssclass:: sports-table
.. list-table::
   :header-rows: 1
   :widths: 15 15 70

   * - Id
     - Icon
     - Name
   * - 3
     - .. image:: ../_images/sports/hiking.png
     - Hiking
   * - 5
     - .. image:: ../_images/sports/running.png
     - Running
   * - 8
     - .. image:: ../_images/sports/trail.png
     - Trail
   * - 6
     - .. image:: ../_images/sports/walking.png
     - Walking

Water sports
~~~~~~~~~~~~
.. versionadded:: 0.5.0 Rowing
.. versionadded:: 0.7.20 Open Water Swimming
.. versionadded:: 0.9.3 Canoeing and Kayaking
.. versionchanged:: 0.9.3 Modified Rowing image
.. versionadded:: 0.9.10 Windsurfing
.. versionadded:: 0.10.3 Standup paddleboarding
.. versionadded:: 1.1.0 Canoeing (Whitewater) and Kayaking (Whitewater)
.. versionchanged:: 1.1.0 Modified Canoeing and Kayaking images

.. cssclass:: sports-table
.. list-table::
   :header-rows: 1
   :widths: 15 15 70

   * - Id
     - Icon
     - Name
   * - 20
     - .. image:: ../_images/sports/canoeing.png
     - Canoeing
   * - 26
     - .. image:: ../_images/sports/canoeing_whitewater.png
     - Canoeing (Whitewater)
   * - 19
     - .. image:: ../_images/sports/kayaking.png
     - Kayaking
   * - 27
     - .. image:: ../_images/sports/kayaking_whitewater.png
     - Kayaking (Whitewater)
   * - 16
     - .. image:: ../_images/sports/open_water_swimming.png
     - Open Water Swimming
   * - 11
     - .. image:: ../_images/sports/rowing.png
     - Rowing
   * - 23
     - .. image:: ../_images/sports/standup_paddleboarding.png
     - Standup Paddleboarding
   * - 22
     - .. image:: ../_images/sports/windsurfing.png
     - Windsurfing

Rackets sports
~~~~~~~~~~~~~~
.. versionadded:: 0.11.0 Tennis (Outdoor)
.. versionadded:: 1.0.0 Padel (Outdoor)

.. cssclass:: sports-table
.. list-table::
   :header-rows: 1
   :widths: 15 15 70

   * - Id
     - Icon
     - Name
   * - 25
     - .. image:: ../_images/sports/padel_outdoor.png
     - Padel (Outdoor)
   * - 24
     - .. image:: ../_images/sports/tennis_outdoor.png
     - Tennis (Outdoor)

Winter sports and mountain sports
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. versionadded:: 0.5.0 Skiing (Alpine) and Skiing (Cross Country)
.. versionadded:: 0.5.2 Snowshoes
.. versionadded:: 0.7.3 Mountaineering

.. cssclass:: sports-table
.. list-table::
   :header-rows: 1
   :widths: 15 15 70

   * - Id
     - Icon
     - Name
   * - 14
     - .. image:: ../_images/sports/mountaineering.png
     - Mountaineering
   * - 9
     - .. image:: ../_images/sports/skiing_alpine.png
     - Skiing (Alpine)
   * - 10
     - .. image:: ../_images/sports/skiing_cross_country.png
     - Skiing (Cross Country)
   * - 10
     - .. image:: ../_images/sports/snowshoes.png
     - Snowshoes


Other sports
~~~~~~~~~~~~
.. versionadded:: 0.7.19 Paragliding
.. versionadded:: 0.8.7 Swimrun

.. cssclass:: sports-table
.. list-table::
   :header-rows: 1
   :widths: 15 15 70

   * - Id
     - Icon
     - Name
   * - 15
     - .. image:: ../_images/sports/paragliding.png
     - Paragliding
   * - 18
     - .. image:: ../_images/sports/swimrun.png
     - Swimrun

.. note::
  | Swimrun is displayed as a single activity with no difference between segments for now.

Sports configuration
--------------------
.. versionchanged:: 0.8.0 added default equipment
.. versionchanged:: 1.1.0 added pace/speed display

It is possible to configure sport in user preferences (see `Account & preferences <account_and_preferences.html#sports-preferences>`__) :

- Sport color
- Active status
- Stopped speed threshold
- Default equipment
- Pace/Speed display

Data entered and extracted
==========================

.. versionchanged:: 0.7.11 added Visual Crossing as weather provider
.. versionremoved:: 0.7.23 removed DarkSky as weather provider
.. versionchanged:: 0.8.0 added equipment
.. versionchanged:: 0.8.9 added workout description
.. versionchanged:: 0.8.9 added extraction of description from file
.. versionchanged:: 0.8.10 title can be entered when creation workout with file
.. versionchanged:: 0.9.0 added Markdown syntax for descriptions and private notes
.. versionchanged:: 0.11.0 Garmin mapping updated
.. versionchanged:: 1.1.0 added extraction of total calories from file, missing elevations

If present in .gpx, .tcx and .fit files, the source (application or device) is displayed.

.. note::
     .fit files from Garmin devices may contain product id instead of product name. The mapping between the product id and the product name allows the product name to be displayed instead, if available.

| If the name is present in the file, it is used as the workout title. Otherwise, a title is generated from the sport and workout date.
| Users can provide title while uploading file.

| Users can add description and private notes.
| A limited Markdown syntax can be used.

If present and no description is provided by the user, the description from the file is used as the workout description.

An `equipment <equipment.html>`__ can be associated with a workout. For now, only one equipment can be associated.

If present in .gpx, .tcx or .fit files, the total calories are extracted.

If a weather provider is set by the administrator (data source is displayed in **About** page), the weather is extracted for the start and end points.


Visibility levels
=================

.. versionadded:: 0.9.0
.. versionchanged:: 0.10.0 added visibility levels for heart rate
.. versionchanged:: 1.1.0 added visibility levels for total calories

Visibility level can be set separately for workout data, analysis and map:

- private: only owner can see data,
- followers only: only owner and followers can see data,
- public: anyone can see data even unauthenticated users.

| Workout visibility applies to title, description, records and workout data except elevation.
| Analysis visibility applies to chart data, elevation and segments, if workout is associated with a file.
| Map visibility applies to the map, if workout is associated with a file.

.. note::
  | Default visibility is private. All workouts created before **FitTrackee** 0.9.0 are private.

In addition, the visibility level can be set for all workouts for heart rate (average and max values and values displayed in chart) and total calories (value displayed in the workout detail).

Default visibility can be set in the `user preferences <account_and_preferences.html#preferences>`__.

.. note::
  | A workout with a file whose visibility for map and analysis data does not allow them to be viewed appears as a workout without a file.
  | Max. speed and ascent/descent are returned regardless analysis visibility.

Users can report a workout that violates instance rules. This will send a notification to moderators and administrators.

.. important::
  | Please keep in mind that the server operating team or the moderation team may view content with restricted visibility.

Calculated data
===============

.. admonition:: Technical notes

  Related data are stored in database in metric system.

Calculated values may differ from values calculated by the application or device that originally generated the files, in particular the maximum speed or the duration of pauses.

By default, extreme speed values (which may be related to GPS errors) are excluded, which also affects the maximum speed (and pace).

.. note::
  A user preference allows this behavior to be disabled (see `Account & preferences <account_and_preferences.html#preferences>`__).


Stopped speed threshold
-----------------------
.. versionchanged:: 0.5.0 added configuration

Stopped speed threshold affects speeds and durations calculation.

The value used by `gpxpy <https://github.com/tkrajina/gpxpy>`_ is not the default one for the following sports (0.1 km/h instead of 1 km/h):

- Hiking
- Mountaineering
- Open Water Swimming
- Padel (Outdoor)
- Paragliding
- Skiing (Cross Country)
- Snowshoes
- Swimrun
- Tennis (Outdoor)
- Trail
- Walking

.. note::
  | Stopped speed threshold can be overridden in user preferences (see `Account & preferences <account_and_preferences.html#sports-preferences>`__).
  | It is not possible to enter 0 as stopped speed threshold, as gpxpy ignores it when it is equal to 0.

Elevation
---------
.. versionchanged:: 1.0.6 elevation is not displayed for flatwater sports
.. versionchanged:: 1.1.0 add missing elevation and elevation data source change

Elevation-related data for racket sports (Outdoor Tennis and Padel) and flatwater sports (Canoeing, Kayaking, Rowing, Open Water Swimming, Rowing and Standup Paddleboarding) are not stored in database and displayed if the file contains elevation

| If some elevation data are missing and an `elevation service <../installation/elevation.html>`__ is enabled by the administrators (data source are displayed in **About** page), the missing elevations can be retrieved on workout creation if the user preference is set.
| In this case, all elevations are updated.

Elevation data source can also be changed after creation.

Records
-------

.. versionchanged:: 0.6.11 added highest ascent record
.. versionchanged:: 1.1.0 added pace records

Depending on sports, following records are calculated:

- average speed
- average pace
- best pace
- farthest distance
- highest ascent
- longest duration
- maximum speed

.. note::
  Records may differ from records displayed by the application that originally generated the files.

Display
*******

Once created, the workout is displayed with the calculated data and, in the case of workouts created from a file, with a map and chart.

Example for a workout created with a .gpx file:

.. figure:: ../_images/workout-detail.png
   :alt: Workout Detail on FitTrackee

If the file contains multiple segments, each of them can be displayed.

Depending on preferences, data is displayed using the metric or imperial system.

Displayed data
==============
.. versionchanged:: 0.5.5 added wind direction
.. versionchanged:: 0.5.5 added equipment
.. versionchanged:: 0.10.0 added file source, heart rate, and cadence
.. versionchanged:: 0.11.0 added power
.. versionchanged:: 1.1.0 added pace and total calories

Depending on the sport and the method used to create the workout, the following data are displayed:

- if present, file source
- durations (moving and total durations and pauses)
- distance
- average and max. speeds (depending on sport or pace/display preference)
- average and best paces for the following sports (depending on pace/display preference):

  - Hiking
  - Running
  - Trail
  - Walking

- if present, min. and max. altitudes
- if present, ascent and descent
- if present, average and max. heart rate
- if present, average and max. cadence for the following sports:

  - Cycling (Sport)
  - Cycling (Trekking)
  - Cycling (Transport)
  - Cycling (Virtual)
  - Halfbike
  - Mountain Biking
  - Mountain Biking (Electric)
  - Hiking
  - Mountaineering
  - Snowshoes
  - Running
  - Trail
  - Walking
  - Open Water Swimming

- if present, average and max. power for the following sports:

  - Cycling (Sport)
  - Cycling (Trekking)
  - Cycling (Transport)
  - Cycling (Virtual)
  - Halfbike
  - Mountain Biking
  - Mountain Biking (Electric)

- if present, total calories
- | if present, weather data
  | Wind is displayed, with an arrow indicating the direction (a tooltip can be displayed with the direction that the wind is coming **from**).
- records

  .. note::
    Records may differ from records displayed by the application that originally generated the files.

- associated equipment, according to its visibility (equipment details are only visible to its owner)

.. note::
   | Source and average and max values for heart rate and cadence are not displayed for workouts created before v0.10.0.
   | Average and max values for power are not displayed for workouts created before v0.11.0.
   | Pace and total calories are not displayed for workouts created before v1.1.0.
   | Refreshing the workout allows these values to be calculated.


Map
===

.. versionchanged:: 0.5.0 added full screen and reset control
.. versionchanged:: 0.11.0 added heatmap for racket sports

| A map is displayed for workout with a file with the tile server set by the administrators (OpenStreetMap by default).
| Controls allow full screen view and position reset.
| If the sport is Outdoor Tennis or Padel, a heat map is also available.

Chart
=====

.. versionchanged:: 0.10.0 added heart rate and cadence
.. versionchanged:: 0.11.0 added power and display preference for charts
.. versionchanged:: 1.1.0 added pace and total calories, change default value for charts display preference

A chart is displayed for workout with a file, depending on sport and available data:

- speed (by default, speed is not displayed when pace is displayed)
- pace
- elevation
- heart rate
- cadence
- power

Speed/pace, elevation, heart rate, cadence and power can be displayed on one chart or split on multiple charts.

.. image:: ../_images/pace_elevation_on_same_chart.png
   :alt: Pace and elevation are displayed in the same chart.

The preferred display can be stored in a `user preference <account_and_preferences.html#preferences>`__.

Workout menu
============

.. versionchanged:: 0.5.1 added button for download
.. versionchanged:: 0.9.0 added like button
.. versionchanged:: 0.12.0 added refresh button
.. versionchanged:: 1.1.0 added button for elevation data source, file download updated

.. cssclass:: workout-buttons-table
.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Button
     - Action
   * - .. image:: ../_images/workout_buttons/workout_like.png
     - Like workout (only for authenticated users, depending on workout visibility)
   * - .. image:: ../_images/workout_buttons/workout_download.png
     - Download the original workout file or the generated .gpx file (only for workout owner)
   * - .. image:: ../_images/workout_buttons/workout_edition.png
     - Edit workout (only for workout owner)
   * - .. image:: ../_images/workout_buttons/workout_refresh.png
     - Refresh workout (only for workout owner)
   * - .. image:: ../_images/workout_buttons/workout_elevation_data_source.png
     - Change elevation data source workout (only for workout owner)
   * - .. image:: ../_images/workout_buttons/workout_delete.png
     - Delete workout (only for workout owner)
   * - .. image:: ../_images/workout_buttons/workout_report.png
     - Report workout (only for authenticated users except the workout owner, depending on workout visibility)


Edition and deletion
********************

.. versionchanged:: 0.12.0 added workout refresh
.. versionchanged:: 1.1.0 change elevation data source

Workout can be edited:

- sport
- title
- equipment
- description
- private notes
- workout visibility
- analysis visibility
- map visibility
- date (only workouts without gpx)
- duration (only workouts without gpx)
- distance (only workouts without gpx)
- ascent and descent (only workouts without gpx)

| Some values are only calculated on workout creation.
| The previously uploaded workouts are not updated in the following cases:

- updating some preferences ("max. speed calculation strategy" and "pause events triggering segment creation"),
- updating stopped speed threshold in sport preferences (used to calculate pauses),
- configuring a weather data provider,
- some new features,
- Garmin device mappings update,
- bug fixes on file processing.

The calculated data can be refreshed by clicking on **Refresh** button and weather data fetched (if provider is set and the workout does not have weather data).

.. note::
  | A `CLI command <../cli.html#ftcli-workouts-refresh>`__ is available to refresh several workouts depending on options.

  .. warning::
     If a weather data provider is defined and the ``--with-weather`` option is provided and/or an Elevation API URL is set and ``--with-elevation`` option is provided, the rate limit may be reached, resulting in API rate limit errors when a large number of workouts is refreshed.

| The elevation data source can be changed if an `elevation service <../installation/elevation.html>`__ is enabled by the administrators.
| In this case, the available services are displayed after clicking on the button **Change elevation data source**:

.. image:: ../_images/elevations-choices.png
   :alt: List of available elevation sources


It is also possible to get the elevation again from the file:

.. image:: ../_images/elevations-choices-with-file.png
   :alt: List of available elevation sources with file

A workout can be deleted by clicking on the **Delete** button.