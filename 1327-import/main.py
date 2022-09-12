import json
import logging
import os

import django
from django.db import IntegrityError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myhpi.settings")
django.setup()
from django.contrib.auth.models import Group, User

logger = logging.getLogger("1327_import")


def main():

    logger.setLevel(level=logging.INFO)
    logger.addHandler(logging.StreamHandler())
    logger.info("Welcome to the 1327 importer!")
    logger.info("Please provide the absolute path to the database dump of 1327 to import.")
    json_path = input()
    logger.info("Loading file. This may take a while.")
    with open(json_path) as dump_file:
        data = json.loads(dump_file.read())

    # Groups
    logger.info("Creating groups")
    group_data = list(filter(lambda entry: entry["model"] == "auth.group", data))
    group_1327_pk_dict = {}
    logger.warning("Group permission import is currently not supported.")
    for group in group_data:
        group_name = group["fields"]["name"]
        group_1327_pk = group["pk"]
        group = Group.objects.create(name=group_name)
        group_1327_pk_dict[group_1327_pk] = group

    # Users
    logger.info("Creating users")
    user_data = list(filter(lambda entry: entry["model"] == "user_management.userprofile", data))
    user_1327_pk_dict = {}
    total_user_count = len(user_data)
    user_import_count = 0
    for user in user_data:
        user_1327_pk = user["pk"]
        fields = user["fields"]
        try:
            username=fields["username"]
            first_name = fields["first_name"]
            last_name = fields["last_name"]

            # fill in some data to fill non-null columns
            if username and not first_name and "." in username:
                first_name = username.split(".")[0].capitalize()
            if username and not last_name and "." in username:
                last_name = username.split(".")[1].capitalize()

            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=username,
                is_superuser=False,
                email=fields["email"],
                password="",
            )
            user_1327_pk_dict[user_1327_pk] = user
            for group_pk in fields["groups"]:
                group_1327_pk_dict[group_pk].user_set.add(user)

            user_import_count += 1
        except IntegrityError:
            logger.warning(f"Could not create user {fields['username']}")
    logger.info(f"Imported {user_import_count} of {total_user_count} users")


if __name__ == "__main__":
    main()