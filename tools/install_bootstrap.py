import argparse
import logging
import os
import shutil
import zipfile

import requests

TEMP_DIRECTORY = "tmp"
ZIP_FILENAME = "bootstrap.zip"
VERSION = "5.3.3"
logger = logging.getLogger("myhpi_install_bootstrap")


def ensure_correct_directory():
    if os.getcwd().endswith("tools"):
        os.chdir("..")
    try:
        with open("pyproject.toml") as toml_file:
            return "myHPI" in toml_file.readlines()[1]
    except FileNotFoundError:
        return False


def download_zip():
    bootstrap_zip_url = f"https://github.com/twbs/bootstrap/archive/refs/tags/v{VERSION}.zip"
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
    source_dir = os.path.join(TEMP_DIRECTORY, f"bootstrap-{VERSION}", "scss")
    target_dir = os.path.join("myhpi", "static", "scss")
    logger.info("Moving scss directory")
    shutil.move(source_dir, target_dir)
    logger.info("Renaming scss directory")
    os.rename(
        os.path.join("myhpi", "static", "scss", "scss"),
        os.path.join("myhpi", "static", "scss", "bootstrap"),
    )

    logger.info("Moving js files")
    min_js_path = os.path.join(
        TEMP_DIRECTORY, f"bootstrap-{VERSION}", "dist", "js", "bootstrap.bundle.min.js"
    )
    min_js_map_path = os.path.join(
        TEMP_DIRECTORY, f"bootstrap-{VERSION}", "dist", "js", "bootstrap.bundle.min.js.map"
    )
    shutil.move(min_js_path, os.path.join("myhpi", "static", "js"))
    shutil.move(min_js_map_path, os.path.join("myhpi", "static", "js"))


def remove_temporary_directory():
    logger.info("Removing temporary directory")
    shutil.rmtree(TEMP_DIRECTORY)


def remove_current_bootstrap():
    logger.info("Removing current bootstrap installation")
    bootstrap_scss_directory = os.path.join("myhpi", "static", "scss", "bootstrap")
    if os.path.exists(bootstrap_scss_directory):
        shutil.rmtree(bootstrap_scss_directory)
    bootstrap_min_js_path = os.path.join("myhpi", "static", "js", "bootstrap.bundle.min.js")
    if os.path.exists(bootstrap_min_js_path):
        os.remove(bootstrap_min_js_path)
    bootstrap_min_js_map_path = os.path.join("myhpi", "static", "js", "bootstrap.bundle.min.js.map")
    if os.path.exists(bootstrap_min_js_map_path):
        os.remove(bootstrap_min_js_map_path)


def is_bootstrap_installed():
    return (
        os.path.exists(os.path.join("myhpi", "static", "scss", "bootstrap"))
        and os.path.exists(os.path.join("myhpi", "static", "js", "bootstrap.bundle.min.js"))
        and os.path.exists(os.path.join("myhpi", "static", "js", "bootstrap.bundle.min.js.map"))
    )


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [-u]", description="Install bootstrap for myHPI."
    )
    parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="Update (Remove and reinstall) current bootstrap installation.",
    )
    parser.add_argument(
        "-r", "--remove", action="store_true", help="Remove current bootstrap installation."
    )
    parser.add_argument(
        "--is-installed", action="store_true", help="Check if bootstrap is installed."
    )
    return parser


def install_bootstrap():
    logger.setLevel(level=logging.INFO)
    logger.addHandler(logging.StreamHandler())
    parser = init_argparse()
    args = parser.parse_args()
    correct_dir = ensure_correct_directory()
    if not correct_dir:
        logger.error(
            "The program was not executed in the correct directory!\n\
        Ensure that it is run in the top directory of the repository."
        )
        exit(1)
    if args.is_installed:
        is_installed = is_bootstrap_installed()
        exit(0 if is_installed else 1)
    if args.update or args.remove:
        remove_current_bootstrap()
        if args.remove:
            exit(0)
    file_path = download_zip()
    extract_zip(file_path)
    move_files()
    remove_temporary_directory()
    print("Installed bootstrap")


if __name__ == "__main__":
    install_bootstrap()
