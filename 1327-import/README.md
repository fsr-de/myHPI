# 1327 import

This tool can import some data from a 1327 database dump.
To create the dump use the command `python manage.py dumpdata --exclude sessions.session --indent 2 > ~/db.json` on your 1327 instance.

Then run the import tool on your myhpi instance simply with `python 1327-import/main.py` from this repository's directory.

Currently the import supports:
- Groups (only names)
- Users (name, email, username)
- User membership in groups
