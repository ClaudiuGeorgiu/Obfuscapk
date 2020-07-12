#!/usr/bin/env python3

import logging
import random
import re
from typing import List

from obfuscapk import obfuscator_category
from obfuscapk import util
from obfuscapk.obfuscation import Obfuscation


class CodeBlock:
    def __init__(self, jump_id=0, smali_code=""):
        self.jump_id = jump_id
        self.smali_code = smali_code

    def add_smali_code_to_block(self, smali_code):
        self.smali_code += smali_code


class Reorder(obfuscator_category.ICodeObfuscator):
    def __init__(self):
        self.logger = logging.getLogger(
            "{0}.{1}".format(__name__, self.__class__.__name__)
        )
        super().__init__()

        self.if_mapping = {
            "if-eq": "if-ne",
            "if-ne": "if-eq",
            "if-lt": "if-ge",
            "if-ge": "if-lt",
            "if-gt": "if-le",
            "if-le": "if-gt",
            "if-eqz": "if-nez",
            "if-nez": "if-eqz",
            "if-ltz": "if-gez",
            "if-gez": "if-ltz",
            "if-gtz": "if-lez",
            "if-lez": "if-gtz",
        }

    def obfuscate(self, obfuscation_info: Obfuscation):
        self.logger.info('Running "{0}" obfuscator'.format(self.__class__.__name__))

        try:
            op_codes = util.get_code_block_valid_op_codes()
            op_code_pattern = re.compile(r"\s+(?P<op_code>\S+)")
            if_pattern = re.compile(
                r"\s+(?P<if_op_code>\S+)"
                r"\s(?P<register>[vp0-9,\s]+?),\s:(?P<goto_label>\S+)"
            )

            for smali_file in util.show_list_progress(
                obfuscation_info.get_smali_files(),
                interactive=obfuscation_info.interactive,
                description="Code reordering",
            ):
                self.logger.debug('Reordering code in file "{0}"'.format(smali_file))
                with util.inplace_edit_file(smali_file) as (in_file, out_file):
                    editing_method = False
                    inside_try_catch = False
                    jump_count = 0
                    for line in in_file:
                        if (
                            line.startswith(".method ")
                            and " abstract " not in line
                            and " native " not in line
                            and not editing_method
                        ):
                            # If at the beginning of a non abstract/native method
                            out_file.write(line)
                            editing_method = True
                            inside_try_catch = False
                            jump_count = 0

                        elif line.startswith(".end method") and editing_method:
                            # If a the end of the method.
                            out_file.write(line)
                            editing_method = False
                            inside_try_catch = False

                        elif editing_method:
                            # Inside method. Check if this line contains an op code at
                            # the beginning of the string.
                            match = op_code_pattern.match(line)
                            if match:
                                op_code = match.group("op_code")

                                # Check if we are entering or leaving a try-catch
                                # block of code.
                                if op_code.startswith(":try_start_"):
                                    out_file.write(line)
                                    inside_try_catch = True
                                elif op_code.startswith(":try_end_"):
                                    out_file.write(line)
                                    inside_try_catch = False

                                # If this is a valid op code, and we are not inside a
                                # try-catch block, mark this section with a special
                                # label that will be used later and invert the if
                                # conditions (if any).
                                elif op_code in op_codes and not inside_try_catch:
                                    jump_name = util.get_random_string(16)
                                    out_file.write(
                                        "\tgoto/32 :l_{label}_{count}\n\n".format(
                                            label=jump_name, count=jump_count
                                        )
                                    )
                                    out_file.write("\tnop\n\n")
                                    out_file.write("#!code_block!#\n")
                                    out_file.write(
                                        "\t:l_{label}_{count}\n".format(
                                            label=jump_name, count=jump_count
                                        )
                                    )
                                    jump_count += 1

                                    new_if = self.if_mapping.get(op_code, None)
                                    if new_if:
                                        if_match = if_pattern.match(line)
                                        random_label_name = util.get_random_string(16)
                                        out_file.write(
                                            "\t{if_cond} {register}, "
                                            ":gl_{new_label}\n\n".format(
                                                if_cond=new_if,
                                                register=if_match.group("register"),
                                                new_label=random_label_name,
                                            )
                                        )
                                        out_file.write(
                                            "\tgoto/32 :{0}\n\n".format(
                                                if_match.group("goto_label")
                                            )
                                        )
                                        out_file.write(
                                            "\t:gl_{0}".format(random_label_name)
                                        )
                                    else:
                                        out_file.write(line)
                                else:
                                    out_file.write(line)
                            else:
                                out_file.write(line)

                        else:
                            out_file.write(line)

                # Reorder code blocks randomly.
                with util.inplace_edit_file(smali_file) as (in_file, out_file):
                    editing_method = False
                    block_count = 0
                    code_blocks: List[CodeBlock] = []
                    current_code_block = None
                    for line in in_file:
                        if (
                            line.startswith(".method ")
                            and " abstract " not in line
                            and " native " not in line
                            and not editing_method
                        ):
                            # If at the beginning of a non abstract/native method
                            out_file.write(line)
                            editing_method = True
                            block_count = 0
                            code_blocks = []
                            current_code_block = None

                        elif line.startswith(".end method") and editing_method:
                            # If a the end of the method.
                            editing_method = False
                            random.shuffle(code_blocks)
                            for code_block in code_blocks:
                                out_file.write(code_block.smali_code)
                            out_file.write(line)

                        elif editing_method:
                            # Inside method. Check if this line is marked with
                            # a special label.
                            if line.startswith("#!code_block!#"):
                                block_count += 1
                                current_code_block = CodeBlock(block_count, "")
                                code_blocks.append(current_code_block)
                            else:
                                if block_count > 0 and current_code_block:
                                    current_code_block.add_smali_code_to_block(line)
                                else:
                                    out_file.write(line)

                        else:
                            out_file.write(line)

        except Exception as e:
            self.logger.error(
                'Error during execution of "{0}" obfuscator: {1}'.format(
                    self.__class__.__name__, e
                )
            )
            raise

        finally:
            obfuscation_info.used_obfuscators.append(self.__class__.__name__)
