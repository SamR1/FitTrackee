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
- tests,
- documentation (source and build).

Continuous integration workflows run on **Github Actions** platform (on **push** and **pull requests**).


### How to install FitTrackee

see [Installations instructions](https://samr1.github.io/FitTrackee/installation.html)

### Pull Requests

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

* If needed, add or update tests.

* If needed, update documentation (no need to build documentation, it will be done when releasing).

* If updated code contains client-side changes, you can generate a build, in a **separate commit** to ease code review (or to easily drop it in case of conflicts when updating your branch).
  ```shell
  $ make build-client
  ```

* Create your pull request to merge on `dev` branch.

* Ensure the pull requests description clearly describes the problem and solution. Include the relevant issue number if applicable.

* If needed, [update your branch](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/keeping-your-pull-request-in-sync-with-the-base-branch). 


Thanks.