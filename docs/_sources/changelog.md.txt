# Change log

## Version 0.7.14 (2023/03/08)

### Bugs Fixed

* [#314](https://github.com/SamR1/FitTrackee/issues/314) - GPX file is not deleted when the process fails 
### Translations

* [PR#315](https://github.com/SamR1/FitTrackee/pull/315) - Translations update from Hosted Weblate (Dutch, thanks to @bjornclauw)


## Version 0.7.13 (2023/03/05)

This version allows to display the instance privacy policy. A user must agree to the privacy policy to register.  
A default policy is available and a custom policy can be defined in the administration.  
**Note:** After **FitTrackee** upgrade, a message will be displayed to all users in order to review the policy.  

A user can now request a data export (containing user info, workout data and uploaded gpx files).

Lastly, additional information that may be useful to users can be displayed in **About** page.


### Features and enhancements

* [#301](https://github.com/SamR1/FitTrackee/issues/301) - add privacy policy
* [#304](https://github.com/SamR1/FitTrackee/issues/304) - add user data export
* [#305](https://github.com/SamR1/FitTrackee/issues/305) - add additional information in About page

### Bugs Fixed

* [PR#307](https://github.com/SamR1/FitTrackee/pull/307) - Minor fixes
  * update workout and map files name
  * fix error message when api is not running
  * fix modal position

### Translations

* [PR#297](https://github.com/SamR1/FitTrackee/pull/297) - Translations update from Hosted Weblate (Dutch)
* [PR#308](https://github.com/SamR1/FitTrackee/pull/308) - Translations update from Hosted Weblate (Dutch)
* [PR#310](https://github.com/SamR1/FitTrackee/pull/310) - Translations update from Hosted Weblate (Dutch and German)

Thanks to the contributors:
- @bjornclauw
- @qwerty287

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://samr1.github.io/FitTrackee/installation.html#upgrade))


## Version 0.7.12 (2023/02/16)

### Translations

* [PR#290](https://github.com/SamR1/FitTrackee/pull/290) - Translations update from Hosted Weblate (German, thanks to @qwerty287)

### Misc

* [#294](https://github.com/SamR1/FitTrackee/issues/294) - drop PostgreSQL10 support
* dependencies update


## Version 0.7.11 (2022/12/31)

### Features and enhancements

* [PR#265](https://github.com/SamR1/FitTrackee/pull/265) - Implementing alternative weather API (VisualCrossing.com)  
  **Note**: A new environment variable must be to set to configure the weather data provider: `WEATHER_API_PROVIDER` (see [documentation](https://samr1.github.io/FitTrackee/installation.html#weather-data))

### Translations

* [PR#287](https://github.com/SamR1/FitTrackee/pull/287) - Translations update from Hosted Weblate (Dutch)
* [PR#289](https://github.com/SamR1/FitTrackee/pull/289) - Translations update from Hosted Weblate (German)


Thanks to the contributors:
- @bjornclauw
- @jat255 
- @qwerty287


## Version 0.7.10 (2022/12/21)

FitTrackee is now available in Italian (thanks to @dperruso).

### Features and enhancements

* [#92](https://github.com/SamR1/FitTrackee/issues/92) - Add ascent and descent parameters in workout import without GPX file

### Translations

* [#279](https://github.com/SamR1/FitTrackee/issues/279) - [Translation Request] - Italian (thanks to @dperruso)
* [c88a515](https://github.com/SamR1/FitTrackee/commit/c88a5158fea5f9e2fa8c41ecc2c100f6d9319371) - Translations update from Hosted Weblate (Dutch, thanks to @bjornclauw)
* [f96dcef](https://github.com/SamR1/FitTrackee/commit/f96dcef0dc69d00f65a036fa2e33c22612004cb1) - Translations update (German)

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://samr1.github.io/FitTrackee/installation.html#upgrade))


## Version 0.7.9 (2022/12/11)

### Features and enhancements

* [#280](https://github.com/SamR1/FitTrackee/issues/280) - New sport: Mountaineering

### Translations

* [PR#278](https://github.com/SamR1/FitTrackee/pull/278) - Translations update from Hosted Weblate (German, thanks to @qwerty287)
* [PR#282](https://github.com/SamR1/FitTrackee/pull/282) - Init italian translation files

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://samr1.github.io/FitTrackee/installation.html#upgrade))


## Version 0.7.8 (2022/11/30)

FitTrackee is now available in Dutch (thanks to @bjornclauw).


### Translations

* [#270](https://github.com/SamR1/FitTrackee/issues/270) - [translations request] Dutch (Nederlands)


## Version 0.7.7 (2022/11/27)

### Features and enhancements

* [#258](https://github.com/SamR1/FitTrackee/issues/258) - Request: parse links in notes area (thanks to @jat255)

### Bugs Fixed

* [PR#271](https://github.com/SamR1/FitTrackee/pull/271) - Fix workouts creation

### Translations

* [PR#273](https://github.com/SamR1/FitTrackee/pull/273) - Init Dutch translations files

### Misc

* [PR#274](https://github.com/SamR1/FitTrackee/pull/274) - Tests parallelization
* [PR#275](https://github.com/SamR1/FitTrackee/pull/275) - Disable worker entry point

**Note:** `fittrackee_worker` command is disabled, please use existing flask-dramatiq CLI (see [documentation](https://samr1.github.io/FitTrackee/installation.html#from-pypi))

## Version 0.7.6 (2022/11/09)

### Translations

* [3c8d9c2](https://github.com/SamR1/FitTrackee/commit/3c8d9c262358958346125dd286f09ed9881fda4b) - fix api locale file (remove trailing comma) 

### Misc

* dev dependencies update


## Version 0.7.5 (2022/11/09)

### Bugs Fixed

* [#264](https://github.com/SamR1/FitTrackee/issues/264) - UI has white and gray background

### Translations

* [#266](https://github.com/SamR1/FitTrackee/issues/266) - Translations update from Hosted Weblate (German, thanks to @qwerty287)


## Version 0.7.4 (2022/11/05)

### Bugs Fixed

* [#260](https://github.com/SamR1/FitTrackee/issues/260) - Files size is not checked in zip archive
* [#261](https://github.com/SamR1/FitTrackee/issues/261) - The API should return an error when the number of files in an archive exceeds the limit

Note: archive import still needs some improvements (see [#89](https://github.com/SamR1/FitTrackee/issues/89))

### Translations

* [b1536fc](https://github.com/SamR1/FitTrackee/pull/262/commits/b1536fc637649c4c32a88af6d96c131f05bc1742) - fix french translations in administration 

### Documentation

* [#257](https://github.com/SamR1/FitTrackee/issues/257) - Add client_max_body_size note to example nginx config 

Thanks to @jat255 


## Version 0.7.3 (2022/11/01)

### Features and enhancements

* [#112](https://github.com/SamR1/FitTrackee/issues/112) - allow user to change date format
* [#244](https://github.com/SamR1/FitTrackee/issues/244) - New sport type: "Virtual Ride"

Thanks to @jat255 

### Bugs Fixed

* [#246](https://github.com/SamR1/FitTrackee/issues/246) - Add support to PostgreSQL 15
* [#247](https://github.com/SamR1/FitTrackee/issues/247) - Segments duration is displayed with microseconds

### Translations

* [PR#252](https://github.com/SamR1/FitTrackee/issues/252) - init Norwegian Bokmål translations files

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://samr1.github.io/FitTrackee/installation.html#upgrade))


## Version 0.7.2 (2022/09/21)

### Translations

* [PR#242](https://github.com/SamR1/FitTrackee/issues/242) - Translations update from Weblate (German, thanks to @qwerty287)


## Version 0.7.1 (2022/09/21)

### Bugs Fixed

* [PR#241](https://github.com/SamR1/FitTrackee/issues/241) - Add missing password strength estimation package (german)

### Translations

* [PR#239](https://github.com/SamR1/FitTrackee/issues/239) - Translations update from Weblate (German, thanks to @qwerty287)
* [cb9d02f](https://github.com/SamR1/FitTrackee/commit/cb9d02ff1d047e9abd80a87121796f94376b54d3) - Update OAuth 2.0 translations (English & French)


## Version 0.7.0 (2022/09/19)

### Features and enhancements

* [#88](https://github.com/SamR1/FitTrackee/issues/88) - OAuth 2.0 access token for api access
* [#231](https://github.com/SamR1/FitTrackee/issues/231) - Invalidate token on logout
* [PR#236](https://github.com/SamR1/FitTrackee/issues/236) - Add API rate limits

### Bugs Fixed

* [#232](https://github.com/SamR1/FitTrackee/issues/232) - Speed chart can not be hidden
* [#237](https://github.com/SamR1/FitTrackee/issues/237) - Can not edit a workout when notes value is null

### Translations

* [PR#212](https://github.com/SamR1/FitTrackee/issues/212) - Translations update from Hosted Weblate (thanks to J. Lavoie)

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://samr1.github.io/FitTrackee/installation.html#upgrade))


## Version 0.6.12 (2022/09/14)

### Issues Closed

#### Bugs Fixed

* [#230](https://github.com/SamR1/FitTrackee/issues/230) - Database problem after upgrade to 0.6.11

### Pull Requests

#### Misc

* [#225](https://github.com/SamR1/FitTrackee/pull/225) - Fix grammar issue

Thanks to @Skylan0916

In this release 1 issue was closed.  
**Note:** This release contains a fix on the last database migration that will be executed only on versions lower than v0.6.11 (no data differences with v0.6.11, the fix allows to execute the migration on Postgres<12)  
(see upgrade instructions in [documentation](https://samr1.github.io/FitTrackee/installation.html#upgrade)).


## Version 0.6.11 (2022/07/27)

### Issues Closed

#### Bugs Fixed

* [#213](https://github.com/SamR1/FitTrackee/issues/213) - Statistics - When using imperial measurements, ascent/descent should be in ft not mi

### Pull Requests

#### Features

* [#223](https://github.com/SamR1/FitTrackee/pull/223) - Display ascent record icon
* [#167](https://github.com/SamR1/FitTrackee/pull/167) - Added ascent record to Dashboard 
* [#162](https://github.com/SamR1/FitTrackee/pull/162) - Added total elevation to dashboard 

Thanks to @Fmstrat

In this release 1 issue was closed.  
**Note:** This release contains database migration (see upgrade instructions in [documentation](https://samr1.github.io/FitTrackee/installation.html#upgrade))


### Version 0.6.10 (2022/07/13)

### Issues Closed

#### Bugs Fixed

* [#210](https://github.com/SamR1/FitTrackee/issues/210) - ERROR - could not download 6 tiles  
  **Note**: for tile server requiring subdomains, see the new environment variable [`STATICMAP_SUBDOMAINS`](https://samr1.github.io/FitTrackee/installation.html#envvar-STATICMAP_SUBDOMAINS)

### Pull Requests

#### Bugs Fixed

* [#209](https://github.com/SamR1/FitTrackee/pull/209) - Incorrect duration with track containing multiple segments

Thanks to @gorgobacka

In this release 1 issue was closed.  


## Version 0.6.9 (2022/07/03)

FitTrackee is now available in German (thanks to @gorgobacka).  
And translations can be updated on Weblate.

### Issues Closed

#### Features

* [#200](https://github.com/SamR1/FitTrackee/issues/200) - Detect browser language to use matching translation if available

#### Bugs Fixed

* [PR#208](https://github.com/SamR1/FitTrackee/pull/208) - fix order on records cards
* [#201](https://github.com/SamR1/FitTrackee/issues/201) - html lang attribute is not updated when changing language

#### Translations

* [PR#197](https://github.com/SamR1/FitTrackee/pull/197) - Translations update from Weblate (French)
* [#196](https://github.com/SamR1/FitTrackee/issues/196) - Use translation management tool
* [#190](https://github.com/SamR1/FitTrackee/issues/190) - Add German translation

In this release 4 issues were closed.  

Thanks to the contributors:
- @gorgobacka
- J. Lavoie (from Weblate)


## Version 0.6.8 (2022/06/22)

### Issues Closed

#### Bugs Fixed

* [#193](https://github.com/SamR1/FitTrackee/issues/193) - Allow deleting a workout when files are missing
* [#192](https://github.com/SamR1/FitTrackee/issues/192) - Returns 404 instead of 500 when map file not found
* [#191](https://github.com/SamR1/FitTrackee/issues/191) - Layout issue on Workouts page

### Misc

* change gpx and map file naming (included in [PR#195](https://github.com/SamR1/FitTrackee/pull/195))  
  Note: it does not affect previously imported files
* [cc4287e](https://github.com/SamR1/FitTrackee/commit/cc4287ed327faaba268a0c689841d16a7aecc3fb) - Fix docker env file

In this release 3 issues were closed.  

## Version 0.6.7 (2022/06/11)

### Issues Closed

#### Bugs Fixed

* [#156](https://github.com/SamR1/FitTrackee/issues/156) - Process gpx file with offset

In this release 1 issue was closed.  


## Version 0.6.6 (2022/05/29)

### Misc

No new features in this release, only dependencies update and code refacto before introducing new features.


## Version 0.6.5 (2022/04/24)

It is now possible to start FitTrackee without a configured SMTP provider (see [documentation](https://samr1.github.io/FitTrackee/installation.html#emails)).
It reduces pre-requisites for single-user instances.

To manage users, a new [CLI](https://samr1.github.io/FitTrackee/cli.html) is available.


### Issues Closed

#### Features

* [#180](https://github.com/SamR1/FitTrackee/issues/180) - allow using FitTrackee without SMTP server

In this release 1 issue was closed.  


## Version 0.6.4 (2022/04/23)

### Issues Closed

#### Bugs Fixed

* [#178](https://github.com/SamR1/FitTrackee/issues/178) - cannot send email with TLS

In this release 1 issue was closed.  


## Version 0.6.3 (2022/04/09)

### Pull Requests

#### Bugs Fixed

* [#177](https://github.com/SamR1/FitTrackee/pull/177) - Minor fixes 
  * add missing translation 
  * fix 'Add Workout' card position on small screens


## Version 0.6.2 (2022/04/03)

### Issues Closed

#### Bugs Fixed

* [#175](https://github.com/SamR1/FitTrackee/issues/175) - Distance card on dashboard is not refreshed
* [#173](https://github.com/SamR1/FitTrackee/issues/173) - link to user profile in workout card is incorrect

In this release 2 issues were closed.  


## Version 0.6.1 (2022/03/27)

### Issues Closed

#### Bugs Fixed

* [#171](https://github.com/SamR1/FitTrackee/issues/171) - Stats chart is not updated correctly 

In this release 1 issue was closed.  


## Version 0.6.0 (2022/03/27)

This version introduces some changes on [user registration](https://samr1.github.io/FitTrackee/features.html#account-preferences).  
From now on, a user needs to confirm his account after registration (an email with confirmation instructions is sent after registration).


### Issues Closed

#### Features

* [#155](https://github.com/SamR1/FitTrackee/issues/155) -  Improve user registration
* [#106](https://github.com/SamR1/FitTrackee/issues/106) -  Allow user to update email

#### Bugs Fixed

* [#169](https://github.com/SamR1/FitTrackee/issues/169) -  user picture is not refreshed after update

### Pull Requests

#### Bugs Fixed

* [#161](https://github.com/SamR1/FitTrackee/pull/161) - Minor translation issue on 'Farthest'
* [#160](https://github.com/SamR1/FitTrackee/pull/160) - Minor translation issue on APP_ERROR

Thanks to @Fmstrat

In this release 3 issues were closed.  
**Note:** This release contains database migration (see upgrade instructions in [documentation](https://samr1.github.io/FitTrackee/installation.html#upgrade))


## Version 0.5.7 (2022/02/13)

This release contains several fixes including security fixes.  
Thanks to @DanielSiersleben for the report.

And from now on, admin account is not created on application initialization.  
A new command is added to set administration rights on the account created after registration 
(see [documentation](https://samr1.github.io/FitTrackee/installation.html#upgrade))

### Issues Closed

#### Misc

* [#149](https://github.com/SamR1/FitTrackee/issues/149) - improve database initialisation

### Pull Requests

#### Security

* [#152](https://github.com/SamR1/FitTrackee/pull/152) - Fixes and improvements:
  - set autoescape on jinja templates

* [#151](https://github.com/SamR1/FitTrackee/pull/151) - fix security issues:
  - sanitize input when serving images
  - sanitize inputs when serving map tiles
  - allow only alphanumeric characters and '_' in username

#### Misc

* [#152](https://github.com/SamR1/FitTrackee/pull/152) - Fixes and improvements:
  - fix dramatiq warning when launching workers w/ script entrypoint
  - check app config before dropping database, to avoid deleting data on production
  - remove dotenv warning

In this release 1 issue was closed.


## Version 0.5.6 (2022/02/05)

### Issues Closed

#### Bugs Fixed

* [#146](https://github.com/SamR1/FitTrackee/issues/146) - incorrect label on workouts filters

### Pull Requests

* [#145](https://github.com/SamR1/FitTrackee/pull/145) - fix on database models 


In this release 1 issue was closed.  
**Note:** This release contains database migration (see upgrade instructions in [documentation](https://samr1.github.io/FitTrackee/installation.html#upgrade))


## Version 0.5.5 (2022/01/19)

### Issues Closed

#### New Features

* [#140](https://github.com/SamR1/FitTrackee/issues/140) - Add a fullscreen control to workout map
* [#138](https://github.com/SamR1/FitTrackee/issues/138) - Add control to reset map to initial position
* [#135](https://github.com/SamR1/FitTrackee/issues/135) - Start and finish markers
* [#134](https://github.com/SamR1/FitTrackee/issues/134) - Wind direction

#### Bugs Fixed

* [877fa0f](https://github.com/SamR1/FitTrackee/commit/877fa0faaabc0130402638905fe04f84563eb278) - fix sport icon color (when changed) on calendar on small resolutions

In this release 4 issues were closed.


## Version 0.5.4 (2022/01/01)

### Issues Closed

#### Bugs Fixed

* [#131](https://github.com/SamR1/FitTrackee/issues/131) - No workouts displayed on calendar

In this release 1 issue was closed.


## Version 0.5.3 (2022/01/01)

### Issues Closed

#### Bugs Fixed

* [#129](https://github.com/SamR1/FitTrackee/issues/129) - Display only active sports when editing a workout
* [#127](https://github.com/SamR1/FitTrackee/issues/127) - parse_email_url() can't validate a legitimate EMAIL_URI such as "smtp://localhost:25"

In this release 2 issues were closed.


## Version 0.5.2 (2021/12/19)

### Issues Closed

#### New Features

* [#123](https://github.com/SamR1/FitTrackee/issues/123) - Allow user to reset preferences for a sport
* [#121](https://github.com/SamR1/FitTrackee/issues/121) - Add activity : snowshoes

In this release 2 issues were closed.  
**Note:** This release contains database migration.


## Version 0.5.1 (2021/11/30)

### Issues Closed

#### New Features

* [#116](https://github.com/SamR1/FitTrackee/issues/116) - Better UI for Speed and Elevation buttons in the graph of the Workout screen
* [#115](https://github.com/SamR1/FitTrackee/issues/115) - Add option to download the GPX file of a Workout
* [#5](https://github.com/SamR1/FitTrackee/issues/5) - Display a chart with average speed

In this release 3 issues were closed.  


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
