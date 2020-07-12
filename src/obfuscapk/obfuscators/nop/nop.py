#!/usr/bin/env python3

import logging
import re

from obfuscapk import obfuscator_category
from obfuscapk import util
from obfuscapk.obfuscation import Obfuscation


class Nop(obfuscator_category.ICodeObfuscator):
    def __init__(self):
        self.logger = logging.getLogger(
            "{0}.{1}".format(__name__, self.__class__.__name__)
        )
        super().__init__()

    def obfuscate(self, obfuscation_info: Obfuscation):
        self.logger.info('Running "{0}" obfuscator'.format(self.__class__.__name__))

        try:
            op_codes = util.get_nop_valid_op_codes()
            pattern = re.compile(r"\s+(?P<op_code>\S+)")

            for smali_file in util.show_list_progress(
                obfuscation_info.get_smali_files(),
                interactive=obfuscation_info.interactive,
                description='Inserting "nop" instructions in smali files',
            ):
                self.logger.debug(
                    'Inserting "nop" instructions in file "{0}"'.format(smali_file)
                )
                with util.inplace_edit_file(smali_file) as (in_file, out_file):
                    for line in in_file:

                        # Print original instruction.
                        out_file.write(line)

                        # Check if this line contains an op code at the beginning
                        # of the string.
                        match = pattern.match(line)
                        if match:
                            op_code = match.group("op_code")
                            # If this is a valid op code, insert some nop instructions
                            # after it.
                            if op_code in op_codes:
                                nop_count = util.get_random_int(1, 5)
                                out_file.write("\tnop\n" * nop_count)

        except Exception as e:
            self.logger.error(
                'Error during execution of "{0}" obfuscator: {1}'.format(
                    self.__class__.__name__, e
                )
            )
            raise

        finally:
            obfuscation_info.used_obfuscators.append(self.__class__.__name__)
