#!/usr/bin/env python3.7

import logging

from obfuscapk import obfuscator_category
from obfuscapk import util
from obfuscapk.obfuscation import Obfuscation


class ArithmeticBranch(obfuscator_category.ICodeObfuscator):

    def __init__(self):
        self.logger = logging.getLogger('{0}.{1}'.format(__name__, self.__class__.__name__))
        super().__init__()

    def obfuscate(self, obfuscation_info: Obfuscation):
        self.logger.info('Running "{0}" obfuscator'.format(self.__class__.__name__))

        try:
            for smali_file in util.show_list_progress(obfuscation_info.get_smali_files(),
                                                      interactive=obfuscation_info.interactive,
                                                      description='Inserting arithmetic computations in smali files'):
                self.logger.debug('Inserting arithmetic computations in file "{0}"'.format(smali_file))
                with util.inplace_edit_file(smali_file) as current_file:
                    editing_method = False
                    start_label = None
                    end_label = None
                    for line in current_file:
                        if line.startswith('.method ') and ' abstract ' not in line and \
                                ' native ' not in line and not editing_method:
                            # Entering method.
                            print(line, end='')
                            editing_method = True

                        elif line.startswith('.end method') and editing_method:
                            # Exiting method.
                            if start_label and end_label:
                                print('\t:{0}'.format(end_label))
                                print('\tgoto/32 :{0}'.format(start_label))
                                start_label = None
                                end_label = None
                            print(line, end='')
                            editing_method = False

                        elif editing_method:
                            # Inside method.
                            print(line, end='')
                            match = util.locals_pattern.match(line)
                            if match and int(match.group('local_count')) >= 2:
                                # If there are at least 2 registers available, add a fake branch at the beginning of
                                # the method: one branch will continue from here, the other branch will go to the end
                                # of the method and then will return here through a "goto" instruction.
                                v0, v1 = util.get_random_int(1, 32), util.get_random_int(1, 32)
                                start_label = util.get_random_string(16)
                                end_label = util.get_random_string(16)
                                tmp_label = util.get_random_string(16)
                                print('\n\tconst v0, {0}'.format(v0))
                                print('\tconst v1, {0}'.format(v1))
                                print('\tadd-int v0, v0, v1')
                                print('\trem-int v0, v0, v1')
                                print('\tif-gtz v0, :{0}'.format(tmp_label))
                                print('\tgoto/32 :{0}'.format(end_label))
                                print('\t:{0}'.format(tmp_label))
                                print('\t:{0}'.format(start_label))

                        else:
                            print(line, end='')

        except Exception as e:
            self.logger.error('Error during execution of "{0}" obfuscator: {1}'.format(self.__class__.__name__, e))
            raise

        finally:
            obfuscation_info.used_obfuscators.append(self.__class__.__name__)
