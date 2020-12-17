#!/usr/bin/env python3

import logging
from typing import List, Set

from obfuscapk import obfuscator_category
from obfuscapk import util
from obfuscapk.obfuscation import Obfuscation


class MethodRename(obfuscator_category.IRenameObfuscator):
    def __init__(self):
        self.logger = logging.getLogger(
            "{0}.{1}".format(__name__, self.__class__.__name__)
        )
        super().__init__()

        self.ignore_package_names = []

    def rename_method(self, method_name: str) -> str:
        method_md5 = util.get_string_md5(method_name)
        return "m{0}".format(method_md5.lower()[:8])

    def rename_method_declarations(
        self,
        smali_files: List[str],
        class_names_to_ignore: Set[str],
        interactive: bool = False,
    ) -> Set[str]:
        renamed_methods: Set[str] = set()

        # Search for method definitions that can be renamed.
        for smali_file in util.show_list_progress(
            smali_files,
            interactive=interactive,
            description="Renaming method declarations",
        ):
            with util.inplace_edit_file(smali_file) as (in_file, out_file):

                skip_remaining_lines = False
                class_name = None
                for line in in_file:

                    if skip_remaining_lines:
                        out_file.write(line)
                        continue

                    if not class_name:
                        class_match = util.class_pattern.match(line)
                        # If this is an enum class, don't rename anything.
                        if " enum " in line:
                            skip_remaining_lines = True
                            out_file.write(line)
                            continue
                        elif class_match:
                            class_name = class_match.group("class_name")
                            if (
                                class_name in class_names_to_ignore
                                or class_name.startswith(
                                    tuple(self.ignore_package_names)
                                )
                            ):
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
                        method = "{method_name}({method_param}){method_return}".format(
                            method_name=method_match.group("method_name"),
                            method_param=method_match.group("method_param"),
                            method_return=method_match.group("method_return"),
                        )
                        # Rename method declaration (invocations of this method will be
                        # renamed later).
                        method_name = method_match.group("method_name")
                        out_file.write(
                            line.replace(
                                "{0}(".format(method_name),
                                "{0}(".format(self.rename_method(method_name)),
                            )
                        )
                        # Direct methods cannot be overridden, so they can be called
                        # only by the same class that declares them.
                        renamed_methods.add(
                            "{class_name}->{method}".format(
                                class_name=class_name, method=method
                            )
                        )
                    else:
                        out_file.write(line)

        return renamed_methods

    def rename_method_invocations(
        self,
        smali_files: List[str],
        methods_to_rename: Set[str],
        interactive: bool = False,
    ):
        for smali_file in util.show_list_progress(
            smali_files,
            interactive=interactive,
            description="Renaming method invocations",
        ):
            with util.inplace_edit_file(smali_file) as (in_file, out_file):
                for line in in_file:
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
                        invoke_type = invoke_match.group("invoke_type")
                        # Rename the method invocation only if is direct or static (we
                        # are renaming only direct methods). The list of methods to
                        # rename already contains the class name of each method, since
                        # here we have a list of methods whose declarations were already
                        # renamed.
                        if (
                            "direct" in invoke_type or "static" in invoke_type
                        ) and method in methods_to_rename:
                            method_name = invoke_match.group("invoke_method")
                            out_file.write(
                                line.replace(
                                    "->{0}(".format(method_name),
                                    "->{0}(".format(self.rename_method(method_name)),
                                )
                            )
                        else:
                            out_file.write(line)
                    else:
                        out_file.write(line)

    def obfuscate(self, obfuscation_info: Obfuscation):
        self.logger.info('Running "{0}" obfuscator'.format(self.__class__.__name__))

        # Get user defined ignore package list.
        self.ignore_package_names = obfuscation_info.get_ignore_package_names()

        try:
            # NOTE: only direct methods (methods that are by nature non-overridable,
            # namely private instance methods, constructors and static methods) will be
            # renamed.

            android_class_names: Set[str] = set(util.get_android_class_names())

            renamed_methods: Set[str] = self.rename_method_declarations(
                obfuscation_info.get_smali_files(),
                android_class_names,
                obfuscation_info.interactive,
            )

            self.rename_method_invocations(
                obfuscation_info.get_smali_files(),
                renamed_methods,
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
