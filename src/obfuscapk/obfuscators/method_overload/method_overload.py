#!/usr/bin/env python3.7

import logging
import random
from typing import List, Set

from obfuscapk import obfuscator_category
from obfuscapk import util
from obfuscapk.obfuscation import Obfuscation


class MethodOverload(obfuscator_category.ICodeObfuscator):

    def __init__(self):
        self.logger = logging.getLogger('{0}.{1}'.format(__name__, self.__class__.__name__))
        super().__init__()

        self.is_adding_methods = True

        self.param_types = ['Ljava/lang/String;', 'Z', 'B', 'S', 'C', 'I', 'F']

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
                        # If this is a class to ignore, get its methods and add them to the list of methods to be
                        # ignored when performing method overloading.
                        class_match = util.class_pattern.match(line)
                        if class_match:
                            class_name = class_match.group('class_name')
                            if class_name not in class_names_to_ignore:
                                # The methods of this class shouldn't be ignored when performing method overloading,
                                # so proceed with the next class.
                                break
                            else:
                                continue

                    # Skip virtual methods, consider only the direct methods defined earlier in the file.
                    if line.startswith('# virtual methods'):
                        break

                    # Method declared in class.
                    method_match = util.method_pattern.match(line)

                    # Avoid constructors, native and abstract methods (these will be avoided also when performing
                    # method overloading).
                    if method_match and '<init>' not in line and '<clinit>' not in line and \
                            ' native ' not in line and ' abstract ' not in line:
                        method = '{method_name}({method_param}){method_return}'.format(
                            method_name=method_match.group('method_name'),
                            method_param=method_match.group('method_param'),
                            method_return=method_match.group('method_return')
                        )
                        methods_to_ignore.add(method)

        return methods_to_ignore

    def add_method_overloads_to_file(self, smali_file: str, overloaded_method_body: str,
                                     methods_to_ignore: Set[str]) -> int:
        new_methods_num: int = 0
        with util.inplace_edit_file(smali_file) as current_file:

            skip_remaining_lines = False
            class_name = None
            for line in current_file:

                if skip_remaining_lines:
                    print(line, end='')
                    continue

                if not class_name:
                    class_match = util.class_pattern.match(line)
                    # If this is an enum class, skip it.
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
                    # Add method overload.
                    if method not in methods_to_ignore:
                        # Create random parameter lists to be added to the method signature.
                        # Add 3 overloads for each method and for each overload use 4 random params.
                        for params in util.get_random_list_permutations(random.sample(self.param_types, 4))[:3]:
                            new_param = ''.join(params)
                            # Update parameter list and add void return type.
                            overloaded_signature = line.replace(
                                '({0}){1}'.format(method_match.group('method_param'),
                                                  method_match.group('method_return')),
                                '({0}{1})V'.format(method_match.group('method_param'), new_param)
                            )
                            print(overloaded_signature, end='')
                            print(overloaded_method_body)
                            new_methods_num += 1

                        # Print original method.
                        print(line, end='')
                    else:
                        print(line, end='')
                else:
                    print(line, end='')

        return new_methods_num

    def add_method_overloads(self, smali_files: List[str], methods_to_ignore: Set[str],
                             max_methods_to_add: int, interactive: bool = False):

        overloaded_method_body = util.get_smali_method_overload()
        added_methods = 0

        for smali_file in util.show_list_progress(smali_files,
                                                  interactive=interactive,
                                                  description='Inserting method overloads in smali files'):
            self.logger.debug('Inserting method overloads in file "{0}"'.format(smali_file))
            if added_methods < max_methods_to_add:
                added_methods += self.add_method_overloads_to_file(smali_file, overloaded_method_body,
                                                                   methods_to_ignore)
            else:
                break

        self.logger.debug('{0} new overloaded methods were added'.format(added_methods))

    def obfuscate(self, obfuscation_info: Obfuscation):
        self.logger.info('Running "{0}" obfuscator'.format(self.__class__.__name__))

        try:
            android_class_names: Set[str] = set(util.get_android_class_names())
            parent_class_names: Set[str] = self.get_parent_class_names(obfuscation_info.get_smali_files())

            # Methods in parent classes belonging to the Android framework should be ignored.
            classes_to_ignore: Set[str] = parent_class_names.intersection(android_class_names)
            methods_to_ignore: Set[str] = self.get_methods_to_ignore(obfuscation_info.get_smali_files(),
                                                                     classes_to_ignore)

            # There is a method limit for dex files.
            max_methods_to_add = obfuscation_info.get_remaining_methods_per_obfuscator()

            if obfuscation_info.is_multidex():
                for index, dex_smali_files in enumerate(
                        util.show_list_progress(obfuscation_info.get_multidex_smali_files(),
                                                interactive=obfuscation_info.interactive, unit='dex',
                                                description='Processing multidex')):
                    max_methods_to_add = obfuscation_info.get_remaining_methods_per_obfuscator()[index]
                    self.add_method_overloads(dex_smali_files, methods_to_ignore, max_methods_to_add,
                                              obfuscation_info.interactive)
            else:
                self.add_method_overloads(obfuscation_info.get_smali_files(), methods_to_ignore, max_methods_to_add,
                                          obfuscation_info.interactive)

        except Exception as e:
            self.logger.error('Error during execution of "{0}" obfuscator: {1}'.format(self.__class__.__name__, e))
            raise

        finally:
            obfuscation_info.used_obfuscators.append(self.__class__.__name__)
