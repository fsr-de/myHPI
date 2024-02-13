# myHPI

[![tests](https://github.com/fsr-de/myHPI/actions/workflows/tests.yml/badge.svg)](https://github.com/fsr-de/myHPI/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/fsr-de/myHPI/badge.svg?branch=main)](https://coveralls.io/github/fsr-de/myHPI?branch=main)

This tool is used to manage the student representative website at https://myhpi.de. It is a CMS based on Wagtail/Django and adds several functionalities like polls.

## Development setup

For a quick start, use the [dev container](https://containers.dev/), e.g. by installing the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) in Visual Studio Code or using the [built-in feature in JetBrains IDEs](https://jetbrains.com/help/idea/connect-to-devcontainer.html). This automatically installs all dependencies in a container. After starting the container, setup your local data by following the Manual Setup from step 9 (creating a superuser).

### Manual setup

To set up a development version on your local machine, you need to execute the following steps:

1. Check out repository and cd to it
1. Set up a virtualenv for the project with Python >=3.11 and activate it (e.g., `python3 -m venv venv` and `source venv/bin/activate`)
1. Install poetry (if not already installed): `curl -sSL https://install.python-poetry.org/ | python -`
1. Install dependencies with `poetry install`
1. Install bootstrap with `python tools/install_bootstrap.py`
1. Create env file by copying the `.env.example` file to `.env`, e.g. `cp .env.example .env` (Notice that for some functionality like OIDC some settings must be changed)
1. Migrate the database with `python manage.py migrate`
1. Compile translations with `python manage.py compilemessages` (does not work on Windows, recommended to skip this step or see [docs](https://docs.djangoproject.com/en/4.0/topics/i18n/translation/#gettext-on-windows))
1. Create a local superuser with `python manage.py createsuperuser`
1. Start the development server with `python manage.py runserver`
1. Optionally: Create test data with `python tools/create_test_data.py`
1. Open your web browser, visit `http://localhost:8000/admin` and log in with the user you just created

### Tests

Test the code with `python manage.py test myhpi.tests`.

### Code style

We recommend installing a pre-commit hook with `pre-commit install`. That will (look at `.pre-commit-config.yaml`) before every commit

-   run `autoflake` with a couple of flags to remove unused imports,
-   run `isort .` to sort imports,
-   run `black .` to format the code. You can also check out the [IDE integration](https://github.com/psf/black#editor-integration)

If you want to do that manually, run `pre-commit run --all-files`. Next to that, we also run `pylint myhpi` to check for semantic issues in the code.

## Tips

- To create translations, run `python manage.py makemessages -l de -i venv`.

### Reset database

1. Delete `db.sqlite3`
2. Conduct development setup steps 7+
