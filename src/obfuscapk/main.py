#!/usr/bin/env python
# coding: utf-8

import logging
import os
import shutil
from typing import List

from . import util
from .obfuscation import Obfuscation
from .obfuscator_manager import ObfuscatorManager
from .tool import Apktool, Jarsigner, Zipalign

if 'LOG_LEVEL' in os.environ:
    log_level = os.environ['LOG_LEVEL']
else:
    log_level = logging.ERROR

# Logging configuration.
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s> [%(levelname)s][%(name)s][%(funcName)s()] %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S', level=log_level)


def check_external_tool_dependencies():
    """
    Make sure all the external needed tools are available and ready to be used.
    """
    apktool: Apktool = Apktool()
    jarsigner: Jarsigner = Jarsigner()
    zipalign: Zipalign = Zipalign()

    external_tool_paths = [apktool.apktool_path, jarsigner.jarsigner_path, zipalign.zipalign_path]

    # APKTOOL_PATH, JARSIGNER_PATH and ZIPALIGN_PATH environment variables can be used to specify the
    # location of the external tools (make sure they have the execute permission).
    for external_tool_path in external_tool_paths:
        if shutil.which(external_tool_path) is None:
            raise RuntimeError('Something is wrong with executable "{0}"'.format(external_tool_path))


def perform_obfuscation(input_apk_path: str, obfuscator_list: List[str], working_dir_path: str = None,
                        obfuscated_apk_path: str = None, interactive: bool = False, ignore_libs: bool = False,
                        virus_total_api_key: List[str] = None):
    """
    Apply the obfuscation techniques to an input application and generate an obfuscated apk file.

    :param input_apk_path: The path to the input application file to obfuscate.
    :param obfuscator_list: A list containing the names of the obfuscation techniques to apply.
    :param working_dir_path: The working directory where to store the intermediate files. By default a directory
                             will be created in the same directory as the input application. If the specified
                             directory doesn't exist, it will be created.
    :param obfuscated_apk_path: The path where to save the obfuscated apk file. By default the file will be saved
                                in the working directory.
    :param interactive: If True, show a progress bar with the obfuscation progress.
    :param ignore_libs: If True, exclude known third party libraries from the obfuscation operations.
    :param virus_total_api_key: A list containing Virus Total API keys, needed only when using Virus Total obfuscator.
    """

    check_external_tool_dependencies()

    if not os.path.isfile(input_apk_path):
        logger.critical('Unable to find application file "{0}"'.format(input_apk_path))
        raise FileNotFoundError('Unable to find application file "{0}"'.format(input_apk_path))

    obfuscation = Obfuscation(input_apk_path, working_dir_path, obfuscated_apk_path, interactive=interactive,
                              ignore_libs=ignore_libs, virus_total_api_key=virus_total_api_key)

    manager = ObfuscatorManager()
    obfuscator_name_to_obfuscator_object = {ob.name: ob.plugin_object for ob in manager.get_all_obfuscators()}
    obfuscator_name_to_function = {ob.name: ob.plugin_object.obfuscate for ob in manager.get_all_obfuscators()}

    obfuscator_progress = util.show_list_progress(obfuscator_list, interactive=interactive, unit='obfuscator',
                                                  description='Running obfuscators')

    # Check how many obfuscators in list will add new fields/methods.
    for obfuscator_name in obfuscator_list:
        if obfuscator_name_to_obfuscator_object[obfuscator_name].is_adding_fields:
            obfuscation.obfuscators_adding_fields += 1
        if obfuscator_name_to_obfuscator_object[obfuscator_name].is_adding_methods:
            obfuscation.obfuscators_adding_methods += 1

    for obfuscator_name in obfuscator_progress:
        if obfuscator_name in obfuscator_name_to_function:
            try:
                if interactive:
                    obfuscator_progress.set_description('Running obfuscators ({0})'.format(obfuscator_name))
                (obfuscator_name_to_function[obfuscator_name])(obfuscation)
            except Exception as e:
                logger.critical('Error during obfuscation: {0}'.format(e), exc_info=True)
                raise
