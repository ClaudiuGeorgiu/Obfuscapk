#!/usr/bin/env python3

import logging
import os
import secrets
import string
from typing import List, Union

from obfuscapk import util
from obfuscapk.tool import Apktool, ApkSigner, Zipalign
from obfuscapk.toolbundledecompiler import BundleDecompiler, AABSigner


class Obfuscation(object):
    """
    This class holds the details and the internal state of an obfuscation operation.
    When obfuscating a new application, an instance of this class has to be instantiated
    and passed to all the obfuscators (in sequence).
    """

    def __init__(
        self,
        apk_path: str,
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
        self.logger = logging.getLogger(__name__)

        self.apk_path: str = apk_path
        self.working_dir_path: str = working_dir_path
        self.obfuscated_apk_path: str = obfuscated_apk_path
        self.ignore_libs: bool = ignore_libs
        self.interactive: bool = interactive
        self.virus_total_api_key: str = virus_total_api_key
        self.keystore_file: str = keystore_file
        self.keystore_password: str = keystore_password
        self.key_alias: str = key_alias
        self.key_password: str = key_password
        self.ignore_packages_file: str = ignore_packages_file
        self.use_aapt2 = use_aapt2
        if apk_path.endswith("aab"):
            self.is_bundle = True
        else:
            self.is_bundle = False

        # Random string (32 chars long) generation with ASCII letters and digits
        self.encryption_secret = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(32)
        )
        self.logger.debug(
            'Auto-generated random secret key for encryption: "{0}"'.format(
                self.encryption_secret
            )
        )

        # The list of obfuscators already used on the application.
        self.used_obfuscators: List[str] = []

        # How many obfuscators will add new fields/methods during this obfuscation
        # operation.
        self.obfuscators_adding_fields: int = 0
        self.obfuscators_adding_methods: int = 0

        # Flags indicating if certain files have already been added to the application
        # during this obfuscation operation. This is used to avoid adding the files
        # more than once (in that case the application rebuild wouldn't succeed).
        self.decrypt_asset_smali_file_added_flag: bool = False
        self.decrypt_string_smali_file_added_flag: bool = False

        self._remaining_fields_per_obfuscator = None
        self._remaining_methods_per_obfuscator = None

        self._is_decoded: bool = False
        self._decoded_apk_path: Union[str, None] = None
        self._is_multidex: bool = False
        self._manifest_file: Union[str, None] = None
        self._smali_files: List[str] = []
        self._multidex_smali_files: List[List[str]] = []  # A list for each dex file.
        self._native_lib_files: List[str] = []

        # Check if the apk file to obfuscate is a valid file.
        if not os.path.isfile(self.apk_path):
            self.logger.error('Unable to find file "{0}"'.format(self.apk_path))
            raise FileNotFoundError('Unable to find file "{0}"'.format(self.apk_path))

        # If no working directory is specified, use a new directory in the same
        # directory as the apk file to obfuscate.
        if not self.working_dir_path:
            self.working_dir_path = os.path.join(
                os.path.dirname(self.apk_path), "obfuscation_working_dir"
            )
            self.logger.debug(
                "No working directory provided, the operations will take place in the "
                'same directory as the input file, in the directory "{0}"'.format(
                    self.working_dir_path
                )
            )

        if not os.path.isdir(self.working_dir_path):
            try:
                os.makedirs(self.working_dir_path, exist_ok=True)
            except Exception as e:
                self.logger.error(
                    'Unable to create working directory "{0}": {1}'.format(
                        self.working_dir_path, e
                    )
                )
                raise

        # If the path of the output obfuscated apk is not specified, save it in the
        # working directory.
        if not self.obfuscated_apk_path:
            if self.is_bundle:
                self.obfuscated_apk_path = "{0}_obfuscated.aab".format(
                    os.path.join(
                        self.working_dir_path,
                        os.path.splitext(os.path.basename(self.apk_path))[0],
                    )
                )
            else:
                self.obfuscated_apk_path = "{0}_obfuscated.apk".format(
                    os.path.join(
                        self.working_dir_path,
                        os.path.splitext(os.path.basename(self.apk_path))[0],
                    )
                )
            self.logger.debug(
                "No obfuscated apk path provided, the result will be saved "
                'as "{0}"'.format(self.obfuscated_apk_path)
            )

    def _get_total_fields(self) -> Union[int, List[int]]:

        if not self._is_decoded:
            self.decode_apk()

        # The result is not saved but is calculated each time this function is called,
        # since the total number might change when the smali files are modified by
        # an obfuscator.

        # Workaround to use the same code for single dex and multidex applications.
        to_iterate = [self._smali_files]
        if self._is_multidex:
            to_iterate = self._multidex_smali_files

        # If this is a multidex application, return a list with the number of fields
        # contained in each dex, otherwise just return the total number of fields
        # contained in the application.

        return_list = []
        for dex_smali_files in to_iterate:

            total_fields = set()

            for smali_file in dex_smali_files:
                with open(smali_file, "r", encoding="utf-8") as current_file:
                    class_name = None
                    for line in current_file:

                        if not class_name:
                            class_match = util.class_pattern.match(line)
                            if class_match:
                                class_name = class_match.group("class_name")
                                continue

                        # Field declared in class.
                        field_match = util.field_pattern.match(line)
                        if field_match:
                            field = "{class_name}->{field_name}:{field_type}".format(
                                class_name=class_name,
                                field_name=field_match.group("field_name"),
                                field_type=field_match.group("field_type"),
                            )
                            total_fields.add(field)

                        # Field usage.
                        field_usage_match = util.field_usage_pattern.match(line)
                        if field_usage_match:
                            field = "{class_name}->{field_name}:{field_type}".format(
                                class_name=field_usage_match.group("field_object"),
                                field_name=field_usage_match.group("field_name"),
                                field_type=field_usage_match.group("field_type"),
                            )
                            total_fields.add(field)

            return_list.append(len(total_fields))

        if self._is_multidex:
            return return_list
        else:
            return return_list[0]

    def _get_total_methods(self) -> Union[int, List[int]]:

        if not self._is_decoded:
            self.decode_apk()

        # The result is not saved but is calculated each time this function is called,
        # since the total number might change when the smali files are modified by
        # an obfuscator.

        # Workaround to use the same code for single dex and multidex applications.
        to_iterate = [self._smali_files]
        if self._is_multidex:
            to_iterate = self._multidex_smali_files

        # If this is a multidex application, return a list with the number of methods
        # contained in each dex, otherwise just return the total number of methods
        # contained in the application.

        return_list = []
        for dex_smali_files in to_iterate:

            total_methods = set()

            for smali_file in dex_smali_files:
                with open(smali_file, "r", encoding="utf-8") as current_file:
                    class_name = None
                    for line in current_file:

                        if not class_name:
                            class_match = util.class_pattern.match(line)
                            if class_match:
                                class_name = class_match.group("class_name")
                                continue

                        # Method used in annotation.
                        annotation_method_match = util.annotation_method_pattern.match(
                            line
                        )
                        if annotation_method_match:
                            method = (
                                "{class_name}->"
                                "{method_name}({method_param}){method_return}".format(
                                    class_name=annotation_method_match.group(
                                        "method_object"
                                    ),
                                    method_name=annotation_method_match.group(
                                        "method_name"
                                    ),
                                    method_param=annotation_method_match.group(
                                        "method_param"
                                    ),
                                    method_return=annotation_method_match.group(
                                        "method_return"
                                    ),
                                )
                            )
                            total_methods.add(method)

                        # Method declared in class.
                        method_match = util.method_pattern.match(line)
                        if method_match:
                            method = (
                                "{class_name}->"
                                "{method_name}({method_param}){method_return}".format(
                                    class_name=class_name,
                                    method_name=method_match.group("method_name"),
                                    method_param=method_match.group("method_param"),
                                    method_return=method_match.group("method_return"),
                                )
                            )
                            total_methods.add(method)

                        # Method invocation.
                        invoke_match = util.invoke_pattern.match(line)
                        if invoke_match:
                            method = (
                                "{class_name}->"
                                "{method_name}({method_param}){method_return}".format(
                                    class_name=invoke_match.group("invoke_object"),
                                    method_name=invoke_match.group("invoke_method"),
                                    method_param=invoke_match.group("invoke_param"),
                                    method_return=invoke_match.group("invoke_return"),
                                )
                            )
                            total_methods.add(method)

            return_list.append(len(total_methods))

        if self._is_multidex:
            return return_list
        else:
            return return_list[0]

    def _get_remaining_fields(self) -> Union[int, List[int]]:

        if not self._is_decoded:
            self.decode_apk()

        # The result is not saved but is calculated each time this function is called,
        # since the the number of available fields might change when the smali files are
        # modified by an obfuscator.

        total_fields = self._get_total_fields()

        # If this is a multidex application, return a list with the number of remaining
        # available fields for each dex, otherwise just return the number of remaining
        # available fields for the application.

        # There is a 64K field limit for dex files.
        if self._is_multidex:
            remaining_fields = [64000 - dex_fields for dex_fields in total_fields]
        else:
            remaining_fields = 64000 - total_fields

        return remaining_fields

    def _get_remaining_methods(self) -> Union[int, List[int]]:

        if not self._is_decoded:
            self.decode_apk()

        # The result is not saved but is calculated each time this function is called,
        # since the the number of available methods might change when the smali files
        # are modified by an obfuscator.

        total_methods = self._get_total_methods()

        # If this is a multidex application, return a list with the number of remaining
        # available methods for each dex, otherwise just return the number of remaining
        # available methods for the application.

        # There is a 64K method limit for dex files.
        if self._is_multidex:
            remaining_methods = [64000 - dex_methods for dex_methods in total_methods]
        else:
            remaining_methods = 64000 - total_methods

        return remaining_methods

    def decode_apk(self) -> None:

        if not self._is_decoded:

            # The input apk will be decoded with apktool or BundleDecompiler.
            apktool: Apktool = Apktool()
            bundledecompiler: BundleDecompiler = BundleDecompiler()

            # <working_directory>/<apk_path>/
            self._decoded_apk_path = os.path.join(
                self.working_dir_path,
                os.path.splitext(os.path.basename(self.apk_path))[0],
            )
            try:
                if self.is_bundle:
                    bundledecompiler.decode(
                        self.apk_path, self._decoded_apk_path, force=False
                    )
                else:
                    apktool.decode(self.apk_path, self._decoded_apk_path, force=True)

                # Path to the decoded manifest file.
                if self.is_bundle:
                    self._manifest_file = os.path.join(
                        self._decoded_apk_path,
                        "base",
                        "manifest",
                        "AndroidManifest.xml",
                    )
                else:
                    self._manifest_file = os.path.join(
                        self._decoded_apk_path, "AndroidManifest.xml"
                    )

                # A list containing the paths to all the smali files obtained with
                # apktool or bundledecompiler.
                self._smali_files = [
                    os.path.join(root, file_name)
                    for root, dir_names, file_names in os.walk(self._decoded_apk_path)
                    for file_name in file_names
                    if file_name.endswith(".smali")
                ]

                if self.ignore_libs:
                    # Normalize paths for the current OS ('.join(x, "")' is used to add
                    # a trailing slash).
                    libs_to_ignore = list(
                        map(
                            lambda x: os.path.join(os.path.normpath(x), ""),
                            util.get_libs_to_ignore(),
                        )
                    )
                    filtered_smali_files = []

                    for smali_file in self._smali_files:
                        # Get the path without the initial part <root>/smali/.
                        relative_smali_file = os.path.join(
                            *(
                                os.path.relpath(
                                    smali_file, self._decoded_apk_path
                                ).split(os.path.sep)[1:]
                            )
                        )
                        # Get only the smali files that are not part of known third
                        # party libraries.
                        if not any(
                            relative_smali_file.startswith(lib)
                            for lib in libs_to_ignore
                        ):
                            filtered_smali_files.append(smali_file)

                    self._smali_files = filtered_smali_files

                # Sort the list of smali files to always have the list in the same
                # order.
                self._smali_files.sort()

                # Check if multidex.
                if self.is_bundle:
                    if os.path.isdir(
                        os.path.join(
                            self._decoded_apk_path, "base", "dex", "smali_classes2"
                        )
                    ):
                        self._is_multidex = True
                else:
                    if os.path.isdir(
                        os.path.join(self._decoded_apk_path, "smali_classes2")
                    ):
                        self._is_multidex = True

                if self._is_multidex:
                    smali_directories = ["smali"]
                    for i in range(2, 15):
                        smali_directories.append("smali_classes{0}".format(i))

                    for smali_directory in smali_directories:
                        if self.is_bundle:
                            current_directory = os.path.join(
                                self._decoded_apk_path,
                                "base",
                                "dex",
                                smali_directory,
                                "",
                            )
                        else:
                            current_directory = os.path.join(
                                self._decoded_apk_path, smali_directory, ""
                            )
                        if os.path.isdir(current_directory):
                            self._multidex_smali_files.append(
                                [
                                    smali_file
                                    for smali_file in self._smali_files
                                    if smali_file.startswith(current_directory)
                                ]
                            )

                # A list containing the paths to the native libraries included in the
                # application.
                self._native_lib_files = [
                    os.path.join(root, file_name)
                    for root, dir_names, file_names in os.walk(
                        os.path.join(self._decoded_apk_path, "lib")
                    )
                    for file_name in file_names
                    if file_name.endswith(".so")
                ]

                # Sort the list of native libraries to always have the list in the
                # same order.
                self._native_lib_files.sort()

            except Exception as e:
                self.logger.error("Error during apk decoding: {0}".format(e))
                raise
            else:
                self._is_decoded = True

    def get_remaining_fields_per_obfuscator(self) -> Union[int, List[int]]:

        if not self._is_decoded:
            self.decode_apk()

        # This function has to be called before running an obfuscator that adds new
        # fields. It will calculate the available number of fields that can be added by
        # each obfuscator before hitting the 64K limit. So if there are f available
        # fields and n obfuscators that will add new fields, each obfuscator will be
        # able to add a maximum of f/n fields.

        if self._remaining_fields_per_obfuscator:
            return self._remaining_fields_per_obfuscator

        remaining_fields = self._get_remaining_fields()

        if self.obfuscators_adding_fields > 1:
            if self._is_multidex:
                self._remaining_fields_per_obfuscator = [
                    dex_fields // self.obfuscators_adding_fields
                    for dex_fields in remaining_fields
                ]
            else:
                self._remaining_fields_per_obfuscator = (
                    remaining_fields // self.obfuscators_adding_fields
                )
        else:
            self._remaining_fields_per_obfuscator = remaining_fields

        return self._remaining_fields_per_obfuscator

    def get_remaining_methods_per_obfuscator(self) -> Union[int, List[int]]:

        if not self._is_decoded:
            self.decode_apk()

        # This function has to be called before running an obfuscator that adds new
        # methods. It will calculate the available number of methods that can be added
        # by each obfuscator before hitting the 64K limit. So if there are m available
        # methods and n obfuscators that will add new methods, each obfuscator will be
        # able to add a maximum of m/n methods.

        if self._remaining_methods_per_obfuscator:
            return self._remaining_methods_per_obfuscator

        remaining_methods = self._get_remaining_methods()

        if self.obfuscators_adding_methods > 1:
            if self._is_multidex:
                self._remaining_methods_per_obfuscator = [
                    dex_methods // self.obfuscators_adding_methods
                    for dex_methods in remaining_methods
                ]
            else:
                self._remaining_methods_per_obfuscator = (
                    remaining_methods // self.obfuscators_adding_methods
                )
        else:
            self._remaining_methods_per_obfuscator = remaining_methods

        return self._remaining_methods_per_obfuscator

    def build_obfuscated_apk(self) -> None:

        if not self._is_decoded:
            self.decode_apk()

        # The obfuscated apk will be built with apktool or BundleDecompiler.
        apktool: Apktool = Apktool()
        bundledecompiler: BundleDecompiler = BundleDecompiler()

        try:
            if self.is_bundle:
                bundledecompiler.build(self._decoded_apk_path, self.obfuscated_apk_path)
            else:
                apktool.build(
                    self._decoded_apk_path, self.obfuscated_apk_path, self.use_aapt2
                )
        except Exception as e:
            self.logger.error("Error during apk building: {0}".format(e))
            raise

    def sign_obfuscated_apk(self) -> None:

        # This method must be called AFTER the obfuscated apk has been built.

        # The obfuscated apk will be signed with APKSigner or BundleDecompiler.
        aabsigner: AABSigner = AABSigner()
        apksigner: ApkSigner = ApkSigner()

        # If a custom keystore file is not provided, use the default one bundled with
        # the tool. Otherwise check that the keystore password and a key alias are
        # provided along with the custom keystore.
        if not self.keystore_file:
            self.keystore_file = os.path.join(
                os.path.dirname(__file__), "resources", "obfuscation_keystore.jks"
            )
            self.keystore_password = "obfuscation_password"
            self.key_alias = "obfuscation_key"
        else:
            if not os.path.isfile(self.keystore_file):
                self.logger.error(
                    'Unable to find keystore file "{0}"'.format(self.keystore_file)
                )
                raise FileNotFoundError(
                    'Unable to find keystore file "{0}"'.format(self.keystore_file)
                )
            if not self.keystore_password or not self.key_alias:
                raise ValueError(
                    "When using a custom keystore file, keystore password and key "
                    "alias must be provided too"
                )

        try:
            if self.is_bundle:
                aabsigner.sign(
                    self.obfuscated_apk_path,
                )
            else:
                apksigner.resign(
                    self.obfuscated_apk_path,
                    self.keystore_file,
                    self.keystore_password,
                    self.key_alias,
                    self.key_password,
                )
        except Exception as e:
            self.logger.error("Error during apk signing: {0}".format(e))
            raise

    def align_obfuscated_apk(self) -> None:

        # This method must be called AFTER the obfuscated apk has been signed.

        # The obfuscated apk will be aligned with zipalign.
        zipalign: Zipalign = Zipalign()
        if self.is_bundle:
            return

        try:
            zipalign.align(self.obfuscated_apk_path)
        except Exception as e:
            self.logger.error("Error during apk alignment: {0}".format(e))
            raise

    def is_multidex(self) -> bool:

        if not self._is_decoded:
            self.decode_apk()

        return self._is_multidex

    def get_manifest_file(self) -> str:

        if not self._is_decoded:
            self.decode_apk()

        return self._manifest_file

    def get_smali_files(self) -> List[str]:

        if not self._is_decoded:
            self.decode_apk()

        return self._smali_files

    def get_multidex_smali_files(self) -> List[List[str]]:

        if not self._is_decoded:
            self.decode_apk()

        # If this isn't a multidex application, an empty list will be returned.
        return self._multidex_smali_files

    def get_native_lib_files(self) -> List[str]:

        if not self._is_decoded:
            self.decode_apk()

        return self._native_lib_files

    def get_assets_directory(self) -> str:

        if not self._is_decoded:
            self.decode_apk()

        # '.join(x, "")' is used to add a trailing slash.
        if self.is_bundle:
            return os.path.join(self._decoded_apk_path, "base", "assets", "")
        else:
            return os.path.join(self._decoded_apk_path, "assets", "")

    def get_resource_directory(self) -> str:

        if not self._is_decoded:
            self.decode_apk()

        # '.join(x, "")' is used to add a trailing slash.
        if self.is_bundle:
            return os.path.join(self._decoded_apk_path, "base", "res", "")
        else:
            return os.path.join(self._decoded_apk_path, "res", "")

    def get_ignore_package_names(self) -> List[str]:
        ignore_package_list = []

        if self.ignore_packages_file is None:
            return ignore_package_list

        # Normalize package names into smali format.
        for item in util.get_non_empty_lines_from_file(self.ignore_packages_file):
            ignore_package_list.append("L{0}".format(item).replace(".", "/"))

        return ignore_package_list
