# Contributing

Thank you for considering contributing to this open source project! Please take a moment
to review this document in order to make the contribution process easy and effective for
everyone involved.

Following these guidelines helps to communicate that you respect the time of the
developers managing and developing this open source project. In return, we will
reciprocate that respect by addressing your issue, assessing changes, and helping you
finalize your pull requests.

As for everything else in the project, the contributions are governed by our
[Code of Conduct](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/docs/CODE_OF_CONDUCT.md).



## Issues

Issues should be used to report problems, request new features, or to discuss potential
changes before a pull request is created. When you create a new issue, a template will
be loaded that will guide you through collecting and providing the information we need.

If you find an issue that addresses the problem you're having, please add your own
reproduction information to the existing issue rather than creating a new one.

### Security issues

Review our
[Security Policy](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/docs/SECURITY.md).
Please **do not** use public issues to report security vulnerabilities.

### Bug reports

A bug is a *demonstrable problem* that is caused by the code in the repository. Good bug
reports are extremely helpful - thank you!

Guidelines for bug reports:

1. **Use the GitHub issue search** - check if the issue has already been reported

2. **Check if the issue has been fixed** - try to reproduce it using the latest `master`
branch in the repository

3. **Isolate the problem** - ideally create a reduced test case

A good bug report shouldn't leave others needing to chase you up for more information.
Please try to be as detailed as possible in your report. What is your environment? What
steps will reproduce the issue? What OS experiences the problem? What would you expect
to be the outcome? All these details will help people to fix any potential bugs.

### Feature requests

Feature requests are welcome. But take a moment to find out whether your idea fits with
the scope and aims of the project. It's up to *you* to make a strong case to convince
the project's developers of the merits of this feature. Please provide as much detail
and context as possible.



## Pull requests (PR)

Good pull requests - patches, improvements, new features - are a fantastic help. They
should remain focused in scope and avoid containing unrelated commits. In general, pull
requests should:

* Address a single concern in the least number of changed lines as possible

* Add unit or integration tests for fixed or changed functionality (if a test suite
already exists)

* Include documentation (if appropriate)

* Be accompanied by a complete pull request template (loaded automatically when a PR is
created)

**Please ask first** before embarking on any significant pull request (e.g., new
features that would require breaking changes), otherwise you risk spending a lot of time
working on something that the project's developers might not want to merge into the
project. It's best to open an issue to discuss your proposal first.

`NOTE:` by submitting a PR, you agree to license your work under the same license as
that used by the project.

### For new Contributors

If you never created a pull request before, here's a brief guide:

1. [Fork](http://help.github.com/fork-a-repo/) the project, clone your fork, and
configure the remotes:
    ```Shell
    $ # Clone your fork of the repo into the current directory.
    $ git clone https://github.com/<your-username>/<repo-name>
    $ # Navigate to the newly cloned directory.
    $ cd <repo-name>
    $ # Assign the original repo to a remote called "upstream".
    $ git remote add upstream https://github.com/ClaudiuGeorgiu/<repo-name>
    ```

2. If you cloned a while ago, get the latest changes from upstream:
    ```Shell
    $ git checkout master
    $ git pull upstream master
    ```

3. Create a new topic branch (off the main project development branch) to contain your
feature, change, or fix:
    ```Shell
    $ git checkout -b <topic-branch-name>
    ```

4. Now the fun part: implement your changes.

5. If you added or changed a feature, make sure to document it accordingly.

6. Follow any formatting and testing guidelines specific to this repository.

7. Commit changes and push your topic branch up to your fork:
    ```Shell
    $ git add <changed-files>
    $ git commit -m "<descriptive-commit-message>"
    $ git push origin <topic-branch-name>
    ```

8. [Open a pull request](https://help.github.com/articles/using-pull-requests/) in our
repository and follow the PR template so that we can efficiently review the changes.
