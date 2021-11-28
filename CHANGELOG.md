# Change log

## Version 0.5.1 (unreleased)

### Issues Closed

#### New Features

* [#5](https://github.com/SamR1/FitTrackee/issues/5) - Display a chart with average speed

In this release 1 issue was closed.  


## Version 0.5.0 (2021/11/14)

### Issues Closed

#### New Features

* [#99](https://github.com/SamR1/FitTrackee/issues/99) - Display workout with imperial units 
* [#91](https://github.com/SamR1/FitTrackee/issues/91) - Display elevation chart with min and max altitude of workout
* [#90](https://github.com/SamR1/FitTrackee/issues/90) - Add user sports preferences
* [#18](https://github.com/SamR1/FitTrackee/issues/18) - Better UI

#### Bugs Fixed

* [#95](https://github.com/SamR1/FitTrackee/issues/95) - Some workouts seem to be missing on statistics chart

#### Misc

* [#104](https://github.com/SamR1/FitTrackee/issues/104) - Switch to AGPLv3 license

### Pull Requests

* [#101](https://github.com/SamR1/FitTrackee/pull/101) - Docker updates for full files 
* [#100](https://github.com/SamR1/FitTrackee/pull/100) - Add client application in docker for development
* [#98/#109](https://github.com/SamR1/FitTrackee/pull/109) - Added stopped_speed_threshold to support slow movement
* [#84/#93](https://github.com/SamR1/FitTrackee/pull/93) - Add elevation data and new sports

In this release 6 issues were closed.  
**Note:** This release contains database migrations.

Thanks to the contributors:
- @Fmstrat
- @paf38


## Version 0.4.9 (2021/07/16)

### Issues Closed

#### New Features

* [#83](https://github.com/SamR1/Fittrackee/issues/83) - allow using configured tile server to generate static maps  
  **Note**: to keep using the default tile server, set environment variable `DEFAULT_STATICMAP` to `True`
* [#81](https://github.com/SamR1/Fittrackee/issues/81) - display remaining characters in textarea

#### Bugs Fixed

* [#82](https://github.com/SamR1/Fittrackee/issues/82) - a user can not modify his birth day
* [#80](https://github.com/SamR1/Fittrackee/issues/80) - can not save notes with control characters

In this release 4 issues were closed.


## Version 0.4.8 (2021/07/03)

### Issues Closed

#### Bugs Fixed

* [#79](https://github.com/SamR1/Fittrackee/issues/79) - Fails to start after make rebuild

In this release 1 issue was closed.


## Version 0.4.7 (2021/04/07)

### Issues Closed

#### Bugs Fixed

* [#75](https://github.com/SamR1/Fittrackee/issues/75) - Workouts on the same day are not displayed in right order

### Misc

* Update Python and Javascript dependencies  
**IMPORTANT**: Due to [SQLAlchemy update (1.4+)](https://docs.sqlalchemy.org/en/14/changelog/changelog_14.html#change-3687655465c25a39b968b4f5f6e9170b), engine URLs starting with `postgres://` are no longer supported. Please update `DATABASE_URL` with `postgresql://`.

In this release 1 issue was closed.


## Version 0.4.6 (2021/02/21)

### Issues Closed

#### Bugs Fixed

* [#72](https://github.com/SamR1/Fittrackee/issues/72) - Error message when file exceeding size is incorrect
* [#71](https://github.com/SamR1/Fittrackee/issues/71) - max size or max number of files must be greater than 0
* [#70](https://github.com/SamR1/Fittrackee/issues/70) - max size for an archive must not be less than uploaded files max size

In this release 3 issues were closed.


## Version 0.4.5 (2021/02/17)

### Issues Closed

#### Bugs Fixed

* [#66](https://github.com/SamR1/Fittrackee/issues/66) - invalid gpx limit used when importing zip archive
* [#64](https://github.com/SamR1/Fittrackee/issues/64) - Only 50 workouts per month shown in calendar

In this release 2 issues were closed.


## Version 0.4.4 (2021/01/31)

### Issues Closed

#### Bugs Fixed

* [#62](https://github.com/SamR1/Fittrackee/issues/62) - Error when sending reset password email

### Misc

* Refactoring before introducing new features.
* Add docker files for evaluation purposes.

In this release 1 issue was closed.


## Version 0.4.3 (2021/01/10)

### Issues Closed

#### New Features

* [#58](https://github.com/SamR1/Fittrackee/issues/58) - Standardize terms used for workouts  
**Note:** Database model, upload directory for workouts and API endpoints are also updated.

#### Bugs Fixed

* [#59](https://github.com/SamR1/Fittrackee/issues/59) - No message displayed on uploading image error

In this release 2 issues were closed.


## Version 0.4.2 (2021/01/03)

### Misc

No new features in this release, only some refactorings before introducing 
new features.


## Version 0.4.1 (2020/12/31)

### Issues Closed

#### New Features

* [#57](https://github.com/SamR1/Fittrackee/issues/57) - Use uuid for activities

In this release 1 issue was closed.


## Version 0.4.0 - FitTrackee on PyPI (2020/09/19)

This version introduces some major changes:
- Installation becomes more easy. **FitTrackee** can be now be installed from PyPi.  
⚠️ Warning: please read [installation documentation](https://samr1.github.io/FitTrackee/installation.html), some environment variables and files have been renamed.
- It's now possible to change the tile provider for maps. The default tile server is now **OpenStreetMap**'s standard tile layer (replacing **ThunderForest Outdoors**), 
see [Map tile server in documentation](https://samr1.github.io/FitTrackee/installation.html#map-tile-server).

### Issues Closed

#### New Features

* [#54](https://github.com/SamR1/Fittrackee/issues/54) - Tile server can be changed
* [#53](https://github.com/SamR1/Fittrackee/issues/53) - Simplify FitTrackee installation

In this release 2 issue were closed.


## Version 0.3.0 - Administration (2020/07/15)

This version introduces some major changes:
- FitTrackee administration is now available (see [documentation](https://samr1.github.io/FitTrackee/features.html#administration))  
⚠️ Warning: some application parameters move from environment variables to database (see [installation](https://samr1.github.io/FitTrackee/installation.html#environment-variables)).
- in order to send emails, Redis is now a mandatory dependency

### Issues Closed

#### New Features

* [#50](https://github.com/SamR1/Fittrackee/issues/50) - A user can reset his password
* [#17](https://github.com/SamR1/Fittrackee/issues/17) - A user can delete his account
* [#15](https://github.com/SamR1/Fittrackee/issues/15) - Complete the administration

In this release 3 issues were closed.


## Version 0.2.5 - Fix and improvements (2020/01/31)

### Misc

This version contains minor fix and improvements on client side:
* [4c3fc34](https://github.com/SamR1/FitTrackee/commit/4c3fc343d51b9c27d3ebab71df648bcf7d7bae59) - empty user data on logout
* [34614d5](https://github.com/SamR1/FitTrackee/commit/34614d5a6c29f4911d92db33d36fe95721b39f33) - add spinner on loading activities
* [b862a77](https://github.com/SamR1/FitTrackee/commit/b862a77344abbb07d98fe3ce8b157b5cef0e8d1c), 
[2e1ee2c](https://github.com/SamR1/FitTrackee/commit/2e1ee2c7a1456eb2fe0c0255959c695cc7908975) -
add URL interceptors to simplify routes definition


## Version 0.2.4 - Minor fix (2020/01/30)

### Issues Closed

#### Bugs Fixed

* [#47](https://github.com/SamR1/Fittrackee/issues/47) - timezone drop-down is not displayed correctly
* [#46](https://github.com/SamR1/Fittrackee/issues/46) - calendar cannot display more than 5 or 6 activities on the same day

In this release 2 issues were closed.


## Version 0.2.3 - FitTrackee available in French (2019/12/29)

### Issues Closed

#### New Features

* [#43](https://github.com/SamR1/Fittrackee/issues/43) - Display weekend days with a different background color on calendar
* [#40](https://github.com/SamR1/Fittrackee/issues/40) - Localize FitTrackee (i18n)

#### Bugs Fixed

* [#44](https://github.com/SamR1/Fittrackee/issues/44) - Cannot edit an activity that does not have a gpx file

In this release 3 issues were closed.


## Version 0.2.2 - Statistics fix (2019/09/23)

### Issues Closed

#### Bugs Fixed

* [#41](https://github.com/SamR1/Fittrackee/issues/41) - User statistics are incorrect

In this release 1 issue was closed.

## Version 0.2.1 - Fix and improvements (2019/09/01)

### Issues Closed

#### New Features

* [#4](https://github.com/SamR1/Fittrackee/issues/4) - Show points on the map when mouse over the chart
* [#14](https://github.com/SamR1/Fittrackee/issues/14) - Display segments informations
* [#21](https://github.com/SamR1/Fittrackee/issues/21) - Document the API
* [#23](https://github.com/SamR1/Fittrackee/issues/23) - The user can choose the first day of the week
* [#36](https://github.com/SamR1/Fittrackee/issues/36) - Disable user registration
* [#33](https://github.com/SamR1/Fittrackee/issues/33) - Add file size limit on file upload
* [#37](https://github.com/SamR1/Fittrackee/issues/37) - Display map on activities list

#### Bugs Fixed

* [#34](https://github.com/SamR1/Fittrackee/issues/34) - Weather is not displayed anymore 

### Misc

* **[Poetry](https://poetry.eustace.io/)** replaces **[pipenv](https://docs.pipenv.org)** for Python packages management

In this release 8 issues were closed.


## Version 0.2.0 - Statistics (2019/07/07)

### Issues Closed

#### New Features

* [#13](https://github.com/SamR1/Fittrackee/issues/13) - Detailed statistics

### Misc

* Update dependencies

In this release 1 issue was closed.


## Version 0.1.1 - Fix and improvements (2019/02/07)

### Issues Closed

#### New Features

* [#25](https://github.com/SamR1/FitTrackee/issues/25) - Display records on calendar
* [#22](https://github.com/SamR1/FitTrackee/issues/22) - Add a total on current month statistics

#### Bugs Fixed

* [#31](https://github.com/SamR1/FitTrackee/issues/31) - Use moving duration for stats
* [#29](https://github.com/SamR1/FitTrackee/issues/29) - Pause duration calculation with segments
* [#28](https://github.com/SamR1/FitTrackee/issues/28) - Error on uploading gpx file
* [#26](https://github.com/SamR1/FitTrackee/issues/26) - Total is incorrect in tooltip when duration is displayed
* [#24](https://github.com/SamR1/FitTrackee/issues/24) - Some distances are not displayed correctly on current month statistics

In this release 7 issues were closed.


## Version 0.1.0 - First release 🎉 (2018-07-04)

**Features:**
- Account creation (only standard user, not admin)
- 6 sports supported:
   - Cycling (Sport)
   - Cycling (Transport)
   - Hiking
   - Montain Biking
   - Running
   - Walking 
- Activity creation by uploading a gpx file. An activity can even be created without gpx (the user must enter date, time, duration and distance)
- Activity edition and deletion
- An activity can be displayed with map (if with gpx), weather (if the DarkSky API key is provided) and charts (speed and elevation)
- A user can add a note
- Month calendar with activities
- Current month statistics
- Records by sports:
   - average speed
   - farest distance
   - longest duration
   - maximum speed
- Activities list and search


**Notes:**
- only activity owner can see his activity
- no administration for now

➡️ more informations: see [documentation](https://samr1.github.io/FitTrackee/)  and [current issues](https://github.com/SamR1/FitTrackee/issues)


### Issues Closed

#### New Features

* [#11](https://github.com/SamR1/FitTrackee/issues/11) - Timezone support
* [#10](https://github.com/SamR1/FitTrackee/issues/10) - Add a note to an activity
* [#9](https://github.com/SamR1/FitTrackee/issues/9) - User statistics on dashboard
* [#8](https://github.com/SamR1/FitTrackee/issues/8) - Add weather to activities
* [#3](https://github.com/SamR1/FitTrackee/issues/3) - Search filter for activities
* [#2](https://github.com/SamR1/FitTrackee/issues/2) - Calendar to view activities

In this release 6 issues were closed.
