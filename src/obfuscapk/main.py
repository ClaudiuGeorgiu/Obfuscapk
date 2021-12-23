#!/usr/bin/env python3

import logging
import os
from typing import List

from obfuscapk import util
from obfuscapk.obfuscation import Obfuscation
from obfuscapk.obfuscator_manager import ObfuscatorManager
from obfuscapk.tool import Apktool, Zipalign, ApkSigner
from obfuscapk.toolbundledecompiler import BundleDecompiler

if "LOG_LEVEL" in os.environ:
    log_level = os.environ["LOG_LEVEL"]
else:
    # By default log only the error messages.
    log_level = logging.ERROR

# For the plugin system log only the error messages and ignore the log level set by
# the user.
logging.getLogger("yapsy").level = logging.ERROR

# Logging configuration.
logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s> [%(levelname)s][%(name)s][%(funcName)s()] %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
    level=log_level,
)


def check_external_tool_dependencies():
    """
    Make sure all the external needed tools are available and ready to be used.
    """
    # APKTOOL_PATH, APKSIGNER_PATH and ZIPALIGN_PATH environment variables can be
    # used to specify the location of the external tools (make sure they have the
    # execute permission). If there is a problem with any of the executables below,
    # an exception will be thrown by the corresponding constructor.
    logger.debug("Checking external tool dependencies")
    Apktool()
    BundleDecompiler()
    ApkSigner()
    Zipalign()


def perform_obfuscation(
    input_apk_path: str,
    obfuscator_list: List[str],
    working_dir_path: str = None,
    obfuscated_apk_path: str = None,
    ignore_libs: bool = False,
    interactive: bool = False,
    virus_total_api_key: str = None,
    keystore_file: str = None,
    keystore_password: str = None,
    key_alias: str = None,
    key_password: str = None,
    ignore_packages_file: str = None,
    use_aapt2: bool = False,
):
    """
    Apply the obfuscation techniques to an input application and generate an obfuscated
    apk file.

    :param input_apk_path: The path to the input application file to obfuscate.
    :param obfuscator_list: A list containing the names of the obfuscation techniques
                            to apply.
    :param working_dir_path: The working directory where to store the intermediate
                             files. By default a directory will be created in the same
                             directory as the input application. If the specified
                             directory doesn't exist, it will be created.
    :param obfuscated_apk_path: The path where to save the obfuscated apk file. By
                                default the file will be saved in the working directory.
    :param ignore_libs: If True, exclude known third party libraries from the
                        obfuscation operations.
    :param interactive: If True, show a progress bar with the obfuscation progress.
    :param virus_total_api_key: A string containing Virus Total API key, needed only
                                when using Virus Total obfuscator.
    :param keystore_file: The path to a custom keystore file to be used for signing the
                          resulting obfuscated application. If not provided, a default
                          keystore bundled with this tool will be used instead.
    :param keystore_password: The password of the custom keystore used for signing the
                              resulting obfuscated application (needed only when
                              specifying a custom keystore file).
    :param key_alias: The key alias for signing the resulting obfuscated application
                      (needed only when specifying a custom keystore file).
    :param key_password: The key password for signing the resulting obfuscated
                         application (needed only when specifying a custom keystore
                         file).
    :param ignore_packages_file: The file containing the package names to be ignored
                                 during the obfuscation (one package name per line).
    :param use_aapt2 If True, use aapt2 for rebuild app
    """

    check_external_tool_dependencies()

    if not os.path.isfile(input_apk_path):
        logger.critical('Unable to find application file "{0}"'.format(input_apk_path))
        raise FileNotFoundError(
            'Unable to find application file "{0}"'.format(input_apk_path)
        )

    obfuscation = Obfuscation(
        input_apk_path,
        working_dir_path,
        obfuscated_apk_path,
        ignore_libs,
        interactive,
        virus_total_api_key,
        keystore_file,
        keystore_password,
        key_alias,
        key_password,
        ignore_packages_file,
        use_aapt2,
    )

    manager = ObfuscatorManager()
    obfuscator_name_to_obfuscator_object = {
        ob.name: ob.plugin_object for ob in manager.get_all_obfuscators()
    }
    obfuscator_name_to_function = {
        ob.name: ob.plugin_object.obfuscate for ob in manager.get_all_obfuscators()
    }
    valid_obfuscators = manager.get_obfuscators_names()

    # Check how many obfuscators in list will add new fields/methods.
    for obfuscator_name in obfuscator_list:
        # Make sure all the provided obfuscator names are valid.
        if obfuscator_name not in valid_obfuscators:
            raise ValueError(
                'There is no obfuscator named "{0}"'.format(obfuscator_name)
            )
        if obfuscator_name_to_obfuscator_object[obfuscator_name].is_adding_fields:
            obfuscation.obfuscators_adding_fields += 1
        if obfuscator_name_to_obfuscator_object[obfuscator_name].is_adding_methods:
            obfuscation.obfuscators_adding_methods += 1

    obfuscator_progress = util.show_list_progress(
        obfuscator_list,
        interactive=interactive,
        unit="obfuscator",
        description="Running obfuscators",
    )

    for obfuscator_name in obfuscator_progress:
        try:
            if interactive:
                obfuscator_progress.set_description(
                    "Running obfuscators ({0})".format(obfuscator_name)
                )
            (obfuscator_name_to_function[obfuscator_name])(obfuscation)
        except Exception as e:
            logger.critical("Error during obfuscation: {0}".format(e), exc_info=True)
            raise
