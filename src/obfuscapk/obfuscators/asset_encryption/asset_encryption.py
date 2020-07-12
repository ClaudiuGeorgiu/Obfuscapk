#!/usr/bin/env python3

import logging
import os
import re
from typing import List, Set

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from obfuscapk import obfuscator_category
from obfuscapk import util
from obfuscapk.obfuscation import Obfuscation


class AssetEncryption(obfuscator_category.IEncryptionObfuscator):
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
            # This instruction takes 2 registers, the latter contains the name of the
            # asset file to load.
            open_asset_invoke_pattern = re.compile(
                r"\s+invoke-virtual\s"
                r"{[vp0-9]+,\s(?P<param_register>[vp0-9]+)},\s"
                r"Landroid/content/res/AssetManager;->"
                r"open\(Ljava/lang/String;\)Ljava/io/InputStream;"
            )

            assets_dir = obfuscation_info.get_assets_directory()
            already_encrypted_files: Set[str] = set()

            # Continue only if there are assets file to encrypt.
            if os.path.isdir(assets_dir):
                for smali_file in util.show_list_progress(
                    obfuscation_info.get_smali_files(),
                    interactive=obfuscation_info.interactive,
                    description="Encrypting asset files",
                ):
                    self.logger.debug(
                        'Encrypting asset files used in smali file "{0}"'.format(
                            smali_file
                        )
                    )

                    with open(smali_file, "r", encoding="utf-8") as current_file:
                        lines = current_file.readlines()

                    # Line numbers where an asset file is opened.
                    asset_index: List[int] = []

                    # Registers containing the strings with the names of the opened
                    # asset files.
                    asset_register: List[str] = []

                    # Names of the opened asset files.
                    asset_names: List[str] = []

                    # Each time an asset name is added to asset_names, the line number
                    # of the asset open instruction is added to this list, so the
                    # element in position n in asset_names is opened at the line in
                    # position n in asset_index_for_asset_names. So each time an asset
                    # file is encrypted, the corresponding line is changed to open the
                    # encrypted file. A new variable is needed because asset_index could
                    # have different indices than asset_names because there might be
                    # assets loaded from other variables and not constant strings.
                    asset_index_for_asset_names: List[int] = []

                    for line_number, line in enumerate(lines):
                        invoke_match = open_asset_invoke_pattern.match(line)
                        if invoke_match:
                            # Asset file open instruction.
                            asset_index.append(line_number)
                            asset_register.append(invoke_match.group("param_register"))

                    # Iterate the lines backwards (until the method declaration is
                    # reached) and for each asset file open instruction find the
                    # constant string containing the name of the opened file (if any).
                    for asset_number, index in enumerate(asset_index):
                        for line_number in range(index - 1, 0, -1):
                            if lines[line_number].startswith(".method "):
                                # Method declaration reached, no constant string found
                                # for this asset file so proceed with the next (if any).
                                break

                            # NOTE: if an asset is opened using a constant string, it
                            # will be encrypted. If other code opens the same assets but
                            # using a variable instead of a constant string, it won't
                            # work anymore and this case is not handled by this
                            # obfuscator.

                            string_match = util.const_string_pattern.match(
                                lines[line_number]
                            )
                            if (
                                string_match
                                and string_match.group("register")
                                == asset_register[asset_number]
                            ):
                                # Asset file name string declaration.
                                asset_names.append(string_match.group("string"))
                                asset_index_for_asset_names.append(
                                    asset_index[asset_number]
                                )

                                # Proceed with the next asset file (if any).
                                break

                    # Encrypt the the loaded asset files and replace the old code with
                    # new code to decrypt the encrypted asset files.
                    for index, asset_name in enumerate(asset_names):
                        asset_file = os.path.join(assets_dir, asset_name)
                        if os.path.isfile(asset_file):

                            # Encrypt the asset file (if not already encrypted).
                            if asset_file not in already_encrypted_files:
                                with open(asset_file, "rb") as original_asset_file:
                                    encrypted_content = AES.new(
                                        key=self.encryption_secret.encode(),
                                        mode=AES.MODE_ECB,
                                    ).encrypt(
                                        pad(original_asset_file.read(), AES.block_size)
                                    )

                                with open(asset_file, "wb") as encrypted_asset_file:
                                    encrypted_asset_file.write(encrypted_content)

                                already_encrypted_files.add(asset_file)

                            # Replace the old code with new code to decrypt the
                            # encrypted asset file.
                            lines[asset_index_for_asset_names[index]] = (
                                lines[asset_index_for_asset_names[index]]
                                .replace("invoke-virtual", "invoke-static")
                                .replace(
                                    "Landroid/content/res/AssetManager;->"
                                    "open(Ljava/lang/String;)Ljava/io/InputStream;",
                                    "Lcom/decryptassetmanager/DecryptAsset;->"
                                    "decryptAsset(Landroid/content/res/AssetManager;"
                                    "Ljava/lang/String;)Ljava/io/InputStream;",
                                )
                            )

                    with open(smali_file, "w", encoding="utf-8") as current_file:
                        current_file.writelines(lines)

                if (
                    not obfuscation_info.decrypt_asset_smali_file_added_flag
                    and already_encrypted_files
                ):
                    # Add to the app the code for decrypting the encrypted assets.
                    # The code for decrypting can be put in any smali directory, since
                    # it will be moved to the correct directory when rebuilding the
                    # application.
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

            else:
                self.logger.debug("No assets found")

        except Exception as e:
            self.logger.error(
                'Error during execution of "{0}" obfuscator: {1}'.format(
                    self.__class__.__name__, e
                )
            )
            raise

        finally:
            obfuscation_info.used_obfuscators.append(self.__class__.__name__)
