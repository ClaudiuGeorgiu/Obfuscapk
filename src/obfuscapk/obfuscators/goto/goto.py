#!/usr/bin/env python3

import logging

from obfuscapk import obfuscator_category
from obfuscapk import util
from obfuscapk.obfuscation import Obfuscation


class Goto(obfuscator_category.ICodeObfuscator):
    def __init__(self):
        self.logger = logging.getLogger(
            "{0}.{1}".format(__name__, self.__class__.__name__)
        )
        super().__init__()

    def obfuscate(self, obfuscation_info: Obfuscation):
        self.logger.info('Running "{0}" obfuscator'.format(self.__class__.__name__))

        try:
            for smali_file in util.show_list_progress(
                obfuscation_info.get_smali_files(),
                interactive=obfuscation_info.interactive,
                description='Inserting "goto" instructions in smali files',
            ):
                self.logger.debug(
                    'Inserting "goto" instructions in file "{0}"'.format(smali_file)
                )
                with util.inplace_edit_file(smali_file) as (in_file, out_file):
                    editing_method = False
                    for line in in_file:
                        if (
                            line.startswith(".method ")
                            and " abstract " not in line
                            and " native " not in line
                            and not editing_method
                        ):
                            # If at the beginning of a non abstract/native method
                            # (after the .locals instruction), insert a "goto" to the
                            # label at the end of the method and a label to the first
                            # instruction of the method.
                            out_file.write(line)
                            editing_method = True

                        elif editing_method and util.locals_pattern.match(line):
                            out_file.write(line)
                            out_file.write("\n\tgoto/32 :after_last_instruction\n\n")
                            out_file.write("\t:before_first_instruction\n")

                        elif line.startswith(".end method") and editing_method:
                            # If at the end of the method, insert a label after the
                            # last instruction of the method and a "goto" to the label
                            # at the beginning of the method. This will not cause an
                            # endless loop because the method will return at some point
                            # and the second "goto" won't be called again when the
                            # method finishes.
                            out_file.write("\n\t:after_last_instruction\n\n")
                            out_file.write("\tgoto/32 :before_first_instruction\n\n")
                            out_file.write(line)
                            editing_method = False

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
