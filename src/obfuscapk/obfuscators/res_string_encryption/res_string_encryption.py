#!/usr/bin/env python3

import logging
import os
import re
import xml.etree.cElementTree as Xml
from binascii import hexlify
from typing import List, Set

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad

from obfuscapk import obfuscator_category
from obfuscapk import util
from obfuscapk.obfuscation import Obfuscation


class ResStringEncryption(obfuscator_category.IEncryptionObfuscator):
    def __init__(self):
        self.logger = logging.getLogger(
            "{0}.{1}".format(__name__, self.__class__.__name__)
        )
        super().__init__()

        self.encryption_secret = "This-key-need-to-be-32-character"

    def encrypt_string(self, string_to_encrypt: str) -> str:
        # This is needed to remove the escaping added by Python. For example, if we
        # find in string resources the string "\"message\"" Android will treat it as
        # "message" while in Python it's \"message\", so we need to encrypt "message"
        # and not \"message\" (we have to remove the unnecessary escaping, otherwise
        # the backslashes would by encrypted as part of the string).
        string_to_encrypt = string_to_encrypt.encode(errors="replace").decode(
            "unicode_escape"
        )

        key = PBKDF2(
            password=self.encryption_secret,
            salt=self.encryption_secret.encode(),
            dkLen=32,
            count=128,
        )
        encrypted_string = hexlify(
            AES.new(key=key, mode=AES.MODE_ECB).encrypt(
                pad(string_to_encrypt.encode(errors="replace"), AES.block_size)
            )
        ).decode()
        return encrypted_string

    def encrypt_string_resources(
        self, string_resources_xml_file: str, string_names_to_encrypt: Set[str]
    ):

        xml_parser = Xml.XMLParser(encoding="utf-8")
        xml_tree = Xml.parse(string_resources_xml_file, parser=xml_parser)

        for xml_string in xml_tree.iter("string"):
            string_name = xml_string.get("name", None)
            string_value = xml_string.text
            if string_name and string_value and string_name in string_names_to_encrypt:
                encrypted_string_value = self.encrypt_string(string_value)
                xml_string.text = encrypted_string_value

        xml_tree.write(string_resources_xml_file, encoding="utf-8")

    def encrypt_string_array_resources(
        self,
        string_array_resources_xml_file: str,
        string_array_names_to_encrypt: Set[str],
    ):

        xml_parser = Xml.XMLParser(encoding="utf-8")
        xml_tree = Xml.parse(string_array_resources_xml_file, parser=xml_parser)

        for xml_string_array in xml_tree.iter("string-array"):
            string_array_name = xml_string_array.get("name", None)
            if string_array_name and string_array_name in string_array_names_to_encrypt:
                for item in xml_string_array.iter("item"):
                    if item.text:
                        encrypted_string_value = self.encrypt_string(item.text)
                        item.text = encrypted_string_value

        xml_tree.write(string_array_resources_xml_file, encoding="utf-8")

    def obfuscate(self, obfuscation_info: Obfuscation):
        self.logger.info('Running "{0}" obfuscator'.format(self.__class__.__name__))

        self.encryption_secret = obfuscation_info.encryption_secret
        try:
            string_res_field_pattern = re.compile(
                r"\.field\spublic\sstatic\sfinal\s(?P<string_name>\S+?):I\s=\s"
                r"(?P<string_id>[0-9a-fA-FxX]+)",
                re.UNICODE,
            )

            string_id_pattern = re.compile(
                r"\s+const\s(?P<register>[vp0-9]+),\s(?P<id>\S+)"
            )

            string_array_id_pattern = re.compile(
                r"\s+const/high16\s(?P<register>[vp0-9]+),\s(?P<id>\S+)"
            )

            load_string_res_pattern = re.compile(
                r"\s+invoke-virtual\s"
                r"{[vp0-9]+,\s(?P<param_register>[vp0-9]+)},\s"
                r"(Landroid/content/res/Resources;->getString\(I\)Ljava/lang/String;"
                r"|Landroid/content/Context;->getString\(I\)Ljava/lang/String;)"
            )

            load_string_array_res_pattern = re.compile(
                r"\s+invoke-virtual\s"
                r"{[vp0-9]+,\s(?P<param_register>[vp0-9]+)},\s"
                r"Landroid/content/res/Resources;->"
                r"getStringArray\(I\)\[Ljava/lang/String;"
            )

            move_result_obj_pattern = re.compile(
                r"\s+move-result-object\s(?P<register>[vp0-9]+)"
            )

            # Set with the names of the encrypted string and string array resources.
            encrypted_res_strings: Set[str] = set()
            encrypted_res_string_arrays: Set[str] = set()

            # Find the mappings between string name and string id.
            string_id_to_string_name: dict = {}
            string_array_id_to_string_name: dict = {}
            for smali_file in obfuscation_info.get_smali_files():
                if smali_file.endswith("R$string.smali"):
                    with open(smali_file, "r", encoding="utf-8") as current_file:
                        for line in current_file:
                            if line.startswith(".method "):
                                # Method declaration reached, no more field declarations
                                # from now on.
                                break
                            field_match = string_res_field_pattern.match(line)
                            if field_match:
                                # String name and id declaration.
                                string_id_to_string_name[
                                    field_match.group("string_id")
                                ] = field_match.group("string_name")

                elif smali_file.endswith("R$array.smali"):
                    with open(smali_file, "r", encoding="utf-8") as current_file:
                        for line in current_file:
                            if line.startswith(".method "):
                                # Method declaration reached, no more field declarations
                                # from now on.
                                break
                            field_match = string_res_field_pattern.match(line)
                            if field_match:
                                # String array name and id declaration.
                                string_array_id_to_string_name[
                                    field_match.group("string_id")
                                ] = field_match.group("string_name")

            for smali_file in util.show_list_progress(
                obfuscation_info.get_smali_files(),
                interactive=obfuscation_info.interactive,
                description="Encrypting string resources",
            ):
                self.logger.debug(
                    'Encrypting string resources in file "{0}"'.format(smali_file)
                )

                with open(smali_file, "r", encoding="utf-8") as current_file:
                    lines = current_file.readlines()

                # Line numbers where a string is loaded from resources.
                string_index: List[int] = []

                # Registers containing the strings loaded from resources.
                string_register: List[str] = []

                # The number of local registers in the method where a string resource
                # is loaded.
                string_local_count: List[int] = []

                # Line numbers where a string array is loaded from resources.
                string_array_index: List[int] = []

                # Registers containing the string arrays loaded from resources.
                string_array_register: List[str] = []

                # The number of local registers in the method where a string array
                # resource is loaded.
                string_array_local_count: List[int] = []

                # Look for resource strings that can be encrypted.
                current_local_count = 0
                for line_number, line in enumerate(lines):
                    # We are iterating the lines in order, so each time we enter a
                    # method we'll find the declaration with the number of local
                    # registers available. We need this information because the invoke
                    # instruction that we need later won't take registers with values
                    # greater than 15.
                    match = util.locals_pattern.match(line)
                    if match:
                        current_local_count = int(match.group("local_count"))
                        continue

                    string_res_match = load_string_res_pattern.match(line)
                    if string_res_match:
                        string_index.append(line_number)
                        string_register.append(string_res_match.group("param_register"))
                        string_local_count.append(current_local_count)
                        continue

                    string_array_res_match = load_string_array_res_pattern.match(line)
                    if string_array_res_match:
                        string_array_index.append(line_number)
                        string_array_register.append(
                            string_array_res_match.group("param_register")
                        )
                        string_array_local_count.append(current_local_count)

                # Iterate the lines backwards (until the method declaration is reached)
                # and find the id of each string resource.
                for string_number, index in enumerate(string_index):
                    for line_number in range(index - 1, 0, -1):
                        if lines[line_number].startswith(".method "):
                            # Method declaration reached, no string resource found so
                            # proceed with the next (if any). If we are here it means
                            # that the string was loaded from a variable and not from
                            # a constant reference, so this string should not be
                            # encrypted. We set the corresponding string_index to -1
                            # and we won't insert any decryption code for this string.
                            string_index[string_number] = -1
                            break

                        # NOTE: if a string is loaded from resources, it will be
                        # encrypted. If other code loads the same string but using a
                        # variable instead of the resource id, it won't work anymore
                        # and this case is not handled by this obfuscator.

                        id_match = string_id_pattern.match(lines[line_number])
                        if (
                            id_match
                            and id_match.group("register")
                            == string_register[string_number]
                        ):
                            # String id declaration, get the name corresponding to
                            # the id and add it to the list of string resources to
                            # be encrypted.
                            if id_match.group("id") in string_id_to_string_name:
                                encrypted_res_strings.add(
                                    string_id_to_string_name[id_match.group("id")]
                                )

                            # Proceed with the next asset file (if any).
                            break

                # Iterate the lines backwards (until the method declaration is reached)
                # and find the id of each string array resource.
                for string_array_number, index in enumerate(string_array_index):
                    for line_number in range(index - 1, 0, -1):
                        if lines[line_number].startswith(".method "):
                            # Method declaration reached, no string array resource
                            # found so proceed with the next (if any).
                            # If we are here it means that the string was loaded from a
                            # variable and not from a constant reference, so this string
                            # should not be encrypted. We set the corresponding
                            # string_array_index to -1 and we won't insert any
                            # decryption code for this string.
                            string_array_index[string_array_number] = -1
                            break

                        # NOTE: if a string array is loaded from resources, it will be
                        # encrypted. If other code loads the same string array but using
                        # a variable instead of the resource id, it won't work anymore
                        # and this case is not handled by this obfuscator.

                        id_match = string_array_id_pattern.match(lines[line_number])
                        if (
                            id_match
                            and id_match.group("register")
                            == string_array_register[string_array_number]
                        ):
                            # String array id declaration, get the name corresponding to
                            # the id and add it to the list of string array resources
                            # to be encrypted.
                            if id_match.group("id") in string_array_id_to_string_name:
                                encrypted_res_string_arrays.add(
                                    string_array_id_to_string_name[id_match.group("id")]
                                )

                            # Proceed with the next asset file (if any).
                            break

                # After each string resource is loaded, decrypt it (the string resource
                # will be encrypted directly in the xml file).
                for string_number, index in enumerate(
                    i for i in string_index if i != -1
                ):
                    # For each resource string loaded, look for the next
                    # move-result-object instruction to see in which register the string
                    # is saved, in order to add a new instruction to decrypt it.
                    for line_number in range(index + 1, len(lines)):
                        if lines[line_number].startswith(".end method"):
                            # Method end reached, no move-result-object instruction
                            # found for this string resource (the loaded string is not
                            # used), so proceed with the next (if any).
                            break

                        # If the string resource is put into a register v0-v15 we can
                        # proceed with the encryption, but if it uses a p<number>
                        # register, before encrypting we have to check if
                        # <number> + locals <= 15.
                        move_result_match = move_result_obj_pattern.match(
                            lines[line_number]
                        )
                        if move_result_match:
                            reg_type = move_result_match.group("register")[:1]
                            reg_number = int(move_result_match.group("register")[1:])
                            if (reg_type == "v" and reg_number <= 15) or (
                                reg_type == "p"
                                and reg_number + string_local_count[string_number] <= 15
                            ):
                                # Add string decrypt instruction.
                                lines[line_number] += (
                                    "\n\tinvoke-static {{{register}}}, "
                                    "Lcom/decryptstringmanager/DecryptString;->"
                                    "decryptString(Ljava/lang/String;)"
                                    "Ljava/lang/String;\n\n".format(
                                        register=move_result_match.group("register")
                                    )
                                    + lines[line_number]
                                )

                            # Proceed with the next string resource (if any).
                            break

                # After each string array resource is loaded, decrypt it (the string
                # array resource will be encrypted directly in the xml file).
                for string_array_number, index in enumerate(
                    i for i in string_array_index if i != -1
                ):
                    # For each resource string array loaded, look for the next
                    # move-result-object instruction to see in which register the string
                    # array is saved, in order to add a new instruction to decrypt it.
                    for line_number in range(index + 1, len(lines)):
                        if lines[line_number].startswith(".end method"):
                            # Method end reached, no move-result-object instruction
                            # found for this string array resource (the loaded string
                            # array is not used), so proceed with the next (if any).
                            break

                        # If the string array resource is put into a register v0-v15 we
                        # can proceed with the encryption, but if it uses a p<number>
                        # register, before encrypting we have to check if
                        # <number> + locals <= 15.
                        move_result_match = move_result_obj_pattern.match(
                            lines[line_number]
                        )
                        if move_result_match:
                            reg_type = move_result_match.group("register")[:1]
                            reg_number = int(move_result_match.group("register")[1:])
                            if (reg_type == "v" and reg_number <= 15) or (
                                reg_type == "p"
                                and reg_number
                                + string_array_local_count[string_array_number]
                                <= 15
                            ):
                                # Add string array decrypt instruction.
                                lines[line_number] += (
                                    "\n\tinvoke-static {{{register}}}, "
                                    "Lcom/decryptstringmanager/DecryptString;->"
                                    "decryptStringArray([Ljava/lang/String;)"
                                    "[Ljava/lang/String;\n\n".format(
                                        register=move_result_match.group("register")
                                    )
                                    + lines[line_number]
                                )

                            # Proceed with the next string array resource (if any).
                            break

                with open(smali_file, "w", encoding="utf-8") as current_file:
                    current_file.writelines(lines)

            # Encrypt the strings and the string arrays in the resource files.
            strings_xml_path = os.path.join(
                obfuscation_info.get_resource_directory(), "values", "strings.xml"
            )
            string_arrays_xml_path = os.path.join(
                obfuscation_info.get_resource_directory(), "values", "arrays.xml"
            )
            if os.path.isfile(strings_xml_path):
                self.encrypt_string_resources(strings_xml_path, encrypted_res_strings)
            if os.path.isfile(string_arrays_xml_path):
                self.encrypt_string_array_resources(
                    string_arrays_xml_path, encrypted_res_string_arrays
                )

            if not obfuscation_info.decrypt_string_smali_file_added_flag and (
                encrypted_res_strings or encrypted_res_string_arrays
            ):
                # Add to the app the code for decrypting the encrypted strings. The code
                # for decrypting can be put in any smali directory, since it will be
                # moved to the correct directory when rebuilding the application.
                destination_dir = os.path.dirname(obfuscation_info.get_smali_files()[0])
                destination_file = os.path.join(destination_dir, "DecryptString.smali")
                with open(
                    destination_file, "w", encoding="utf-8"
                ) as decrypt_string_smali:
                    decrypt_string_smali.write(
                        util.get_decrypt_string_smali_code(self.encryption_secret)
                    )
                    obfuscation_info.decrypt_string_smali_file_added_flag = True

        except Exception as e:
            self.logger.error(
                'Error during execution of "{0}" obfuscator: {1}'.format(
                    self.__class__.__name__, e
                )
            )
            raise

        finally:
            obfuscation_info.used_obfuscators.append(self.__class__.__name__)
