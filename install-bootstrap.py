import logging
import os
import shutil
import zipfile

import requests

TEMP_DIRECTORY = "tmp"
ZIP_FILENAME = "bootstrap.zip"
logger = logging.getLogger("myhpi_install_bootstrap")


def ensure_correct_directory():
    with open("pyproject.toml") as toml_file:
        return "myHPI" in toml_file.readlines()[1]


def download_zip():
    bootstrap_zip_url = "https://github.com/twbs/bootstrap/archive/refs/heads/main.zip"
    r = requests.get(bootstrap_zip_url, allow_redirects=True)
    try:
        os.mkdir(TEMP_DIRECTORY)
        logger.info("Created temporary directory")
    except FileExistsError:
        logger.info("Temporary directory already exists")
    logger.info("Downloading zip")
    with open(os.path.join(TEMP_DIRECTORY, ZIP_FILENAME), "wb") as file:
        file.write(r.content)
        return os.path.abspath(os.path.join(TEMP_DIRECTORY, ZIP_FILENAME))


def extract_zip(file_path):
    if not file_path:
        logger.error("No zip file provided")
        exit(1)
    logger.info("Extracting zip")
    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall("tmp")
    logger.info("Removing zip")
    os.remove(file_path)


def move_files():
    source_dir = os.path.join(TEMP_DIRECTORY, "bootstrap-main", "scss")
    target_dir = os.path.join("myhpi", "static", "scss")
    logger.info("Moving scss directory")
    shutil.move(source_dir, target_dir)
    logger.info("Renaming scss directory")
    os.rename(
        os.path.join("myhpi", "static", "scss", "scss"),
        os.path.join("myhpi", "static", "scss", "bootstrap"),
    )

    logger.info("Moving js files")
    min_js_path = os.path.join(TEMP_DIRECTORY, "bootstrap-main", "dist", "js", "bootstrap.bundle.min.js")
    min_js_map_path = os.path.join(TEMP_DIRECTORY, "bootstrap-main", "dist", "js", "bootstrap.bundle.min.js.map")
    shutil.move(min_js_path, os.path.join("myhpi", "static", "js"))
    shutil.move(min_js_map_path, os.path.join("myhpi", "static", "js"))


def remove_temporary_directory():
    logger.info("Removing temporary directory")
    shutil.rmtree(TEMP_DIRECTORY)


def install_bootstrap():
    logger.setLevel(level=logging.INFO)
    logger.addHandler(logging.StreamHandler())
    correct_dir = ensure_correct_directory()
    if not correct_dir:
        logger.error(
            "The program was not executed in the correct directory!\n\
        Ensure that it is run in the top directory of the repository."
        )
        exit(1)

    file_path = download_zip()
    extract_zip(file_path)
    move_files()
    remove_temporary_directory()
    print("Installed bootstrap")


if __name__ == "__main__":
    install_bootstrap()
