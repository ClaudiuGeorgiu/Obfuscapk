#!/usr/bin/env python3

import logging
import random
from typing import List, Set

from obfuscapk import obfuscator_category
from obfuscapk import util
from obfuscapk.obfuscation import Obfuscation


class MethodOverload(obfuscator_category.ICodeObfuscator):
    def __init__(self):
        self.logger = logging.getLogger(
            "{0}.{1}".format(__name__, self.__class__.__name__)
        )
        super().__init__()

        self.is_adding_methods = True

        self.param_types = ["Ljava/lang/String;", "Z", "B", "S", "C", "I", "F"]

    def add_method_overloads_to_file(
        self,
        smali_file: str,
        overloaded_method_body: str,
        class_names_to_ignore: Set[str],
    ) -> int:
        new_methods_num: int = 0
        with util.inplace_edit_file(smali_file) as (in_file, out_file):

            skip_remaining_lines = False
            class_name = None
            for line in in_file:

                if skip_remaining_lines:
                    out_file.write(line)
                    continue

                if not class_name:
                    class_match = util.class_pattern.match(line)
                    # If this is an enum class, skip it.
                    if " enum " in line:
                        skip_remaining_lines = True
                        out_file.write(line)
                        continue
                    elif class_match:
                        class_name = class_match.group("class_name")
                        if class_name in class_names_to_ignore:
                            # The methods of this class should be ignored when
                            # renaming, so proceed with the next class.
                            skip_remaining_lines = True
                        out_file.write(line)
                        continue

                # Skip virtual methods, consider only the direct methods defined
                # earlier in the file.
                if line.startswith("# virtual methods"):
                    skip_remaining_lines = True
                    out_file.write(line)
                    continue

                # Method declared in class.
                method_match = util.method_pattern.match(line)

                # Avoid constructors, native and abstract methods.
                if (
                    method_match
                    and "<init>" not in line
                    and "<clinit>" not in line
                    and " native " not in line
                    and " abstract " not in line
                ):
                    # Create lists with random parameters to be added to the method
                    # signature. Add 3 overloads for each method and for each overload
                    # use 4 random params.
                    for params in util.get_random_list_permutations(
                        random.sample(self.param_types, 4)
                    )[:3]:
                        new_param = "".join(params)
                        # Update parameter list and add void return type.
                        overloaded_signature = line.replace(
                            "({0}){1}".format(
                                method_match.group("method_param"),
                                method_match.group("method_return"),
                            ),
                            "({0}{1})V".format(
                                method_match.group("method_param"), new_param
                            ),
                        )
                        out_file.write(overloaded_signature)
                        out_file.write(overloaded_method_body)
                        new_methods_num += 1

                    # Print original method.
                    out_file.write(line)
                else:
                    out_file.write(line)

        return new_methods_num

    def add_method_overloads(
        self,
        smali_files: List[str],
        class_names_to_ignore: Set[str],
        max_methods_to_add: int,
        interactive: bool = False,
    ):

        overloaded_method_body = util.get_smali_method_overload()
        added_methods = 0

        for smali_file in util.show_list_progress(
            smali_files,
            interactive=interactive,
            description="Inserting method overloads in smali files",
        ):
            self.logger.debug(
                'Inserting method overloads in file "{0}"'.format(smali_file)
            )
            if added_methods < max_methods_to_add:
                added_methods += self.add_method_overloads_to_file(
                    smali_file, overloaded_method_body, class_names_to_ignore
                )
            else:
                break

        self.logger.debug("{0} new overloaded methods were added".format(added_methods))

    def obfuscate(self, obfuscation_info: Obfuscation):
        self.logger.info('Running "{0}" obfuscator'.format(self.__class__.__name__))

        try:
            # NOTE: only direct methods (methods that are by nature non-overridable,
            # namely private instance methods, constructors and static methods) will be
            # overloaded.

            android_class_names: Set[str] = set(util.get_android_class_names())

            # There is a method limit for dex files.
            max_methods_to_add = obfuscation_info.get_remaining_methods_per_obfuscator()

            if obfuscation_info.is_multidex():
                for index, dex_smali_files in enumerate(
                    util.show_list_progress(
                        obfuscation_info.get_multidex_smali_files(),
                        interactive=obfuscation_info.interactive,
                        unit="dex",
                        description="Processing multidex",
                    )
                ):
                    max_methods_to_add = (
                        obfuscation_info.get_remaining_methods_per_obfuscator()[index]
                    )
                    self.add_method_overloads(
                        dex_smali_files,
                        android_class_names,
                        max_methods_to_add,
                        obfuscation_info.interactive,
                    )
            else:
                self.add_method_overloads(
                    obfuscation_info.get_smali_files(),
                    android_class_names,
                    max_methods_to_add,
                    obfuscation_info.interactive,
                )

        except Exception as e:
            self.logger.error(
                'Error during execution of "{0}" obfuscator: {1}'.format(
                    self.__class__.__name__, e
                )
            )
            raise

        finally:
            obfuscation_info.used_obfuscators.append(self.__class__.__name__)
