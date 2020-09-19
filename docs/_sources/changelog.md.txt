# Change log

## Version 0.4.0 (unreleased)

This version introduces some major changes:
- Installation becomes more easy.  
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
