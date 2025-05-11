# Change log

## Version 0.9.10 (2025/05/11)

### Features and enhancements

* [#795](https://github.com/SamR1/FitTrackee/issues/795) - New sport: Windsurfing

### Bugs Fixed

* [#793](https://github.com/SamR1/FitTrackee/issues/793) - Number-template for duration fields in new workout

### Translations

* [PR#787](https://github.com/SamR1/FitTrackee/pull/787) - Translations update (Galician, Polish)
* [PR#789](https://github.com/SamR1/FitTrackee/pull/789) - Translations update (Dutch)

Translation status:
- Basque: 99%
- Bulgarian: 62%
- Chinese (Simplified): 99%
- Croatian: 99%
- Czech: 46%
- Dutch: 99%
- English: 100%
- French: 100%
- Galician: 99%
- German: 98%
- Italian: 51%
- Norwegian Bokmål: 33%
- Polish: 99%
- Portuguese: 61%
- Russian: 38%
- Spanish: 64%


Thanks to the contributors:
- @JcMinarro
- @xmgz
- Wiktor Jędrzejczak

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


## Version 0.9.9 (2025/05/03)

### Bugs Fixed

* [#780](https://github.com/SamR1/FitTrackee/issues/780) - y-Axis in monthly statistics on Dashboard not shown properly


### Translations

* [PR#781](https://github.com/SamR1/FitTrackee/pull/781) - Translations update (Croatian)
* [PR#783](https://github.com/SamR1/FitTrackee/pull/783) - Translations update (Dutch)

Translation status:
- Basque: 100%
- Bulgarian: 62%
- Chinese (Simplified): 99%
- Croatian: 100%
- Czech: 46%
- Dutch: 100%
- English: 100%
- French: 100%
- Galician: 100%
- German: 98%
- Italian: 51%
- Norwegian Bokmål: 33%
- Polish: 97%
- Portuguese: 61%
- Russian: 39%
- Spanish: 63%


Thanks to the contributors:
- @iggydev
- @JeroenED


## Version 0.9.8 (2025/04/27)

### Bugs Fixed

* [PR#779](https://github.com/SamR1/FitTrackee/pull/779) - Fix segments navigation when user is not workout owner


### Translations

* [PR#769](https://github.com/SamR1/FitTrackee/pull/769) - Translations update (Chinese (Simplified Han script))
* [PR#770](https://github.com/SamR1/FitTrackee/pull/770) - Translations update (Galician)
* [#773](https://github.com/SamR1/FitTrackee/issues/773) - [translations request] Croatian
* [PR#774](https://github.com/SamR1/FitTrackee/pull/774) - Translations update (Basque)

Translation status:
- Basque: 100%
- Bulgarian: 62%
- Chinese (Simplified): 99%
- Croatian: 100%
- Czech: 46%
- Dutch: 98%
- English: 100%
- French: 100%
- Galician: 100%
- German: 98%
- Italian: 51%
- Norwegian Bokmål: 33%
- Polish: 97%
- Portuguese: 61%
- Russian: 39%
- Spanish: 63%


Thanks to the contributors:
- @erral
- @iggydev
- @xmgz
- Poesty Li


## Version 0.9.7 (2025/04/20)

### Features and enhancements

* [PR#764](https://github.com/SamR1/FitTrackee/pull/764) - New sport: Halfbike
  * [PR#768](https://github.com/SamR1/FitTrackee/pull/768) - add equipment (bike) to Halfbike workouts
* [PR#767](https://github.com/SamR1/FitTrackee/pull/767) - Add averages in workouts list


### Translations

* [PR#765](https://github.com/SamR1/FitTrackee/pull/765) - Translations update (Dutch)

Translation status:
- Basque: 81%
- Bulgarian: 62%
- Chinese (Simplified): 98%
- Czech: 46%
- Dutch: 98%
- English: 100%
- French: 100%
- Galician: 98%
- German: 98%
- Italian: 51%
- Norwegian Bokmål: 33%
- Polish: 97%
- Portuguese: 61%
- Russian: 39%
- Spanish: 63%


Thanks to the contributors:
- @astridx
- @JeroenED

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


## Version 0.9.6 (2025/04/16)

### Translations

* [PR#762](https://github.com/SamR1/FitTrackee/pull/762) - Init Bengali translations files
* [PR#763](https://github.com/SamR1/FitTrackee/pull/763) - Translations update (German)

Translation status:
- Basque: 82%
- Bulgarian: 63%
- Chinese (Simplified): 100%
- Czech: 46%
- Dutch: 63%
- English: 100%
- French: 100%
- Galician: 100%
- German: 100%
- Italian: 52%
- Norwegian Bokmål: 33%
- Polish: 98%
- Portuguese: 62%
- Russian: 39%
- Spanish: 63%

### Misc

* [2bc97bd](https://github.com/SamR1/FitTrackee/commit/2bc97bda644197dce5ccac9048889321209f84ac) - CI - run coverage only on one test job


Thanks to the contributors:
- @astridx
- @frankzimper


## Version 0.9.5 (2025/04/06)

### Bugs Fixed

* [#751](https://github.com/SamR1/FitTrackee/issues/751) - Time in Analysis is not correct in overlay modal
* [#753](https://github.com/SamR1/FitTrackee/issues/753) - the checkbox "start elevation axis at zero" has no effect
* [PR#757](https://github.com/SamR1/FitTrackee/pull/757) - Fix tasks queue running on Python 3.13  
  **Note**: It is now possible to use Dramatiq CLI directly to run task queue workers, see [documentation](https://docs.fittrackee.org/en/installation.html).
  A new environment (`DRAMATIQ_LOG`) variable has also been added.
* [PR#760](https://github.com/SamR1/FitTrackee/pull/760) - Fix docker files
* [1f8ca78](https://github.com/SamR1/FitTrackee/commit/1f8ca78b82e3b0d91c176a3628bcffeae99e306b) - delete all temporary files when exporting user data export

### Translations

* [PR#745](https://github.com/SamR1/FitTrackee/pull/745) - Translations update (Galician)
* [PR#749](https://github.com/SamR1/FitTrackee/pull/749) - Translations update (Chinese (Simplified Han script))
* [PR#750](https://github.com/SamR1/FitTrackee/pull/750) - Translations update (German)
* [PR#752](https://github.com/SamR1/FitTrackee/pull/752) - Translations update (Galician)
* [PR#756](https://github.com/SamR1/FitTrackee/pull/756) - Translations update (Galician)

Translation status:
- Basque: 82%
- Bulgarian: 63%
- Chinese (Simplified): 100%
- Czech: 46%
- Dutch: 63%
- English: 100%
- French: 100%
- Galician: 100%
- German: 86%
- Italian: 52%
- Norwegian Bokmål: 33%
- Polish: 98%
- Portuguese: 62%
- Russian: 39%
- Spanish: 63%

### Misc

* [PR#746](https://github.com/SamR1/FitTrackee/pull/746) - email tasks refactoring


Thanks to the contributors:
- @glggr
- @xmgz
- Poesty Li


## Version 0.9.4 (2025/03/26)

### Features and enhancements

* [#117](https://github.com/SamR1/FitTrackee/issues/117) - Total data of filtered workouts
* [PR#736](https://github.com/SamR1/FitTrackee/pull/736) - Display date with browser settings when user is unlogged
* [PR#737](https://github.com/SamR1/FitTrackee/pull/737) - Register user with time zone detected from browser

### Bugs Fixed

* [#731](https://github.com/SamR1/FitTrackee/issues/731) - date format inconsistency in statistics
* [#739](https://github.com/SamR1/FitTrackee/issues/739) - total duration displayed on the dashboard is incorrect

### Translations

* [PR#732](https://github.com/SamR1/FitTrackee/pull/732) - Translations update (Basque, Galician)
* [PR#734](https://github.com/SamR1/FitTrackee/pull/734) - Translations update (Basque)
* [PR#735](https://github.com/SamR1/FitTrackee/pull/735) - Translations update (Chinese (Simplified Han script))
* [PR#738](https://github.com/SamR1/FitTrackee/pull/738) - Translations update (Galician, German)
* [PR#740](https://github.com/SamR1/FitTrackee/pull/740) - Translations update (Basque)

Translation status:
- Basque: 82%
- Bulgarian: 63%
- Chinese (Simplified): 98%
- Czech: 46%
- Dutch: 63%
- English: 100%
- French: 100%
- Galician: 99%
- German: 85%
- Italian: 52%
- Norwegian Bokmål: 33%
- Polish: 98%
- Portuguese: 62%
- Russian: 39%
- Spanish: 63%

Thanks to the contributors:
- @erral
- @Medformatik
- @xmgz
- Poesty Li


## Version 0.9.3 (2025/03/15)

### Features and enhancements

* [#714](https://github.com/SamR1/FitTrackee/issues/714) - New sports: Kayaking and Canoeing
* [PR#719](https://github.com/SamR1/FitTrackee/pull/719) - Filter workouts according to visibility in workout list
* [#722](https://github.com/SamR1/FitTrackee/issues/722) - Statistics per day

### Bugs Fixed

* [PR#725](https://github.com/SamR1/FitTrackee/pull/725) - Workout files upload fixes, including:
  * [#716](https://github.com/SamR1/FitTrackee/issues/716) - Trouble importing tracks
  * [#720](https://github.com/SamR1/FitTrackee/issues/720) - Increase WORKER TIMEOUT
* [PR#728](https://github.com/SamR1/FitTrackee/pull/728) - fixed docker-compose.yml

### Translations

* [PR#713](https://github.com/SamR1/FitTrackee/pull/713) - Translations update (Basque, German)
* [PR#721](https://github.com/SamR1/FitTrackee/pull/721) - Translations update (Chinese (Simplified Han script), Galicien, German)
* [PR#726](https://github.com/SamR1/FitTrackee/pull/726) - Translations update (German)
* [PR#729](https://github.com/SamR1/FitTrackee/pull/729) - Translations update (Galician)

Translation status:
- Basque: 81%
- Bulgarian: 63%
- Chinese (Simplified): 99%
- Czech: 46%
- Dutch: 64%
- English: 100%
- French: 100%
- Galician: 99%
- German: 85%
- Italian: 52%
- Norwegian Bokmål: 34%
- Polish: 99%
- Portuguese: 62%
- Russian: 39%
- Spanish: 64%

### Misc

* [PR#717](https://github.com/SamR1/FitTrackee/pull/717) - Adds YAML bug report template

Thanks to the contributors:
- @erral
- @LordSexy
- @mbw83
- @OliverPifferi
- @slackline
- @Von-Birne
- @xmgz
- Poesty Li

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


## Version 0.9.2 (2025/02/12)

### Translations

* [PR#711](https://github.com/SamR1/FitTrackee/pull/711) - Translations update (Chinese (Simplified Han script))
* [PR#712](https://github.com/SamR1/FitTrackee/pull/712) - Translations update (Polish, Basque)

Translation status:
- Basque: 73%
- Bulgarian: 64%
- Chinese (Simplified): 100%
- Czech: 47%
- Dutch: 64%
- English: 100%
- French: 100%
- Galician: 100%
- German: 76%
- Italian: 53%
- Norwegian Bokmål: 34%
- Polish: 100%
- Portuguese: 63%
- Russian: 40%
- Spanish: 64%

### Misc

* [2612cd9](https://github.com/SamR1/FitTrackee/commit/2612cd9e4aa747036b79ed4a8492d0f7fea60c80) - fix Dockerfile used for development

Thanks to the contributors:
- @erral
- Poesty Li
- Wiktor Jędrzejczak


## Version 0.9.1 (2025/02/02)

**Note**: The minimum version for Python is now 3.9.2.

### Features and enhancements

* [PR#709](https://github.com/SamR1/FitTrackee/pull/709) - Display equipment in workout detail for other users depending on visibility

### Bugs Fixed

* [#708](https://github.com/SamR1/FitTrackee/issues/708) - Cannot add/update equipment description 
* [PR#707](https://github.com/SamR1/FitTrackee/pull/707) - Display user workouts only on user profile

### Translations

* [PR#700](https://github.com/SamR1/FitTrackee/pull/700) - Translations update (Chinese (Simplified Han script))
* [PR#702](https://github.com/SamR1/FitTrackee/pull/702) - Translations update (German, Chinese (Simplified Han script))
* [PR#705](https://github.com/SamR1/FitTrackee/pull/705) - Translations update (Polish)

Translation status:
- Basque: 72%
- Bulgarian: 64%
- Chinese (Simplified): 100%
- Czech: 47%
- Dutch: 64%
- English: 100%
- French: 100%
- Galician: 100%
- German: 76%
- Italian: 53%
- Norwegian Bokmål: 34%
- Polish: 88%
- Portuguese: 63%
- Russian: 40%
- Spanish: 64%

### Misc

* [#355](https://github.com/SamR1/FitTrackee/issues/355) - Update SQLAlchemy to 2.x
* [#685](https://github.com/SamR1/FitTrackee/issues/599) - replace deprecated datetime.utcnow()
* [b224e17](https://github.com/SamR1/FitTrackee/commit/b224e171c750dcfc3ca9c03068f91e21dd7eb189) - tools - update ruff config

Thanks to the contributors:
- @OliverPifferi
- Poesty Li
- Wiktor Jędrzejczak

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


## Version 0.9.0 (2025/01/18)

**FitTrackee** now allows you to follow other users, view their workouts according to the level of visibility and interact with them.

The default privacy policy has been updated, as well as the link to the documentation.

**Note**: This version also includes the changes from the beta versions.

### Features and enhancements

* [#16](https://github.com/SamR1/FitTrackee/issues/16) - Add social features [1st part]
  * [#125](https://github.com/SamR1/FitTrackee/issues/125) - Add followers/following and visibility levels
  * [#296](https://github.com/SamR1/FitTrackee/issues/296) - Add comments
  * [#298](https://github.com/SamR1/FitTrackee/issues/298) - Add likes
  * [#299](https://github.com/SamR1/FitTrackee/issues/299) - UI notifications
  * [#381](https://github.com/SamR1/FitTrackee/issues/381) - Block a user to hide unwanted content
  * [#382](https://github.com/SamR1/FitTrackee/issues/382) - Moderation tools
  * [#655](https://github.com/SamR1/FitTrackee/issues/655) - Add moderator and owner roles
  * [PR#666](https://github.com/SamR1/FitTrackee/pull/666) - Display last 5 workouts in user profile
* [PR#675](https://github.com/SamR1/FitTrackee/pull/675) - CLI - create user with provided role
* [#691](https://github.com/SamR1/FitTrackee/issues/691) Support Markdown syntax in description and notes 

### Bugs Fixed

* [#664](https://github.com/SamR1/FitTrackee/issues/664) - privacy policy validation is not displayed
* [#682](https://github.com/SamR1/FitTrackee/issues/682) - Monthly statistics are incorrect
* [#683](https://github.com/SamR1/FitTrackee/issues/683) - User time zone is not taken into account in statistics
* [#680](https://github.com/SamR1/FitTrackee/issues/680) - accessibility and style fixes

### Translations

* [PR#688](https://github.com/SamR1/FitTrackee/pull/688) - Translations update (Basque, Galician)
* [PR#690](https://github.com/SamR1/FitTrackee/pull/690) - Translations update (English, French, Basque, Galician)
* [PR#692](https://github.com/SamR1/FitTrackee/pull/692) - Translations update (French)
* [PR#695](https://github.com/SamR1/FitTrackee/pull/695) - Translations update (Chinese)
* [PR#696](https://github.com/SamR1/FitTrackee/pull/696) - Translations update (Galician)
* [#697](https://github.com/SamR1/FitTrackee/issues/697) - [translations request] Chinese (Simplified Han script) (zh_Hans) 

Translation status:
- Basque: 72%
- Bulgarian: 64%
- Chinese (Simplified): 48%
- Czech: 47%
- Dutch: 64%
- English: 100%
- French: 100%
- Galician: 100%
- German: 64%
- Italian: 53%
- Norwegian Bokmål: 34%
- Polish: 64%
- Portuguese: 63%
- Russian: 64%
- Spanish: 64%

### Misc

* [PR#685](https://github.com/SamR1/FitTrackee/pull/685) - Update link to documentation

Thanks to the contributors:
- @erral
- @xmgz
- Poesty Li

**Note:** If you upgrade from the v0.8.x, there are migrations to apply (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


## Version 0.9.0b6 (2025/01/05)

**This is a pre-release. Don't install this version in production, you may not be able to safely downgrade to a stable version.**  
If you find bugs, please report them.


### Features and enhancements

* [PR#677](https://github.com/SamR1/FitTrackee/pull/677) - Add notification preferences
* [PR#678](https://github.com/SamR1/FitTrackee/pull/678) - Display users who like comment/workout

### Bugs Fixed

* [d743abf](https://github.com/SamR1/FitTrackee/commit/d743abf0e59a3c7cc1e11adbd9c8d0214d0c7da7) - display missing errors in user profile


**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


## Version 0.9.0b5 (2024/12/30)

**This is a pre-release. Don't install this version in production, you may not be able to safely downgrade to a stable version.**  
If you find bugs, please report them.


### Features and enhancements

* [PR#675](https://github.com/SamR1/FitTrackee/pull/675) - CLI - create user with provided role

### Bugs Fixed

* [PR#671](https://github.com/SamR1/FitTrackee/pull/671) - Fix sport icon when unauthenticated user displays user profile
* [PR#674](https://github.com/SamR1/FitTrackee/pull/674) - Fix display of privacy policy message with privacy extension
* [2e9f9d](https://github.com/SamR1/FitTrackee/commit/2e9f9d69eb38d5f310236944d45b4b60d8faff20) - fix translations
* [edc677](https://github.com/SamR1/FitTrackee/commit/edc6776c922925746762f7ac76c267feda7cde2f) - Fix notification icons

### Misc

* [174240](https://github.com/SamR1/FitTrackee/commit/174240f1d9dc702d4346c85e6add4022af2a88c6) - add tags input to docker image build job


## Version 0.8.13 (2024/12/29)

### Translations

* [PR#667](https://github.com/SamR1/FitTrackee/pull/667) - Translations update (Galician)

Translation status:
- Basque: 100%
- Bulgarian: 98%
- Czech: 72%
- Dutch: 99%
- English: 100%
- French: 100%
- Galician: 100%
- German: 100%
- Italian: 81%
- Norwegian Bokmål: 52%
- Polish: 100%
- Portuguese: 97%
- Russian: 62%
- Spanish: 100%

### Misc

* [#126](https://github.com/SamR1/FitTrackee/issues/126) - Docker's Container on docker hub
* [PR#673](https://github.com/SamR1/FitTrackee/pull/673) - Publish package on PyPI using GitHub Actions workflow


Thanks to the contributors:
- @DavidHenryThoreau
- @xmgz


## Version 0.9.0b4 (2024/12/23)

**This is a pre-release. Don't install this version in production, you may not be able to safely downgrade to a stable version.**  
If you find bugs, please report them.

### Features and enhancements

* [PR#666](https://github.com/SamR1/FitTrackee/pull/666) - Display last 5 workouts in user detail
* [#668](https://github.com/SamR1/FitTrackee/issues/668) - add analysis visibility
* [PR#67](https://github.com/SamR1/FitTrackee/pull/670) - create notification when follow request is approved

### Bugs Fixed

* [#664](https://github.com/SamR1/FitTrackee/issues/664) - privacy policy validation is not displayed

### Translations

* [PR#667](https://github.com/SamR1/FitTrackee/pull/667) - Translations update (Galician)

Thanks to the contributors:
- @xmgz


**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


## Version 0.9.0b3 (2024/12/18)

**This is a pre-release. Don't install this version in production, you may not be able to safely downgrade to a stable version.**  
If you find bugs, please report them.

### Features and enhancements

* [#660](https://github.com/SamR1/FitTrackee/issues/660) - mark notification as read on click on workout/comment/...

### Bugs Fixed

* [PR#659](https://github.com/SamR1/FitTrackee/pull/659) - API - get workouts list with equipment
* [PR#662](https://github.com/SamR1/FitTrackee/pull/662) - Minor fixes and improvements

### Misc

* [189071](https://github.com/SamR1/FitTrackee/commit/189071a949ef7cb0c01e8dedcb267af742daefa4) - use uuid instead of id for notifications


**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


## Version 0.9.0b2 (2024/12/14)

**This is a pre-release. Don't install this version in production, you may not be able to safely downgrade to a stable version.**  
If you find bugs, please report them.

### Bugs Fixed

* [#657](https://github.com/SamR1/FitTrackee/issues/657) - can not display next workouts in timeline


## Version 0.9.0b1 (2024/12/14)

**This is a pre-release. Don't install this version in production, you may not be able to safely downgrade to a stable version.**  
If you find bugs, please report them.

### Features and enhancements

* [#16](https://github.com/SamR1/FitTrackee/issues/16) - Add social features [1st part]
  * [#125](https://github.com/SamR1/FitTrackee/issues/125) - Add followers/following and visibility levels
  * [#296](https://github.com/SamR1/FitTrackee/issues/296) - Add comments
  * [#298](https://github.com/SamR1/FitTrackee/issues/298) - Add likes
  * [#299](https://github.com/SamR1/FitTrackee/issues/299) - UI notifications
  * [#381](https://github.com/SamR1/FitTrackee/issues/381) - Block a user to hide unwanted content
  * [#382](https://github.com/SamR1/FitTrackee/issues/382) - Moderation tools
  * [#655](https://github.com/SamR1/FitTrackee/issues/655) - Add moderator and owner roles

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))

## Version 0.8.12 (2024/11/17)

### Bugs Fixed

* [#652](https://github.com/SamR1/FitTrackee/issues/652) - User can not login on new installation

### Misc

* [PR#651](https://github.com/SamR1/FitTrackee/pull/651) - Tests - add databases to parallelize more tests



## Version 0.8.11 (2024/10/30)

**FitTrackee** is now available for Python 3.13.
Python 3.8 is no longer supported, the minimum version is now Python 3.9.

### Translations

* [PR#640](https://github.com/SamR1/FitTrackee/pull/640) - Translations update (Basque)
* [PR#645](https://github.com/SamR1/FitTrackee/pull/645) - Translations update (Russian, Polish)

Translation status:
- Basque: 100%
- Bulgarian: 98%
- Czech: 72%
- Dutch: 99%
- English: 100%
- French: 100%
- Galician: 100%
- German: 100%
- Italian: 81%
- Norwegian Bokmål: 52%
- Polish: 100%
- Portuguese: 97%
- Russian: 62%
- Spanish: 100%

### Misc

* [#455](https://github.com/SamR1/FitTrackee/issues/455) - Drop support for Python 3.8
* [#639](https://github.com/SamR1/FitTrackee/issues/639) - Add support for Python 3.13


Thanks to the contributors:
- @erral
- @sikmir
- Mariuz


## Version 0.8.10 (2024/10/09)

### Features and enhancements

* [PR#635](https://github.com/SamR1/FitTrackee/pull/635) - Add ability to replace gpx title when adding a workout
* [PR#636](https://github.com/SamR1/FitTrackee/pull/636) - Get description from gpx file if present 

### Translations

* [#629](https://github.com/SamR1/FitTrackee/issues/629) - [Translation Request] Russian
* [PR#633](https://github.com/SamR1/FitTrackee/pull/633) - Translations update (Russian, Dutch, Italian, Galician)
* [PR#637](https://github.com/SamR1/FitTrackee/pull/637) - Translations update (Spanish, Russian, German and Galician)

Translation status:
- Basque: 99%
- Bulgarian: 98%
- Czech: 72%
- Dutch: 99%
- English: 100%
- French: 100%
- Galician: 100%
- German: 100%
- Italian: 81%
- Norwegian Bokmål: 52%
- Polish: 98%
- Portuguese: 97%
- Russian: 61%
- Spanish: 100%

### Misc

* [PR#634](https://github.com/SamR1/FitTrackee/pull/634) - CI - add PostgreSQL 17


Thanks to the contributors:
- @boosterl
- @gallegonovato
- @qwerty287
- @Shura0
- @sikmir
- @xmgz


## Version 0.8.9 (2024/09/21)

This release introduces a new field: the workout description.  
This field is longer than the "Notes" field and will have the same visibility as the workout in a next version (see [#125](https://github.com/SamR1/FitTrackee/issues/125)). The "Notes" field will remain private.

### Features and enhancements

* [#610](https://github.com/SamR1/FitTrackee/issues/610) - Add a description field to workout

### Bugs Fixed

* [#621](https://github.com/SamR1/FitTrackee/issues/621) - email username may contain special characters
* [#622](https://github.com/SamR1/FitTrackee/issues/622) - Fix email sending by adding 'Message-ID'

### Translations

* [PR#616](https://github.com/SamR1/FitTrackee/pull/616) - Translations update (Dutch)
* [PR#617](https://github.com/SamR1/FitTrackee/pull/617) - Translations update (Italian)
* [PR#618](https://github.com/SamR1/FitTrackee/pull/618) - Translations update (Polish)
* [PR#620](https://github.com/SamR1/FitTrackee/pull/620) - Translations update (Polish)
* [PR#624](https://github.com/SamR1/FitTrackee/pull/624) - Translations update (Spanish)
* [PR#625](https://github.com/SamR1/FitTrackee/pull/625) - Translations update (Galician and Basque)
* [PR#626](https://github.com/SamR1/FitTrackee/pull/626) - Translations update (German)
* [PR#631](https://github.com/SamR1/FitTrackee/pull/631) - Translations update (Basque)

Translation status:
- Basque: 100%
- Bulgarian: 99%
- Czech: 72%
- Dutch: 99%
- English: 100%
- French: 100%
- Galician: 100%
- German: 100%
- Italian: 82%
- Norwegian Bokmål: 52%
- Polish: 99%
- Portuguese: 97%
- Spanish: 100%

### Misc

* [PR#628](https://github.com/SamR1/FitTrackee/pull/628) - Replace markdown library


Thanks to the contributors:
- @boosterl
- @byakurau
- @dotlambda
- @erral
- @gallegonovato
- @qwerty287
- @xmgz

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


## Version 0.8.8 (2024/09/01)

**FitTrackee** is now available in Bulgarian.

### Bugs Fixed

* [#614](https://github.com/SamR1/FitTrackee/issues/614) - Labels are not translated on workouts average chart

### Translations

* [PR#607](https://github.com/SamR1/FitTrackee/pull/607) - Translations update (German)
* [#608](https://github.com/SamR1/FitTrackee/issues/608) - [translations request] Bulgarian
* [PR#609](https://github.com/SamR1/FitTrackee/pull/609) - Translations update (Galician and Spanish)
* [PR#612](https://github.com/SamR1/FitTrackee/pull/612) - Translations update (Bulgarian and Czech)

 
Translation status:
- Basque: 99%
- Bulgarian: 100%
- Czech: 73%
- Dutch: 99%
- English: 100%
- French: 100%
- Galician: 100%
- German: 100%
- Italian: 82%
- Norwegian Bokmål: 52%
- Polish: 91%
- Portuguese: 98%
- Spanish: 100%


Thanks to the contributors:
- @gallegonovato
- @jmlich
- @mara21
- @qwerty287
- @xmgz


## Version 0.8.7 (2024/08/25)

### Features and enhancements

* [#604](https://github.com/SamR1/FitTrackee/issues/604) - New sport: Swimrun

### Bugs Fixed

* [PR#598](https://github.com/SamR1/FitTrackee/pull/598) - CLI - fix limit for user data export cleanup

### Translations

* [PR#600](https://github.com/SamR1/FitTrackee/pull/600) - Translations update (Galician)
* [PR#603](https://github.com/SamR1/FitTrackee/pull/603) - Translations update (Basque)

 
Translation status:
- Basque: 99%
- Czech: 72%
- Dutch: 99%
- English: 100%
- French: 100%
- Galician: 99%
- German: 98%
- Italian: 82%
- Norwegian Bokmål: 52%
- Polish: 91%
- Portuguese: 98%
- Spanish: 99%


Thanks to the contributors:
- @erral
- @xmgz

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


## Version 0.8.6 (2024/08/03)

### Translations

* [PR#590](https://github.com/SamR1/FitTrackee/pull/590) - Translations update (Italian)
* [PR#591](https://github.com/SamR1/FitTrackee/pull/591) - Translations update (Galician)
* [PR#592](https://github.com/SamR1/FitTrackee/pull/592) - Translations update (German, Dutch)
* [PR#593](https://github.com/SamR1/FitTrackee/pull/593) - Translations update (German)
* [fb10602](https://github.com/SamR1/FitTrackee/commit/fb10602c47c426c432f528a1ecaf0b2dd4759e93) - update and fix translations
 
Translation status:
- Basque: 98%
- Czech: 73%
- Dutch: 100%
- English: 100%
- French: 100%
- Galician: 100%
- German: 99%
- Italian: 82%
- Norwegian Bokmål: 52%
- Polish: 92%
- Portuguese: 98%
- Spanish: 100%

### Misc

* [PR#595](https://github.com/SamR1/FitTrackee/pull/595) - CI - speed up tests


Thanks to the contributors:
- @ConfusedAlex
- @lukasitaly
- @simontb
- @slothje
- @xmgz


## Version 0.8.5 (2024/06/29)

### Features and enhancements

* [#566](https://github.com/SamR1/FitTrackee/issues/566) - [Feature] Improved statistics section with average calculation
* [PR#575](https://github.com/SamR1/FitTrackee/pull/575) - Add page to display sport statistics
* [PR#587](https://github.com/SamR1/FitTrackee/pull/587) - Improve user forms

### Bugs Fixed

* [PR#588](https://github.com/SamR1/FitTrackee/pull/588) - Fix click on workout chart checkbox labels

### Translations

* [PR#564](https://github.com/SamR1/FitTrackee/pull/564) - Translations update (Dutch)
* [PR#565](https://github.com/SamR1/FitTrackee/pull/565) - Translations update (Polish)
* [PR#571](https://github.com/SamR1/FitTrackee/pull/571) - Translations update (Galician, Spanish)
* [PR#582](https://github.com/SamR1/FitTrackee/pull/582) - Translations update (Galician, Spanish)
 
Translation status:
- Basque: 98%
- Czech: 73%
- Dutch: 98%
- English: 100%
- French: 100%
- Galician: 100%
- German: 98%
- Italian: 73%
- Norwegian Bokmål: 52%
- Polish: 92%
- Portuguese: 98%
- Spanish: 100%

### Misc

* [PR#583](https://github.com/SamR1/FitTrackee/pull/583) - Simplify docker deployment


Thanks to the contributors:
- @byakurau
- @gallegonovato
- @jderuiter
- @pluja
- @xmgz

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


## Version 0.8.4 (2024/05/22)

**FitTrackee** is now available in Portuguese.

### Features and enhancements

* [f2aec30](https://github.com/SamR1/FitTrackee/commit/f2aec301e18bdf0ae506db6eb013f76d5c99eff1) - add password strength estimation for Czech
* [#563](https://github.com/SamR1/FitTrackee/issues/563) - CLI - init language preference on user creation

### Translations

* [#550](https://github.com/SamR1/FitTrackee/issues/550) - Typo: par page instead of per page
* [PR#551](https://github.com/SamR1/FitTrackee/pull/551) - Translations update (Czech)
* [PR#555](https://github.com/SamR1/FitTrackee/pull/555) - Translations update (Czech)
* [#558](https://github.com/SamR1/FitTrackee/issues/558) - [translations request] Portuguese
 
Translation status:
- Basque: 100%
- Czech: 74%
- Dutch: 98%
- English: 100%
- French: 100%
- Galician: 100%
- German: 100%
- Italian: 74%
- Norwegian Bokmål: 53%
- Polish: 88%
- Portuguese: 100%
- Spanish: 100%

### Misc

* [PR#556](https://github.com/SamR1/FitTrackee/pull/556) - API - minor refacto
* [PR#557](https://github.com/SamR1/FitTrackee/pull/557) - API - prepare SQLAlchemy migration

Thanks to the contributors:
- @jmlich
- @voodoopt


## Version 0.8.3 (2024/05/09)

### Bugs Fixed

* [#546](https://github.com/SamR1/FitTrackee/issues/546) - workout data are not refreshed after displaying segment

### Translations

* [PR#545](https://github.com/SamR1/FitTrackee/pull/545) - Translations update (Basque, Czech)

Translation status:
- Basque: 100%
- Czech: 25%
- Dutch: 98%
- English: 100%
- French: 100%
- Galician: 100%
- German: 100%
- Italian: 74%
- Norwegian Bokmål: 53%
- Polish: 88%
- Spanish: 100%


Thanks to the contributors:
- @jmlich
- @urtzai


## Version 0.8.2 (2024/05/08)

### Translations

* [PR#540](https://github.com/SamR1/FitTrackee/pull/540) - Translations update (German)
* [PR#542](https://github.com/SamR1/FitTrackee/pull/542) - Translations update (Czech)
* [PR#544](https://github.com/SamR1/FitTrackee/pull/544) - Translations update (German, Czech)

Translation status:
- Basque: 88%
- Czech: 25%
- Dutch: 98%
- English: 100%
- French: 100%
- Galician: 100%
- German: 100%
- Italian: 74%
- Norwegian Bokmål: 53%
- Polish: 88%
- Spanish: 100%

### Misc

* [PR#543](https://github.com/SamR1/FitTrackee/pull/543) - tools - replace black, flake8 and isort with ruff


Thanks to the contributors:
- @jmlich
- @OndrejZivny
- @qwerty287


## Version 0.8.1 (2024/05/01)

### Features and enhancements

* [PR#527](https://github.com/SamR1/FitTrackee/pull/527) - improve Sports endpoints response time

### Bugs Fixed

* [PR#531](https://github.com/SamR1/FitTrackee/pull/531) - Minor navigation fixes on mobile
* [PR#532](https://github.com/SamR1/FitTrackee/pull/532) - Fix footer color on dark mode
* [PR#536](https://github.com/SamR1/FitTrackee/pull/536) - Accessibility fixes

### Translations

* [PR#526](https://github.com/SamR1/FitTrackee/pull/526) - Translations update (Dutch, Galician, Norwegian Bokmål)
* [PR#533](https://github.com/SamR1/FitTrackee/pull/533) - Translations update (Czech)
* [#534](https://github.com/SamR1/FitTrackee/issues/534) - [translations request] Czech
* [PR#537](https://github.com/SamR1/FitTrackee/pull/537) - Translations update (Spanish)
* [PR#538](https://github.com/SamR1/FitTrackee/pull/538) - Translations update (Galician)

Translation status:
- Basque: 88%
- Czech: 15%
- Dutch: 98%
- English: 100%
- French: 100%
- Galician: 100%
- German: 88%
- Italian: 74%
- Norwegian Bokmål: 53%
- Polish: 88%
- Spanish: 100%

### Misc

* [PR#528](https://github.com/SamR1/FitTrackee/pull/528) - README reworked
* [PR#530](https://github.com/SamR1/FitTrackee/pull/530) - specify AGPLv3 license


Thanks to the contributors:
- @comradekingu
- @gallegonovato
- @jderuiter
- @jmlich
- @xmgz


## Version 0.8.0 (2024/04/21)

**FitTrackee** now lets you associate [equipment](https://docs.fittrackee.org/en/features.html#equipments) with workouts and filter workouts on notes.

### Features and enhancements

* [#259](https://github.com/SamR1/FitTrackee/issues/259) - Feature request: "Equipment" that can be associated with workouts
* [#512](https://github.com/SamR1/FitTrackee/issues/512) - Add ability to filter on notes in Workouts List

### Bugs Fixed

* [#508](https://github.com/SamR1/FitTrackee/issues/508) - Stopped speed threshold unit is missing on sports list
* [3b6fa25](https://github.com/SamR1/FitTrackee/commit/3b6fa25e72375b5790a10761cdf7772ebfc02fbb) - fix workouts table display on small resolutions
* [51758b4](https://github.com/SamR1/FitTrackee/commit/51758b45cd9e343b07409a55618879e4a8c534eb) - fix on filters hiding on small resolutions

### Translations

* [PR#507](https://github.com/SamR1/FitTrackee/pull/507) Translations update (Galician)
* [PR#510](https://github.com/SamR1/FitTrackee/pull/510) Translations update (Spanish)
* [PR#511](https://github.com/SamR1/FitTrackee/pull/511) Translations update (Galician)
* [PR#521](https://github.com/SamR1/FitTrackee/pull/521) Translations update (Spanish)
* [PR#524](https://github.com/SamR1/FitTrackee/pull/524) Translations update (Spanish)

Translation status:
- Basque: 89%
- Dutch: 89%
- English: 100%
- French: 100%
- Galician: 99%
- German: 89%
- Italian: 75%
- Norwegian Bokmål: 53%
- Polish: 89%
- Spanish: 100%

### Misc

* [#502](https://github.com/SamR1/FitTrackee/issues/502) - Remove deprecated commands
* [PR#506](https://github.com/SamR1/FitTrackee/pull/506) - CLI - update database commands


Thanks to the contributors:
- @jat255
- @gallegonovato
- @xmgz

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


## Version 0.7.32 (2024/03/10)

### Bugs Fixed

* [#504](https://github.com/SamR1/FitTrackee/issues/504) - Database migrations fail

### Translations

* [#496](https://github.com/SamR1/FitTrackee/issues/496) Translations update (Dutch)
* [#499](https://github.com/SamR1/FitTrackee/issues/499) Translations update (Polish)

Translation status:
- Basque: 100%
- Dutch: 100%
- English: 100%
- French: 100%
- Galician: 100%
- German: 100%
- Italian: 84%
- Norwegian Bokmål: 60%
- Polish: 100%
- Spanish: 100%


Thanks to the contributors:
- @bjornclauw
- Mariuz


## Version 0.7.31 (2024/02/10)

Basque is now available in FitTrackee interface.  

### Bugs Fixed

* [PR#495](https://github.com/SamR1/FitTrackee/pull/495) - fix menu display when clicking on application name

### Translations

* [#490](https://github.com/SamR1/FitTrackee/issues/490) [Translation Request] EU - Basque 

Translation status:
- Basque: 100%
- Dutch: 99%
- English: 100%
- French: 100%
- Galician: 100%
- German: 100%
- Italian: 84%
- Norwegian Bokmål: 60%
- Polish: 99%
- Spanish: 100%

### Misc

* [PR#494](https://github.com/SamR1/FitTrackee/pull/494) - Update install-python command


Thanks to the contributors:
- @erral


## Version 0.7.30 (2024/02/04)

### Features and enhancements

* [b748459](https://github.com/SamR1/FitTrackee/commit/b7484598258b4891b5699e8e8512deee7977d517) - Update alert message colors on dark mode 

### Bugs Fixed

* [PR#481](https://github.com/SamR1/FitTrackee/pull/481) - Handle keyboard navigation on dropdowns
* [3821e37](https://github.com/SamR1/FitTrackee/commit/3821e370228cf14cc73a9c3f17d47178e17e8842) - Make calendar arrows accessible to keyboard navigation 
* [PR#488](https://github.com/SamR1/FitTrackee/pull/488) - CLI - fix user creation when user already exists with same email
* [PR#489](https://github.com/SamR1/FitTrackee/pull/489) - Handle keyboard navigation on calendar

### Translations

* [PR#482](https://github.com/SamR1/FitTrackee/pull/482) - Translations update (Galician and Spanish)
* [PR#484](https://github.com/SamR1/FitTrackee/pull/484) - Translations update (German)

Translation status:
- Dutch: 99%
- English: 100%
- French: 100%
- Galician: 100%
- German: 100%
- Italian: 84%
- Norwegian Bokmål: 60%
- Polish: 99%
- Spanish: 100%

### Misc

* [aff4d68](https://github.com/SamR1/FitTrackee/commit/aff4d68a913b9aee5a620c4fb7f6049410ad7724) - CI - update actions version 


Thanks to the contributors:
- @gallegonovato
- @qwerty287
- @xmgz


## Version 0.7.29 (2024/01/06)

### Features and enhancements

* [8aa4cff](https://github.com/SamR1/FitTrackee/commit/8aa4cff2bb21c877e382c7498442ccef35935d5f) - Update loader color on dark theme 
* [#478](https://github.com/SamR1/FitTrackee/issues/478) - Make application name clickable to access dashboard

### Bugs Fixed

* [PR#479](https://github.com/SamR1/FitTrackee/pull/479) - Minor fixes on UI

### Translations

* [PR#476](https://github.com/SamR1/FitTrackee/pull/476) - Translations update (Polish)
* [PR#477](https://github.com/SamR1/FitTrackee/pull/477) - Translations update (Dutch)

Translation status:
- Dutch: 100%
- English: 100%
- French: 100%
- Galician: 100%
- German: 100%
- Italian: 84%
- Norwegian Bokmål: 60%
- Polish: 100%
- Spanish: 100%

### Misc

* [PR#475](https://github.com/SamR1/FitTrackee/pull/475) - Build - use poetry-core instead of poetry


Thanks to the contributors:
- @traxys
- Mariuz
- Koen


## Version 0.7.28 (2023/12/23)

### Features and enhancements

* [PR#474](https://github.com/SamR1/FitTrackee/pull/474) - Improve links display

### Bugs Fixed

* [6e215aa](https://github.com/SamR1/FitTrackee/commit/6e215aa52eba28b14f74f3484b23197f5f0ddd4d) - fix background color on dark theme when modal is displayed 

### Translations

* [PR#473](https://github.com/SamR1/FitTrackee/pull/473) - Translations update (Galician, Spanish and German)


Translation status:
- Dutch: 98%
- English: 100%
- French: 100%
- Galician: 100%
- German: 100%
- Italian: 84%
- Norwegian Bokmål: 60%
- Polish: 98%
- Spanish: 100%

Thanks to the contributors:
- @gallegonovato
- @qwerty287
- @xmgz


## Version 0.7.27 (2023/12/20)

### Features and enhancements

* [#113](https://github.com/SamR1/FitTrackee/issues/113) - add a dark mode
* [PR#464](https://github.com/SamR1/FitTrackee/pull/464) - Update user preferences display 
* [PR#471](https://github.com/SamR1/FitTrackee/pull/471) - add new sport: "Cycling (Trekking)"

### Bugs Fixed

* [PR#469](https://github.com/SamR1/FitTrackee/pull/469) - change UI display only on login ou user preferences update 
* [PR#472](https://github.com/SamR1/FitTrackee/pull/472) - fix redirection when resetting password

### Translations

* [PR#468](https://github.com/SamR1/FitTrackee/pull/468) - Translations update (Galician & Spanish)

### Misc

* [#456](https://github.com/SamR1/FitTrackee/issues/456) - Drop PostgreSQL 11 support


Translation status:
- Dutch: 99%
- English: 100%
- French: 100%
- Galician: 99%
- German: 99%
- Italian: 85%
- Norwegian Bokmål: 61%
- Polish: 99%
- Spanish: 99%

Thanks to the contributors:
- @DavidHenryThoreau
- @gallegonovato
- @xmgz

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


## Version 0.7.26 (2023/11/19)

### Bugs Fixed

* [#224](https://github.com/SamR1/FitTrackee/issues/224) - Missing elevation results in incorrect ascent/descent total


### Translations

* [PR#444](https://github.com/SamR1/FitTrackee/pull/444) - Translations update (Norwegian Bokmål)


### Misc

In addition to dependencies update:

* [PR#449](https://github.com/SamR1/FitTrackee/pull/449) - Update vue, tooling and chart library
* [PR#450](https://github.com/SamR1/FitTrackee/pull/450) - Update gpxpy to 1.6.1


Translation status:
- Dutch: 100%
- English: 100%
- French: 100%
- Galician: 100%
- German: 100%
- Italian: 85%
- Norwegian Bokmål: 61%
- Polish: 100%
- Spanish: 100%

Thanks to the contributors:
- @comradekingu


## Version 0.7.25 (2023/10/08)

### Bugs Fixed

* [#441](https://github.com/SamR1/FitTrackee/issues/441) - Errors after upgrade to 0.7.24


## Version 0.7.24 (2023/10/04)

### Bugs Fixed

* [PR#433](https://github.com/SamR1/FitTrackee/pull/433) - Handle encoded password in EMAIL_URL

### Translations

* [PR#427](https://github.com/SamR1/FitTrackee/pull/427) - fix typos and translations + refacto
* [PR#431](https://github.com/SamR1/FitTrackee/pull/431) - Translations update (Galician)

### Misc

* [PR#428](https://github.com/SamR1/FitTrackee/pull/428) - CI - Add PostgreSQL 16
* [2bcff2e](https://github.com/SamR1/FitTrackee/commit/2bcff2edc7308f8ec4a59b30dd482025bf7396e7) - API - update Flask to 3.0+ 
* [PR#436](https://github.com/SamR1/FitTrackee/pull/436) - CI - Add Python 3.12
* [PR#438](https://github.com/SamR1/FitTrackee/pull/438) - CI - update workflows


Translation status:
- Dutch: 100%
- English: 100%
- French: 100%
- Galician: 100%
- German: 100%
- Italian: 85%
- Norwegian Bokmål: 35%
- Polish: 100%
- Spanish: 100%

Thanks to the contributors:
- @xmgz


## Version 0.7.23 (2023/09/14)

### Bugs Fixed

* [PR#421](https://github.com/SamR1/FitTrackee/pull/421) - remove darksky from available weather providers in .env
* [PR#426](https://github.com/SamR1/FitTrackee/pull/426) - Update default tile server (thanks to @astridx)

### Misc

* [PR#422](https://github.com/SamR1/FitTrackee/pull/422) - CI - fix e2e tests with packaged version


## Version 0.7.22 (2023/08/23)

### Bugs Fixed

* [PR#411](https://github.com/SamR1/FitTrackee/pull/411) - Fix various typos
* [PR#416](https://github.com/SamR1/FitTrackee/pull/416) - fix modal navigation and closing


### Translations

* [PR#410](https://github.com/SamR1/FitTrackee/pull/410) - Translations update (German)
* [PR#415](https://github.com/SamR1/FitTrackee/pull/415) - Translations update (Polish)
* [PR#417](https://github.com/SamR1/FitTrackee/pull/417) - Translations update (Polish)
* [PR#418](https://github.com/SamR1/FitTrackee/pull/418) - Translations update (Dutch)

Translation status:
- Dutch: 100%
- English: 100%
- French: 100%
- Galician: 100%
- German: 100%
- Italian: 85%
- Norwegian Bokmål: 35%
- Polish: 100%
- Spanish: 100%

Thanks to the contributors:
- @bjornclauw
- @qwerty287
- Mariusz


## Version 0.7.21 (2023/07/30)

### Bugs Fixed

* [#407](https://github.com/SamR1/FitTrackee/issues/407) - Workout display error when speeds are zero


### Misc

* [PR#409](https://github.com/SamR1/FitTrackee/pull/409) - CI - update actions version


## Version 0.7.20 (2023/07/22)

### Features and enhancements

* [#400](https://github.com/SamR1/FitTrackee/issues/400) - Add new sport: open water swimming


### Bugs Fixed

* [PR#398](https://github.com/SamR1/FitTrackee/pull/398) - Fix language dropdown label
* [#402](https://github.com/SamR1/FitTrackee/issues/402) - handle gpx file without elevation


### Translations

* [PR#399](https://github.com/SamR1/FitTrackee/pull/399) - Translations update (Galician)
* [PR#401](https://github.com/SamR1/FitTrackee/pull/401) - Translations update (Galician and Polish)
* [PR#406](https://github.com/SamR1/FitTrackee/pull/406) - Translations update (Galician and Spanish)


Translation status:
- Dutch: 97%
- English: 100%
- French: 100%
- Galician: 100%
- German: 97%
- Italian: 85%
- Norwegian Bokmål: 35%
- Polish: 56%
- Spanish: 100%

Thanks to the contributors:
- @gallegonovato
- @xmgz
- Mariusz

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


## Version 0.7.19 (2023/07/15)

### Features and enhancements

* [PR#380](https://github.com/SamR1/FitTrackee/pull/380) - Update documentation link
* [#390](https://github.com/SamR1/FitTrackee/issues/390) - Improve UI
* [#391](https://github.com/SamR1/FitTrackee/issues/391) - Add new sport: paragliding


### Bugs Fixed

* [#384](https://github.com/SamR1/FitTrackee/issues/384) - Inconsistent page with between workout with and without GPS data
* [#393](https://github.com/SamR1/FitTrackee/issues/393) - PIL.Image module has no attribute ANTIALIAS


### Translations

* [PR#394](https://github.com/SamR1/FitTrackee/pull/394) - Translations update (Galician)
* [PR#397](https://github.com/SamR1/FitTrackee/pull/397) - Translations update (Spanish)


### Documentation

* [PR#386](https://github.com/SamR1/FitTrackee/pull/386) - Minor fix in CONTRIBUTING.md
* [PR#388](https://github.com/SamR1/FitTrackee/pull/388) - Minor typo in CONTRIBUTING.md


### Misc

* [#395](https://github.com/SamR1/FitTrackee/issues/395) - CI - test a packaged version of FitTrackee
* [cc3fe1c](https://github.com/SamR1/FitTrackee/commit/cc3fe1c82e6fb9f4d5ba94f0b8a9763540bbcab4) CI - update python and postgresql default versions


Translation status:
- Dutch: 97%
- English: 100%
- French: 100%
- Galician: 98%
- German: 97%
- Italian: 85%
- Norwegian Bokmål: 35%
- Polish: 42%
- Spanish: 100%

Thanks to the contributors:
- @dkm
- @gallegonovato
- @xmgz

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


## Version 0.7.18 (2023/06/25)

Polish is available in FitTrackee interface ([partially translated](https://hosted.weblate.org/languages/pl/fittrackee/)).  
Documentation is now translated in French (**note**: documentation translations are not yet available on Weblate).

**Important**: Python 3.7 is no longer supported, the minimum version is now Python 3.8.1.

### Translations

* [#351](https://github.com/SamR1/FitTrackee/issues/351) - [Translation Request] Polish
* [PR#370](https://github.com/SamR1/FitTrackee/pull/370) - Translations update (Dutch, thanks to @bjornclauw)
* [PR#371](https://github.com/SamR1/FitTrackee/pull/371) - Translations update (Polish, thanks to Mariusz on Weblate)
* [PR#375](https://github.com/SamR1/FitTrackee/pull/375) - Translations update (French, thanks to @Thovi98)
* [PR#376](https://github.com/SamR1/FitTrackee/pull/376) - Translations update (German, thanks to @qwerty287)


### Documentation

* [1375986](https://github.com/SamR1/FitTrackee/commit/1375986837321fa356decadcff89bfc2144c345e) - Change documentation theme for Furo
* [#377](https://github.com/SamR1/FitTrackee/issues/377) - Init documentation translation


### Misc

* [#354](https://github.com/SamR1/FitTrackee/issues/354) - Drop support for Python 3.7
* [PR#374](https://github.com/SamR1/FitTrackee/pull/374) - Docker - install fittrackee in a virtualenv 


Translation status:
- Dutch: 100%
- English: 100%
- French: 100%
- Galician: 100%
- German: 100%
- Italian: 87%
- Norwegian Bokmål: 36%
- Polish: 43%
- Spanish: 100%

Thanks to all contributors.


## Version 0.7.17 (2023/06/03)

### Translations

* [PR#366](https://github.com/SamR1/FitTrackee/pull/366), [PR#369](https://github.com/SamR1/FitTrackee/pull/369) - Translations update from Hosted Weblate (Galician, thanks to @xmgz)
* [PR#367](https://github.com/SamR1/FitTrackee/pull/367) - Translations update (Spanish, French)

Translation status:
- Dutch: 99%
- English: 100%
- French: 100%
- Galician: 100%
- German: 99%
- Italian: 87%
- Norwegian Bokmål: 36%
- Polish: 3%
- Spanish: 100%


## Version 0.7.16 (2023/05/29)

### Features and enhancements

* [PR#358](https://github.com/SamR1/FitTrackee/pull/358) - Add user preference for filtering of GPX speed data


### Bugs Fixed

* [#359](https://github.com/SamR1/FitTrackee/issues/359) - Footer overlaps content on user preferences page


### Translations

* [PR#350](https://github.com/SamR1/FitTrackee/pull/350) - Translations update from Hosted Weblate (Galician)
* [PR#352](https://github.com/SamR1/FitTrackee/pull/352) - Translations update from Hosted Weblate (Dutch)
* [PR#356](https://github.com/SamR1/FitTrackee/pull/356) - Init Polish translation files
* [PR#357](https://github.com/SamR1/FitTrackee/pull/357) - Translations update from Hosted Weblate (Polish)
* [PR#365](https://github.com/SamR1/FitTrackee/pull/365) - Translations update from Hosted Weblate (Spanish)

Translation status:
- Dutch: 99%
- English: 100%
- French: 100%
- Galician: 99%
- German: 99%
- Italian: 87%
- Norwegian Bokmål: 36%
- Polish: 3%
- Spanish: 100%

**Note:** Polish is not yet available in FitTrackee interface.

Thanks to the contributors:
- @bjornclauw
- @gallegonovato
- @gnu-ewm
- @jat255
- @xmgz

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


## Version 0.7.15 (2023/04/12)

Among enhancements and fixes, **FitTrackee** is now available in Galician, Spanish and partially in Norwegian Bokmål (see translation status below).

**Note**: **DarkSky** API support is removed, since the service shut down on March 31, 2023.


### Features and enhancements

* [#319](https://github.com/SamR1/FitTrackee/issues/319) - Add cli to create users
* [#329](https://github.com/SamR1/FitTrackee/issues/329) - Make "start elevation axis at zero" sticky
* [#333](https://github.com/SamR1/FitTrackee/issues/333) - Feature request: filter workouts by title
* [#338](https://github.com/SamR1/FitTrackee/issues/338) - Display relevant error message when <time> is missing in GPX file

### Bugs Fixed

* [#328](https://github.com/SamR1/FitTrackee/issues/328) - GPX speed and altitude track has incorrect units on x-axis when imperial
* [b29ed7a](https://github.com/SamR1/FitTrackee/commit/b29ed7a31daaf40b149ed33cdb1ddc0144f56161) - fix privacy policy message display on dashboard

### Translations

* [#250](https://github.com/SamR1/FitTrackee/issues/250) - [Translation Request] Norwegian Bokmål
* [#320](https://github.com/SamR1/FitTrackee/issues/320) - [Translation Request] Spanish
* [#323](https://github.com/SamR1/FitTrackee/issues/323) - [Translation Request] Galician
* [06ba975](https://github.com/SamR1/FitTrackee/commit/06ba975302af222089392c424edf95e91d645437), [bcc568e](https://github.com/SamR1/FitTrackee/commit/bcc568ef59ab99f3c164c6231ab3759fc8a30038), [ea0ac99](https://github.com/SamR1/FitTrackee/commit/ea0ac99bdf1dbe645ada7ddd35b4b94815eca775) - Translations update (German)
* [a458f5f](https://github.com/SamR1/FitTrackee/commit/a458f5f275f51b2f9311de0ed51b0a9b537db94e) - Translations update (Dutch)
* [075aeb9](https://github.com/SamR1/FitTrackee/commit/075aeb95e620c06f3ac324d2534d9c9f6660b596) - Translations update (French)
* [60e164d](https://github.com/SamR1/FitTrackee/commit/60e164d7201fc520cd051f2858860a83783443a7) - Translations update (Italian)

Translation status:
- Dutch: 98%
- English: 100%
- French: 100%
- Galician: 100%
- German: 100%
- Italian: 87%
- Norwegian Bokmål: 35%
- Spanish: 100%

### Misc

* [#318](https://github.com/SamR1/FitTrackee/issues/318) - Remove DarkSky Weather provider


Thanks to the contributors:
- @bjornclauw
- @comradekingu
- @jat255
- @gallegonovato 
- @qwerty287
- @xmgz
- J. Lavoie from Weblate
- mondstern from Weblate


**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


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

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


## Version 0.7.12 (2023/02/16)

### Translations

* [PR#290](https://github.com/SamR1/FitTrackee/pull/290) - Translations update from Hosted Weblate (German, thanks to @qwerty287)

### Misc

* [#294](https://github.com/SamR1/FitTrackee/issues/294) - drop PostgreSQL10 support
* dependencies update


## Version 0.7.11 (2022/12/31)

### Features and enhancements

* [PR#265](https://github.com/SamR1/FitTrackee/pull/265) - Implementing alternative weather API (VisualCrossing.com)  
  **Note**: A new environment variable must be to set to configure the weather data provider: `WEATHER_API_PROVIDER` (see [documentation](https://docs.fittrackee.org/en/installation.html#weather-data))

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

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


## Version 0.7.9 (2022/12/11)

### Features and enhancements

* [#280](https://github.com/SamR1/FitTrackee/issues/280) - New sport: Mountaineering

### Translations

* [PR#278](https://github.com/SamR1/FitTrackee/pull/278) - Translations update from Hosted Weblate (German, thanks to @qwerty287)
* [PR#282](https://github.com/SamR1/FitTrackee/pull/282) - Init italian translation files

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


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

**Note:** `fittrackee_worker` command is disabled, please use existing flask-dramatiq CLI (see [documentation](https://docs.fittrackee.org/en/installation.html#from-pypi))

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

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


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

**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


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
(see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade)).


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
**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


### Version 0.6.10 (2022/07/13)

### Issues Closed

#### Bugs Fixed

* [#210](https://github.com/SamR1/FitTrackee/issues/210) - ERROR - could not download 6 tiles  
  **Note**: for tile server requiring subdomains, see the new environment variable [`STATICMAP_SUBDOMAINS`](https://docs.fittrackee.org/en/installation.html#envvar-STATICMAP_SUBDOMAINS)

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

It is now possible to start FitTrackee without a configured SMTP provider (see [documentation](https://docs.fittrackee.org/en/installation.html#emails)).
It reduces pre-requisites for single-user instances.

To manage users, a new [CLI](https://docs.fittrackee.org/en/cli.html) is available.


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

This version introduces some changes on [user registration](https://docs.fittrackee.org/en/features.html#account-preferences).  
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
**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


## Version 0.5.7 (2022/02/13)

This release contains several fixes including security fixes.  
Thanks to @DanielSiersleben for the report.

And from now on, admin account is not created on application initialization.  
A new command is added to set administration rights on the account created after registration 
(see [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))

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
**Note:** This release contains database migration (see upgrade instructions in [documentation](https://docs.fittrackee.org/en/installation.html#upgrade))


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
⚠️ Warning: please read [installation documentation](https://docs.fittrackee.org/en/installation.html), some environment variables and files have been renamed.
- It's now possible to change the tile provider for maps. The default tile server is now **OpenStreetMap**'s standard tile layer (replacing **ThunderForest Outdoors**), 
see [Map tile server in documentation](https://docs.fittrackee.org/en/installation.html#map-tile-server).

### Issues Closed

#### New Features

* [#54](https://github.com/SamR1/Fittrackee/issues/54) - Tile server can be changed
* [#53](https://github.com/SamR1/Fittrackee/issues/53) - Simplify FitTrackee installation

In this release 2 issues were closed.


## Version 0.3.0 - Administration (2020/07/15)

This version introduces some major changes:
- FitTrackee administration is now available (see [documentation](https://docs.fittrackee.org/en/features.html#administration))  
⚠️ Warning: some application parameters move from environment variables to database (see [installation](https://docs.fittrackee.org/en/installation.html#environment-variables)).
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
   - Mountain Biking
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
   - farthest distance
   - longest duration
   - maximum speed
- Activities list and search


**Notes:**
- only activity owner can see his activity
- no administration for now

➡️ more informations: see [documentation](https://docs.fittrackee.org/) and [current issues](https://github.com/SamR1/FitTrackee/issues)


### Issues Closed

#### New Features

* [#11](https://github.com/SamR1/FitTrackee/issues/11) - Timezone support
* [#10](https://github.com/SamR1/FitTrackee/issues/10) - Add a note to an activity
* [#9](https://github.com/SamR1/FitTrackee/issues/9) - User statistics on dashboard
* [#8](https://github.com/SamR1/FitTrackee/issues/8) - Add weather to activities
* [#3](https://github.com/SamR1/FitTrackee/issues/3) - Search filter for activities
* [#2](https://github.com/SamR1/FitTrackee/issues/2) - Calendar to view activities

In this release 6 issues were closed.
