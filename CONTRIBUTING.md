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

Continuous integration pipeline runs on **Gitlab CI**.

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
  
* Run checks (lint, typecheck and tests).
  ```shell
  $ make check-all
  ```
  There are some end-to-end tests, to run them:
  ```shell
  $ make test-e2e
  ```
  Note: For now, pull requests from forks don't trigger pipelines on GitLab CI (see [current issue](https://gitlab.com/gitlab-org/gitlab/-/issues/5667)).  
  So make sure that checks don't return errors locally. 

* If needed, add or update tests.

* If needed, update documentation.

* If code contains client changes, you can generate a build, in a **separate commit** to ease code review.
  ```shell
  $ make build-client
  ```

* Create your pull request to merge on `dev` branch.

* Ensure the pull requests description clearly describes the problem and solution. Include the relevant issue number if applicable.


Thanks.