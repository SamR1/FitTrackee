Statistics
##########

.. versionadded:: 0.2.0


By time period
**************

.. versionchanged:: 0.5.0 added total ascent and descent
.. versionchanged:: 0.5.1 added average speed
.. versionchanged:: 0.5.1 added average distance, duration, workouts, ascent and descent
.. versionchanged:: 0.9.3 added day as time period
.. versionchanged:: 1.1.0 added total calories and average pace

User statistics, by period (day, week, month, year) and by sport, display:

- totals:

  - total distance
  - total duration
  - total workouts
  - total ascent
  - total descent
  - total calories

- averages:

  - average speed
  - average distance
  - average duration
  - average number of workouts
  - average ascent
  - average descent
  - average pace

.. figure:: ../_images/statistics-by-time-period.png
   :alt: Statistics on FitTrackee

By sport
********

.. versionadded:: 0.8.5
.. versionchanged:: 1.1.0 added average pace and total calories

User statistics by sport display:

- total workouts
- distance (total and average)
- duration (total and average)
- average speed
- ascent (total and average)
- descent (total and average)
- average pace (if 'pace' is set in the sport preference)
- total calories
- records

.. figure:: ../_images/statistics-by-sport.png
   :alt: Sport Statistics on FitTrackee

.. note::
  | There is a limit on the number of workouts used to calculate statistics to avoid performance issues. The value can be set in `administration <administration.html#configuration>`__.
  | If the limit is reached, the number of workouts used is displayed.
  | The total number of workouts for a given sport is not affected by this limit.

