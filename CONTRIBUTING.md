# Contributing to FitTrackee

First off, thank you for your interest in contributing!

## Report issues, ask for features

* If a bug is a **security vulnerability**, please refer to [security policy](https://github.com/SamR1/FitTrackee/blob/master/SECURITY.md).

* Ensure an issue was not **already opened** by searching on **GitHub** under [Issues](https://github.com/SamR1/FitTrackee/issues). 

* If not, [open a new one](https://github.com/SamR1/FitTrackee/issues/new) with a descriptive title and provide a description.


## Contributing Code

### Project repository

The **GitHub** repository contains:
- source code (note that the repository also includes client build),
- translations,
- tests,
- documentation (source, translations and build).

Continuous integration workflows run on **Github Actions** platform (on **push** and **pull requests**).

For now, releases do not follow [semantic versioning](https://semver.org). Any version may contain backward-incompatible changes.

### Translations

The available languages are:  
[![Translation status](https://hosted.weblate.org/widgets/fittrackee/-/multi-auto.svg)](https://hosted.weblate.org/engage/fittrackee/)

Application translations files are located:
- on API side (emails): `fittrackee/emails/translations/` (implemented with [Babel](https://babel.pocoo.org/en/latest/))
- on client side: `fittrackee_client/src/locales` (implemented with [Vue I18n](https://vue-i18n.intlify.dev/))

Translations can be updated through [Weblate](https://hosted.weblate.org/engage/fittrackee/).  

Documentation translations are located in following directory: `docsrc/locales`. 
For now only English and French are available and translations files are not yet on Weblate.

### How to install FitTrackee

see [Installations instructions](https://samr1.github.io/FitTrackee/en/installation.html)

### Pull Requests

**Note**: Before starting, please open an issue to discuss implementation if the feature requires major changes or involves the addition of a new sport or language.

Please make your changes from the development branch (`dev`).

* Fork the repository (see [GitHub instructions](https://docs.github.com/en/get-started/quickstart/contributing-to-projects))

* Implement your feature.

* If your changes need a database migration:
  * You can generate one after updating models with the following command:
    ```shell
    $ make migrate-db
    ```
  * For data migration, an empty migration can be created with this following command:
    ```shell
    $ make revision MIGRATION_MESSAGE="<MIGRATION_MESSAGE>"
    ```
  * Rename the migration, prefixing with the next number.
  * To apply database changes:
    ```shell
    $ make upgrade-db
    ```
  * Check the downgrade migration.
  
* Run checks (lint, type check and unit tests).
  ```shell
  $ make check-all
  ```
  There are some end-to-end tests, to run them (needs a running application):
  ```shell
  $ make test-e2e
  ```

* If needed, update translations (at least add English strings).
   * On client side, update files in `fittrackee_client/src/locales` folder.  
   * On API side (emails), to extract new strings into `messages.pot`:
     ```shell
     $ make babel-extract
     ```
     To add new strings in translations files (`fittrackee/emails/translations/<LANG>/LC_MESSAGES/messages.po`):
     ```shell
     $ make babel-update
     ```
     After updating strings in `messages.po`, compile the translations:
     ```shell
     $ make babel-compile
     ```

* If needed, add or update tests.

* If needed, update documentation (no need to build documentation, it will be done when releasing).

* If updated code contains client-side changes, you can generate javascript assets to check **FitTrackee** whithout starting client dev server:
  ```shell
  $ make build-client
  ```
  No need to commit these files, dist files will be generated before merging or when releasing.

* Create your pull request to merge on `dev` branch.

* Ensure the pull requests description clearly describes the problem and solution. Include the relevant issue number if applicable.

* Check that all tests have been successfully passed.

* If needed, [update your branch](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/keeping-your-pull-request-in-sync-with-the-base-branch). 


Thanks.
