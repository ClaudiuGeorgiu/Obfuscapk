#!/usr/bin/env python3

import logging

from obfuscapk import obfuscator_category
from obfuscapk import util
from obfuscapk.obfuscation import Obfuscation


class ArithmeticBranch(obfuscator_category.ICodeObfuscator):
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
                description="Inserting arithmetic computations in smali files",
            ):
                self.logger.debug(
                    'Inserting arithmetic computations in file "{0}"'.format(smali_file)
                )
                with util.inplace_edit_file(smali_file) as (in_file, out_file):
                    editing_method = False
                    start_label = None
                    end_label = None
                    for line in in_file:
                        if (
                            line.startswith(".method ")
                            and " abstract " not in line
                            and " native " not in line
                            and not editing_method
                        ):
                            # Entering method.
                            out_file.write(line)
                            editing_method = True

                        elif line.startswith(".end method") and editing_method:
                            # Exiting method.
                            if start_label and end_label:
                                out_file.write("\t:{0}\n".format(end_label))
                                out_file.write("\tgoto/32 :{0}\n".format(start_label))
                                start_label = None
                                end_label = None
                            out_file.write(line)
                            editing_method = False

                        elif editing_method:
                            # Inside method.
                            out_file.write(line)
                            match = util.locals_pattern.match(line)
                            if match and int(match.group("local_count")) >= 2:
                                # If there are at least 2 registers available, add a
                                # fake branch at the beginning of the method: one branch
                                # will continue from here, the other branch will go to
                                # the end of the method and then will return here
                                # through a "goto" instruction.
                                v0, v1 = (
                                    util.get_random_int(1, 32),
                                    util.get_random_int(1, 32),
                                )
                                start_label = util.get_random_string(16)
                                end_label = util.get_random_string(16)
                                tmp_label = util.get_random_string(16)
                                out_file.write("\n\tconst v0, {0}\n".format(v0))
                                out_file.write("\tconst v1, {0}\n".format(v1))
                                out_file.write("\tadd-int v0, v0, v1\n")
                                out_file.write("\trem-int v0, v0, v1\n")
                                out_file.write("\tif-gtz v0, :{0}\n".format(tmp_label))
                                out_file.write("\tgoto/32 :{0}\n".format(end_label))
                                out_file.write("\t:{0}\n".format(tmp_label))
                                out_file.write("\t:{0}\n".format(start_label))

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
