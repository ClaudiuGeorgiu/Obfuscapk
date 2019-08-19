#!/usr/bin/env python3.7
# coding: utf-8

import logging
import os
import re
from typing import List, Set

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from obfuscapk import obfuscator_category
from obfuscapk import util
from obfuscapk.obfuscation import Obfuscation


class LibEncryption(obfuscator_category.IEncryptionObfuscator):

    def __init__(self):
        self.logger = logging.getLogger('{0}.{1}'.format(__name__, self.__class__.__name__))
        super().__init__()

        self.encryption_secret = 'This-key-need-to-be-32-character'

    def obfuscate(self, obfuscation_info: Obfuscation):
        self.logger.info('Running "{0}" obfuscator'.format(self.__class__.__name__))

        try:
            native_libs = obfuscation_info.get_native_lib_files()

            native_lib_invoke_pattern = re.compile(r'\s+invoke-static\s{(?P<invoke_pass>[vp0-9]+)},\s'
                                                   r'Ljava/lang/System;->loadLibrary\(Ljava/lang/String;\)V')

            encrypted_libs: Set[str] = set()

            if native_libs:
                for smali_file in util.show_list_progress(obfuscation_info.get_smali_files(),
                                                          interactive=obfuscation_info.interactive,
                                                          description='Encrypting native libraries'):
                    self.logger.debug('Replacing native libraries with encrypted native libraries '
                                      'in file "{0}"'.format(smali_file))

                    with open(smali_file, 'r', encoding='utf-8') as current_file:
                        lines = current_file.readlines()

                    # Line numbers where a native library is loaded.
                    lib_index: List[int] = []

                    # Registers containing the strings with the names of the loaded libraries.
                    lib_register: List[str] = []

                    # Names of the loaded libraries.
                    lib_names: List[str] = []

                    editing_constructor = False
                    start_index = 0
                    for line_number, line in enumerate(lines):
                        if line.startswith('.method static constructor <clinit>()V') and not editing_constructor:
                            # Entering static constructor.
                            editing_constructor = True
                            start_index = line_number

                        elif line.startswith('.end method') and editing_constructor:
                            # Only one static constructor per class.
                            break

                        elif editing_constructor:
                            # Inside static constructor.
                            invoke_match = native_lib_invoke_pattern.match(line)
                            if invoke_match:
                                # Native library load instruction.
                                lib_index.append(line_number)
                                lib_register.append(invoke_match.group('invoke_pass'))

                    # Iterate the constructor lines backwards and for each library load instruction
                    # find the string containing the name of the loaded library.
                    for lib_number, index in enumerate(lib_index):
                        for line_number in range(index - 1, start_index, -1):
                            string_match = util.const_string_pattern.match(lines[line_number])
                            if string_match and string_match.group('register') == lib_register[lib_number]:
                                # Native library string declaration.
                                lib_names.append(string_match.group('string'))

                                # Change the library string since it won't be used anymore.
                                lines[line_number] = lines[line_number].replace(
                                    '"{0}"'.format(string_match.group('string')), '"removed"')

                                # Proceed with the next native library (if any).
                                break

                    # Remove current native library invocations (new invocations to the encrypted version
                    # of the libraries will be added later). The const-string references to the libraries
                    # are just renamed and not removed, to avoid errors in case there is a surrounding
                    # try/catch block.
                    lines = [line for index, line in enumerate(lines) if index not in lib_index]

                    # Insert invocations to the encrypted native libraries (if any).
                    if lib_names:
                        editing_method = False
                        after_invoke_super = False
                        for line in lines:
                            if line.startswith('.method protected attachBaseContext(Landroid/content/Context;)V') \
                                    and not editing_method:
                                # Entering method.
                                editing_method = True

                            elif line.startswith('.end method') and editing_method:
                                # Only one method with this signature per class.
                                break

                            elif editing_method and not after_invoke_super:
                                # Inside method, before the call to the parent constructor.
                                # Look for the call to the parent constructor.
                                invoke_match = util.invoke_pattern.match(line)
                                if invoke_match and invoke_match.group('invoke_type') == 'invoke-super':
                                    after_invoke_super = True

                            elif editing_method and after_invoke_super:
                                # Inside method, after the call to the parent constructor. We'll insert here
                                # the invocations of the encrypted native libraries.
                                for lib_name in lib_names:
                                    line += '\n\tconst-string/jumbo p0, "{name}"\n'.format(name=lib_name) + \
                                        '\n\tinvoke-static {p1, p0}, ' \
                                        'Lcom/decryptassetmanager/DecryptAsset;->' \
                                        'loadEncryptedLibrary(Landroid/content/Context;Ljava/lang/String;)V\n'

                        # No existing attachBaseContext method was found, we have to declare it.
                        if not editing_method:
                            # Look for the virtual methods section (if present, otherwise add it).
                            virtual_methods_line = next((line_number for line_number, line in enumerate(lines)
                                                         if line.startswith('# virtual methods')), None)
                            if not virtual_methods_line:
                                lines.append('\n# virtual methods')

                            lines.append('\n.method protected attachBaseContext(Landroid/content/Context;)V\n'
                                         '\t.locals 0\n'
                                         '\n\tinvoke-super {p0, p1}, '
                                         'Landroid/support/v7/app/AppCompatActivity;->'
                                         'attachBaseContext(Landroid/content/Context;)V\n')

                            for lib_name in lib_names:
                                lines.append('\n\tconst-string/jumbo p0, "{name}"\n'.format(name=lib_name) +
                                             '\n\tinvoke-static {p1, p0}, '
                                             'Lcom/decryptassetmanager/DecryptAsset;->'
                                             'loadEncryptedLibrary(Landroid/content/Context;Ljava/lang/String;)V\n')

                            lines.append('\n\treturn-void'
                                         '\n.end method\n')

                        # Encrypt the native libraries used in code and put them in asset folder.
                        assets_dir = obfuscation_info.get_assets_directory()
                        os.makedirs(assets_dir, exist_ok=True)
                        for native_lib in native_libs:
                            for lib_name in lib_names:
                                if native_lib.endswith('{0}.so'.format(lib_name)):
                                    arch = os.path.basename(os.path.dirname(native_lib))
                                    encrypted_lib_path = os.path.join(assets_dir, 'lib,{arch},{lib_name}.so'
                                                                      .format(arch=arch, lib_name=lib_name))

                                    with open(native_lib, 'rb') as native_lib_file:
                                        encrypted_lib = AES \
                                            .new(key=self.encryption_secret.encode(), mode=AES.MODE_ECB) \
                                            .encrypt(pad(native_lib_file.read(), AES.block_size))

                                    with open(encrypted_lib_path, 'wb') as encrypted_lib_file:
                                        encrypted_lib_file.write(encrypted_lib)

                                    encrypted_libs.add(encrypted_lib_path)

                    with open(smali_file, 'w', encoding='utf-8') as current_file:
                        current_file.writelines(lines)

                if not obfuscation_info.decrypt_asset_smali_file_added_flag and encrypted_libs:
                    # Add to the app the code for decrypting the encrypted native libraries. The code
                    # for decrypting can be put in any smali directory, since it will be moved to the
                    # correct directory when rebuilding the application.
                    destination_dir = os.path.dirname(obfuscation_info.get_smali_files()[0])
                    destination_file = os.path.join(destination_dir, 'DecryptAsset.smali')
                    with open(destination_file, 'w', encoding='utf-8') as decrypt_asset_smali:
                        decrypt_asset_smali.write(util.get_decrypt_asset_smali_code())
                        obfuscation_info.decrypt_asset_smali_file_added_flag = True

            else:
                self.logger.debug('No native libraries found')

        except Exception as e:
            self.logger.error('Error during execution of "{0}" obfuscator: {1}'.format(self.__class__.__name__, e))
            raise

        finally:
            obfuscation_info.used_obfuscators.append(self.__class__.__name__)
