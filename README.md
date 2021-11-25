# myHPI

This tool is used to manage the student representative website at https://myhpi.de (not live yet). It is a CMS based on Wagtail/Django and adds several functionalities like polls.

## Development setup

To set up a development version on your local machine, you need to execute the following steps:
1. Check out repository and cd to it
2. Set up a virtualenv for the project with Python >=3.8 and activate it
3. Install poetry (if not already installed): `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -`
4. Install dependencies with `poetry install`
5. Create env file by copying the `.env.example file to `.env`, e.g. `cp .env.example .env`
6. Migrate the database with `python manage.py migrate`
7. Compile translations with `python manage.py compilemessages`
8. Create a local superuser with `python manage.py createsuperuser`
9. Start the development server with `python manage.py runserver`
10. Open your web browser, visit `http://localhost:8000` and log in with your user from step 9

### Tests

Test the code with `pytest`.

### Code style

We recommend installing a pre-commit hook with `pre-commit install`. That will (look at `.pre-commit-config.yaml`) before every commit

* run `autoflake` with a couple of flags to remove unused imports,
* run `isort .` to sort imports,
* run `black .` to format the code. You can also check out the [IDE integration](https://github.com/psf/black#editor-integration)

If you want to do that manually, run `pre-commit run --all-files`. Next to that, we also run `pylint ephios` to check for semantic issues in the code.
