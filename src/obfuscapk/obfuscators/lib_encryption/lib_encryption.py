#!/usr/bin/env python3

import logging
import os
import re
from typing import List, Dict

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from obfuscapk import obfuscator_category
from obfuscapk import util
from obfuscapk.obfuscation import Obfuscation


class LibEncryption(obfuscator_category.IEncryptionObfuscator):
    def __init__(self):
        self.logger = logging.getLogger(
            "{0}.{1}".format(__name__, self.__class__.__name__)
        )
        super().__init__()

        self.encryption_secret = "This-key-need-to-be-32-character"

    def obfuscate(self, obfuscation_info: Obfuscation):
        self.logger.info('Running "{0}" obfuscator'.format(self.__class__.__name__))

        self.encryption_secret = obfuscation_info.encryption_secret
        try:
            native_libs = obfuscation_info.get_native_lib_files()

            native_lib_invoke_pattern = re.compile(
                r"\s+invoke-static\s{(?P<invoke_pass>[vp0-9]+)},\s"
                r"Ljava/lang/System;->loadLibrary\(Ljava/lang/String;\)V"
            )

            encrypted_to_original_mapping: Dict[str, str] = {}

            if native_libs:
                for smali_file in util.show_list_progress(
                    obfuscation_info.get_smali_files(),
                    interactive=obfuscation_info.interactive,
                    description="Encrypting native libraries",
                ):
                    self.logger.debug(
                        "Replacing native libraries with encrypted native libraries "
                        'in file "{0}"'.format(smali_file)
                    )

                    with open(smali_file, "r", encoding="utf-8") as current_file:
                        lines = current_file.readlines()

                    class_name = None

                    local_count = 16

                    # Names of the loaded libraries.
                    lib_names: List[str] = []

                    editing_constructor = False
                    start_index = 0
                    for line_number, line in enumerate(lines):

                        if not class_name:
                            class_match = util.class_pattern.match(line)
                            if class_match:
                                class_name = class_match.group("class_name")
                                continue

                        # Native libraries should be loaded inside static constructors.
                        if (
                            line.startswith(".method static constructor <clinit>()V")
                            and not editing_constructor
                        ):
                            # Entering static constructor.
                            editing_constructor = True
                            start_index = line_number + 1
                            local_match = util.locals_pattern.match(
                                lines[line_number + 1]
                            )
                            if local_match:
                                local_count = int(local_match.group("local_count"))
                                if local_count <= 15:
                                    # An additional register is needed for the
                                    # encryption.
                                    local_count += 1
                                    lines[line_number + 1] = "\t.locals {0}\n".format(
                                        local_count
                                    )
                                    continue

                            # For some reason the locals declaration was not found where
                            # it should be, so assume the local registers are all used
                            # (we can't add any instruction here).
                            break

                        elif line.startswith(".end method") and editing_constructor:
                            # Only one static constructor per class.
                            break

                        elif editing_constructor:
                            # Inside static constructor.
                            invoke_match = native_lib_invoke_pattern.match(line)
                            if invoke_match:
                                # Native library load instruction. Iterate the
                                # constructor lines backwards in order to find the
                                # string containing the name of the loaded library.
                                for l_num in range(line_number - 1, start_index, -1):
                                    string_match = util.const_string_pattern.match(
                                        lines[l_num]
                                    )
                                    if string_match and string_match.group(
                                        "register"
                                    ) == invoke_match.group("invoke_pass"):
                                        # Native library string declaration.
                                        lib_names.append(string_match.group("string"))

                                # Static constructors take no parameters, so the highest
                                # register is v<local_count - 1>.
                                lines[line_number] = (
                                    "\tconst-class v{class_register_num}, "
                                    "{class_name}\n\n"
                                    "\tinvoke-static {{v{class_register_num}, "
                                    "{original_register}}}, "
                                    "Lcom/decryptassetmanager/DecryptAsset;->"
                                    "loadEncryptedLibrary("
                                    "Ljava/lang/Class;Ljava/lang/String;)V\n".format(
                                        class_name=class_name,
                                        original_register=invoke_match.group(
                                            "invoke_pass"
                                        ),
                                        class_register_num=local_count - 1,
                                    )
                                )

                        # Encrypt the native libraries used in code and put them
                        # in assets folder.
                        assets_dir = obfuscation_info.get_assets_directory()
                        os.makedirs(assets_dir, exist_ok=True)
                        for native_lib in native_libs:
                            for lib_name in lib_names:
                                if native_lib.endswith("{0}.so".format(lib_name)):
                                    arch = os.path.basename(os.path.dirname(native_lib))
                                    encrypted_lib_path = os.path.join(
                                        assets_dir,
                                        "lib.{arch}.{lib_name}.so".format(
                                            arch=arch, lib_name=lib_name
                                        ),
                                    )

                                    with open(native_lib, "rb") as native_lib_file:
                                        encrypted_lib = AES.new(
                                            key=self.encryption_secret.encode(),
                                            mode=AES.MODE_ECB,
                                        ).encrypt(
                                            pad(native_lib_file.read(), AES.block_size)
                                        )

                                    with open(
                                        encrypted_lib_path, "wb"
                                    ) as encrypted_lib_file:
                                        encrypted_lib_file.write(encrypted_lib)

                                    encrypted_to_original_mapping[
                                        encrypted_lib_path
                                    ] = native_lib

                    with open(smali_file, "w", encoding="utf-8") as current_file:
                        current_file.writelines(lines)

                if (
                    not obfuscation_info.decrypt_asset_smali_file_added_flag
                    and encrypted_to_original_mapping
                ):
                    # Add to the app the code for decrypting the encrypted native
                    # libraries. The code for decrypting can be put in any smali
                    # directory, since it will be moved to the correct directory
                    # when rebuilding the application.
                    destination_dir = os.path.dirname(
                        obfuscation_info.get_smali_files()[0]
                    )
                    destination_file = os.path.join(
                        destination_dir, "DecryptAsset.smali"
                    )
                    with open(
                        destination_file, "w", encoding="utf-8"
                    ) as decrypt_asset_smali:
                        decrypt_asset_smali.write(
                            util.get_decrypt_asset_smali_code(self.encryption_secret)
                        )
                        obfuscation_info.decrypt_asset_smali_file_added_flag = True

                # Remove the original native libraries that were encrypted (the
                # encrypted ones will be used instead).
                for _, original_lib in encrypted_to_original_mapping.items():
                    try:
                        os.remove(original_lib)
                    except OSError as e:
                        self.logger.warning(
                            'Unable to delete native library "{0}": {1}'.format(
                                original_lib, e
                            )
                        )

            else:
                self.logger.debug("No native libraries found")

        except Exception as e:
            self.logger.error(
                'Error during execution of "{0}" obfuscator: {1}'.format(
                    self.__class__.__name__, e
                )
            )
            raise

        finally:
            obfuscation_info.used_obfuscators.append(self.__class__.__name__)
