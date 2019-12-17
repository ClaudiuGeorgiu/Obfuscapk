#!/usr/bin/env python3.7

import logging
from typing import List, Set

from obfuscapk import obfuscator_category
from obfuscapk import util
from obfuscapk.obfuscation import Obfuscation


class MethodRename(obfuscator_category.IRenameObfuscator):

    def __init__(self):
        self.logger = logging.getLogger('{0}.{1}'.format(__name__, self.__class__.__name__))
        super().__init__()

    def rename_method(self, method_name: str) -> str:
        method_md5 = util.get_string_md5(method_name)
        return 'm{0}'.format(method_md5.lower()[:8])

    def get_parent_class_names(self, smali_files: List[str]) -> Set[str]:
        class_names: Set[str] = set()
        for smali_file in smali_files:
            with open(smali_file, 'r', encoding='utf-8') as current_file:
                for line in current_file:
                    super_class_match = util.super_class_pattern.match(line)
                    if super_class_match:
                        class_names.add(super_class_match.group('class_name'))
                        break

        if 'Ljava/lang/Object;' in class_names:
            class_names.remove('Ljava/lang/Object;')

        return class_names

    def get_methods_to_ignore(self, smali_files: List[str], class_names_to_ignore: Set[str]) -> Set[str]:
        methods_to_ignore: Set[str] = set()
        for smali_file in smali_files:
            with open(smali_file, 'r', encoding='utf-8') as current_file:
                class_name = None
                for line in current_file:

                    if not class_name:
                        # Every smali file contains a class, so check if this class belongs to the classes to ignore.
                        # If this is a class to ignore (when renaming), get its methods and add them to the list of
                        # methods to be ignored when performing renaming.
                        class_match = util.class_pattern.match(line)
                        if class_match:
                            class_name = class_match.group('class_name')
                            if class_name not in class_names_to_ignore:
                                # The methods of this class shouldn't be ignored when renaming,
                                # so proceed with the next class.
                                break
                            else:
                                continue

                    # Skip virtual methods, consider only the direct methods defined earlier in the file.
                    if line.startswith('# virtual methods'):
                        break

                    # Method declared in class.
                    method_match = util.method_pattern.match(line)

                    # Avoid constructors, native and abstract methods (these will be avoided also when renaming).
                    if method_match and '<init>' not in line and '<clinit>' not in line and \
                            ' native ' not in line and ' abstract ' not in line:
                        method = '{method_name}({method_param}){method_return}'.format(
                            method_name=method_match.group('method_name'),
                            method_param=method_match.group('method_param'),
                            method_return=method_match.group('method_return')
                        )
                        methods_to_ignore.add(method)

        return methods_to_ignore

    def rename_method_declarations(self, smali_files: List[str], methods_to_ignore: Set[str],
                                   interactive: bool = False) -> Set[str]:
        renamed_methods: Set[str] = set()

        # Search for method definitions that can be renamed.
        for smali_file in util.show_list_progress(smali_files,
                                                  interactive=interactive,
                                                  description='Renaming method declarations'):
            with util.inplace_edit_file(smali_file) as current_file:

                skip_remaining_lines = False
                class_name = None
                for line in current_file:

                    if skip_remaining_lines:
                        print(line, end='')
                        continue

                    if not class_name:
                        class_match = util.class_pattern.match(line)
                        # If this is an enum class, don't rename anything.
                        if ' enum ' in line:
                            skip_remaining_lines = True
                            print(line, end='')
                            continue
                        elif class_match:
                            class_name = class_match.group('class_name')
                            print(line, end='')
                            continue

                    # Skip virtual methods, consider only the direct methods defined earlier in the file.
                    if line.startswith('# virtual methods'):
                        skip_remaining_lines = True
                        print(line, end='')
                        continue

                    # Method declared in class.
                    method_match = util.method_pattern.match(line)

                    # Avoid constructors, native and abstract methods.
                    if method_match and '<init>' not in line and '<clinit>' not in line and \
                            ' native ' not in line and ' abstract ' not in line:
                        method = '{method_name}({method_param}){method_return}'.format(
                            method_name=method_match.group('method_name'),
                            method_param=method_match.group('method_param'),
                            method_return=method_match.group('method_return')
                        )
                        if method not in methods_to_ignore:
                            # Rename method declaration (invocations of this method will be renamed later).
                            method_name = method_match.group('method_name')
                            print(line.replace(
                                '{0}('.format(method_name),
                                '{0}('.format(self.rename_method(method_name))
                            ), end='')
                            renamed_methods.add(method)
                        else:
                            print(line, end='')
                    else:
                        print(line, end='')

        return renamed_methods

    def rename_method_invocations(self, smali_files: List[str], methods_to_rename: Set[str],
                                  android_class_names: Set[str], interactive: bool = False):
        for smali_file in util.show_list_progress(smali_files,
                                                  interactive=interactive,
                                                  description='Renaming method invocations'):
            with util.inplace_edit_file(smali_file) as current_file:
                for line in current_file:
                    # Method invocation.
                    invoke_match = util.invoke_pattern.match(line)
                    if invoke_match:
                        method = '{method_name}({method_param}){method_return}'.format(
                            method_name=invoke_match.group('invoke_method'),
                            method_param=invoke_match.group('invoke_param'),
                            method_return=invoke_match.group('invoke_return')
                        )
                        invoke_type = invoke_match.group('invoke_type')
                        class_name = invoke_match.group('invoke_object')
                        # Rename the method invocation only if is direct or static (we are renaming only direct methods)
                        # and if is called from a class that is not an Android API class.
                        if ('direct' in invoke_type or 'static' in invoke_type) and method in methods_to_rename and \
                                class_name not in android_class_names:
                            method_name = invoke_match.group('invoke_method')
                            print(line.replace(
                                '{0}('.format(method_name),
                                '{0}('.format(self.rename_method(method_name))
                            ), end='')
                        else:
                            print(line, end='')
                    else:
                        print(line, end='')

    def obfuscate(self, obfuscation_info: Obfuscation):
        self.logger.info('Running "{0}" obfuscator'.format(self.__class__.__name__))

        try:
            android_class_names: Set[str] = set(util.get_android_class_names())
            parent_class_names: Set[str] = self.get_parent_class_names(obfuscation_info.get_smali_files())

            # Methods in parent classes belonging to the Android framework should be ignored when renaming.
            classes_to_ignore: Set[str] = parent_class_names.intersection(android_class_names)
            methods_to_ignore: Set[str] = self.get_methods_to_ignore(obfuscation_info.get_smali_files(),
                                                                     classes_to_ignore)

            renamed_methods: Set[str] = self.rename_method_declarations(obfuscation_info.get_smali_files(),
                                                                        methods_to_ignore, obfuscation_info.interactive)

            self.rename_method_invocations(obfuscation_info.get_smali_files(), renamed_methods, android_class_names,
                                           obfuscation_info.interactive)

        except Exception as e:
            self.logger.error('Error during execution of "{0}" obfuscator: {1}'.format(self.__class__.__name__, e))
            raise

        finally:
            obfuscation_info.used_obfuscators.append(self.__class__.__name__)
