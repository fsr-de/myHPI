# myHPI

This tool is used to manage the student representative website at https://myhpi.de (not live yet). It is a CMS based on Wagtail/Django and adds several functionalities like polls.

## Development setup

To set up a development version on your local machine, you need to execute the following steps:
1. Check out repository and cd to it
2. Set up a virtualenv for the project with Python >=3.8 and activate it
3. Install poetry (if not already installed): `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -`
4. Install dependencies with `poetry install`
5. Install bootstrap with `python install-bootstrap.py`
6. Create env file by copying the `.env.example` file to `.env`, e.g. `cp .env.example .env` (Notice that for some functionality like OIDC some settings must be changed)
7. Migrate the database with `python manage.py migrate`
8. Compile translations with `python manage.py compilemessages` (does not work on Windows, recommended to skip this step or see [docs](https://docs.djangoproject.com/en/4.0/topics/i18n/translation/#gettext-on-windows))
9. Create a local superuser with `python manage.py createsuperuser`
10. Start the development server with `python manage.py runserver`
11. Open your web browser, visit `http://localhost:8000/admin` and log in with your user from step 8

### Tests

Test the code with `pytest`.

### Code style

We recommend installing a pre-commit hook with `pre-commit install`. That will (look at `.pre-commit-config.yaml`) before every commit

* run `autoflake` with a couple of flags to remove unused imports,
* run `isort .` to sort imports,
* run `black .` to format the code. You can also check out the [IDE integration](https://github.com/psf/black#editor-integration)

If you want to do that manually, run `pre-commit run --all-files`. Next to that, we also run `pylint myhpi` to check for semantic issues in the code.
